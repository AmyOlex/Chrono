import argparse
import os
import re

import anafora


def to_text(timeml_path):
    """
    :param xml.etree.ElementTree.Element timeml_path: path of the TimeML XML
    :return string: the (plain) text content of the XML
    """
    return ''.join(anafora.ElementTree.parse(timeml_path).getroot().itertext())


def to_document_creation_time(timeml_path):
    root = anafora.ElementTree.parse(timeml_path).getroot()
    dct_xpath = ".//TIMEX3[@functionInDocument='CREATION_TIME']"
    for timex3 in root.iterfind(dct_xpath):
        return timex3.attrib["value"]


def to_anafora_data(timeml_path):
    """
    :param xml.etree.ElementTree.Element timeml_path: path of the TimeML XML
    :return anafora.AnaforaData: an Anafora version of the TimeML annotations
    """
    entity_tags = {"TIMEX3", "EVENT", "SIGNAL"}
    tag_id_attrs = {
        "TIMEX3": "tid",
        "EVENT": "eid",
        "SIGNAL": "sid",
        "MAKEINSTANCE": "eiid",
        "TLINK": "lid",
        "SLINK": "lid",
        "ALINK": "lid",
    }
    ref_id_attrs = {"eventID", "signalID", "beginPoint", "endPoint", "valueFromFunction", "anchorTimeID",
                    "eventInstanceID", "timeID", "signalID", "relatedToEventInstance", "relatedToTime",
                    "subordinatedEventInstance", "tagID"}
    text = to_text(timeml_path)
    data = anafora.AnaforaData()
    root = anafora.ElementTree.parse(timeml_path).getroot()

    prefix_to_char = {'t': 'e', 'e': 'e', 's': 'e', 'ei': 'r', 'l': 'r'}
    timeml_id_to_anafora_id = {}
    count = 1
    file_base, _ = os.path.splitext(os.path.basename(timeml_path))
    for elem in root.iter():
        if elem.tag in tag_id_attrs:
            timeml_id = elem.attrib[tag_id_attrs[elem.tag]]
            [(prefix, number)] = re.findall(r'^(\D+)(\d+)$', timeml_id)
            timeml_id_to_anafora_id[timeml_id] = '{0:d}@{1}@{2}@gold'.format(count, prefix_to_char[prefix], file_base)
            count += 1

    def add_annotations_from(elem, offset=0):
        start = offset
        annotation = None
        if elem.tag in tag_id_attrs:
            annotation = anafora.AnaforaEntity() if elem.tag in entity_tags else anafora.AnaforaRelation()
            id_attr = tag_id_attrs[elem.tag]
            annotation.id = timeml_id_to_anafora_id[elem.attrib[id_attr]]
            annotation.type = elem.tag
            if isinstance(annotation, anafora.AnaforaEntity):
                annotation.spans = ((start, start),)
            for name, value in elem.attrib.items():
                if name != id_attr:
                    if name in ref_id_attrs:
                        value = timeml_id_to_anafora_id[value]
                    annotation.properties[name] = value
            data.annotations.append(annotation)

        if elem.text is not None:
            offset += len(elem.text)
        for child in elem:
            offset = add_annotations_from(child, offset)

        if annotation is not None and isinstance(annotation, anafora.AnaforaEntity):
            annotation.spans = ((start, offset),)
            if elem.text != text[start:offset]:
                raise ValueError('{0}: "{1}" != "{2}"'.format(timeml_path, elem.text, text[start:offset]))

        if elem.tail is not None:
            offset += len(elem.tail)
        return offset

    add_annotations_from(root)
    return data


def _timeml_dir_to_anafora_dir(timeml_dir, anafora_dir, schema_name="TimeML"):
    for root, _, file_names in os.walk(timeml_dir):
        if root.startswith(timeml_dir):
            sub_dir = root[len(timeml_dir):].lstrip(os.path.sep)
        else:
            sub_dir = ''

        for file_name in file_names:
            if file_name.endswith(".tml"):
                file_path = os.path.join(root, file_name)
                text = to_text(file_path)
                data = to_anafora_data(file_path)
                data.indent()

                anafora_file_name = file_name[:-4]
                anafora_file_dir = os.path.join(anafora_dir, sub_dir, anafora_file_name)
                if not os.path.exists(anafora_file_dir):
                    os.makedirs(anafora_file_dir)
                anafora_file_path = os.path.join(anafora_file_dir, anafora_file_name)

                with open(anafora_file_path, 'w') as text_file:
                    text_file.write(text)
                data.indent()
                data.to_file("{0}.{1}.gold.completed.xml".format(anafora_file_path, schema_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeml-dir", required=True)
    parser.add_argument("--anafora-dir", required=True)
    parser.add_argument("--schema-name", default="TimeML")
    args = parser.parse_args()
    _timeml_dir_to_anafora_dir(args.timeml_dir, args.anafora_dir, args.schema_name)
