from __future__ import absolute_import

import argparse
import logging
import os
import regex

import anafora
import anafora.validate

def fix_thyme_errors(schema, input_dir, output_dir, xml_name_regex="[.]xml$"):
    """
    :param schema anafora.validate.Schema: the THYME schema
    :param input_dir str: the root of a set of THYME Anafora XML directories
    :param output_dir str: the directory where the cleaned versions of the THYME Anafora XML files should be written.
        The directory structure will mirror the input directory structure.
    """
    for sub_dir, text_name, xml_names in anafora.walk(input_dir, xml_name_regex):
        for xml_name in xml_names:
            xml_path = os.path.join(input_dir, sub_dir, xml_name)

            # load the data from the Anafora XML
            try:
                data = anafora.AnaforaData.from_file(xml_path)
            except anafora.ElementTree.ParseError as e:
                logging.warning("SKIPPING invalid XML: %s: %s", e, xml_path)
                continue

            # remove invalid TLINKs and ALINKs
            changed = False
            to_remove = []
            for annotation in data.annotations:
                try:
                    schema.validate(annotation)
                except anafora.validate.SchemaValidationError as e:
                    if annotation.type in {"TLINK", "ALINK"}:
                        logging.warning("REMOVING %s: %s", e, annotation)
                        to_remove.append(annotation)
            for annotation in to_remove:
                data.annotations.remove(annotation)
                changed = True

            # remove TIMEX3s that are directly on top of SECTIONTIMEs and DOCTIMEs
            for span, annotations in anafora.validate.find_entities_with_identical_spans(data):
                try:
                    # sorts SECTIONTIME and DOCTIME before TIMEX3
                    special_time, timex = sorted(annotations, key=lambda a: a.type)
                except ValueError:
                    pass
                else:
                    if special_time.type in {"SECTIONTIME", "DOCTIME"} and timex.type == "TIMEX3":
                        msg = "REPLACING multiple entities for span %s: %s WITH %s"
                        logging.warning(msg, span, timex, special_time)
                        for annotation in data.annotations:
                            for name, value in annotation.properties.items():
                                if value is timex:
                                    annotation.properties[name] = special_time
                        data.annotations.remove(timex)
                        changed = True

            # if we found and fixed any errors, write out the new XML file
            if changed:
                output_sub_dir = os.path.join(output_dir, sub_dir)
                if not os.path.exists(output_sub_dir):
                    os.makedirs(output_sub_dir)
                output_path = os.path.join(output_sub_dir, xml_name)
                data.to_file(output_path)


def convert_thyme_qa_to_anafora_xml(input_dir, output_dir):
    _header_sep_pattern = regex.compile(r'\s*=====+\s*')
    _annotation_sep_pattern = regex.compile(r'\s*-----+\s*')
    _annotation_pattern = regex.compile(r'^Question:(.*?)\nAnswer:(.*?)\nConfidence:(.*?)\n' +
                                        r'Difficulty:(.*?)\nDocTimeRel:(.*?)\n(Text Clip:.*)$', regex.DOTALL)
    _text_clip_pattern = regex.compile(r'Text Clip:\s+\d[\w.]*\s+(\d+),(\d+) (Exact|Support)_Answer ' +
                                       r'Use_(Time_Span|DocTimeRel) ?(.*)\n(.*)(?:\n|$)')

    # iterate through all _qa.txt files in the input directory
    for input_root, dir_names, input_file_names in os.walk(input_dir):
        for input_file_name in input_file_names:
            if input_file_name.endswith("_qa.txt"):
                file_base = input_file_name[:-7]

                # create one Anafora XML for each file
                data = anafora.AnaforaData()
                relation_count = 1
                entity_count = 1
                with open(os.path.join(input_root, input_file_name)) as input_file:
                    text = input_file.read().decode('ascii')

                    # parse the annotations from the THYME question-answer format
                    _, body_text = _header_sep_pattern.split(text)
                    for annotation_text in _annotation_sep_pattern.split(body_text.rstrip(" \n\r-")):
                        match = _annotation_pattern.match(annotation_text)
                        if match is None:
                            raise ValueError("Invalid annotation text:\n" + annotation_text)
                        groups = [s.strip() for s in match.groups()]
                        question, answer, confidence, difficulty, doc_time_rel, text_clip_text = groups
                        text_clip_matches = _text_clip_pattern.findall(text_clip_text)
                        if len(text_clip_text.splitlines()) != 2 * len(text_clip_matches):
                            raise ValueError("Invalid Text Clips in annotation text:\n" + annotation_text)

                        # create Anafora XML annotations for the answers
                        entities = []
                        for begin_text, end_text, _, time_or_doc_time_rel, type_text, clip_text in text_clip_matches:
                            begin = int(begin_text)
                            end = int(end_text)
                            entity_annotation = anafora.AnaforaEntity()
                            entity_annotation.id = '{0:d}@{1}@{2}@gold'.format(entity_count, 'e', file_base)
                            entity_annotation.spans = ((begin, end),)
                            entity_annotation.type = 'EVENT'
                            entity_annotation.parents_type = 'TemporalEntities'
                            if time_or_doc_time_rel == 'DocTimeRel':
                                entity_annotation.properties['DocTimeRel'] = doc_time_rel.upper()
                            entity_count += 1
                            data.annotations.append(entity_annotation)
                            entities.append(entity_annotation)

                        # create an Anafora XML annotation for the question
                        question_annotation = anafora.AnaforaRelation()
                        question_annotation.id = '{0:d}@{1}@{2}@gold'.format(relation_count, 'r', file_base)
                        question_annotation.type = 'Question'
                        question_annotation.parents_type = 'TemporalQuestions'
                        question_annotation.properties['Question'] = question
                        question_annotation.properties['Confidence'] = confidence
                        question_annotation.properties['Difficulty'] = difficulty
                        # FIXME: hacking XML here because current API doesn't allow properties with multiple values
                        for entity in entities:
                            property_elem = anafora.ElementTree.SubElement(question_annotation.properties.xml, 'Answer')
                            property_elem.text = entity.id
                        data.annotations.append(question_annotation)
                        relation_count += 1

                # write the Anafora data out as XML
                output_file_dir = os.path.join(output_dir, file_base)
                output_file_path = os.path.join(output_file_dir, file_base + ".THYME_QA.preannotation.completed.xml")
                if not os.path.exists(output_file_dir):
                    os.makedirs(output_file_dir)
                data.indent()
                data.to_file(output_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    thyme_parser = subparsers.add_parser('thyme')
    thyme_parser.set_defaults(func=fix_thyme_errors)
    thyme_parser.add_argument("-s", "--schema", metavar="FILE", required=True, type=anafora.validate.Schema.from_file,
                              help="An Anafora schema XML file which Anafora annotation XML files will be validated " +
                                   "against.")
    thyme_parser.add_argument("-i", "--input", metavar="DIR", required=True, dest="input_dir",
                              help="The root of a set of Anafora annotation XML directories.")
    thyme_parser.add_argument("-o", "--output", metavar="DIR", required=True, dest="output_dir",
                              help="The directory where the cleaned versions of the Anafora annotation XML files " +
                                   "should be written. The directory structure will mirror the input directory " +
                                   "structure.")
    thyme_parser.add_argument("-x", "--xml-name-regex", metavar="REGEX", default="[.]xml$",
                              help="A regular expression for matching XML files, typically used to restrict the " +
                                   "validation to a subset of the available files (default: %(default)r)")

    thyme_qa_parser = subparsers.add_parser('thyme-qa')
    thyme_qa_parser.set_defaults(func=convert_thyme_qa_to_anafora_xml)
    thyme_qa_parser.add_argument("-i", "--input", metavar="DIR", required=True, dest="input_dir",
                                 help="The root of a set of THYME _qa.txt files.")
    thyme_qa_parser.add_argument("-o", "--output", metavar="DIR", required=True, dest="output_dir",
                                 help="The directory where the Anafora annotation XML files should be written.")

    args = parser.parse_args()
    kwargs = vars(args)
    kwargs.pop('func')(**kwargs)
