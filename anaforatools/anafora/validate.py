import argparse
import collections
import logging
import os

import anafora


class Schema(object):
    def __init__(self, xml):
        """
        :param xml.etree.ElementTree.Element xml: the <schema> element
        """
        default_attribute_elem = xml.find("defaultattribute")
        definition_elem = xml.find("definition")
        entities_elems = definition_elem.findall("entities")
        relations_elems = definition_elem.findall("relations")
        annotations_elems = entities_elems + relations_elems
        if not annotations_elems:
            raise ValueError("no entities or relations in schema")

        self.default_attributes = {}
        if default_attribute_elem is not None:
            for attribute_elem in default_attribute_elem:
                self.default_attributes[attribute_elem.tag] = attribute_elem.text

        self.type_to_properties = {}
        for annotations_elem in annotations_elems:
            if annotations_elem is not None:
                for annotation_elem in annotations_elem:
                    annotation_type = annotation_elem.attrib["type"]
                    properties = {}
                    properties_elem = annotation_elem.find("properties")
                    if properties_elem is not None:
                        for property_elem in properties_elem:
                            schema_property = SchemaProperty(property_elem, self.default_attributes)
                            properties[schema_property.type] = schema_property
                    self.type_to_properties[annotation_type] = properties

    @classmethod
    def from_file(cls, xml_path):
        return cls(anafora.ElementTree.parse(xml_path).getroot())

    def validate(self, annotation):
        """
        :param AnaforaAnnotation annotation: the annotation to be validated
        """
        if annotation.is_self_referential():
            msg = '{0!r} is self-referential'
            raise SchemaValidationError(msg.format(annotation.id))
        schema_properties = self.type_to_properties.get(annotation.type)
        if schema_properties is None:
            msg = 'invalid annotation type {0!r}'
            raise SchemaValidationError(msg.format(annotation.type))
        for schema_property in schema_properties.values():
            if schema_property.required and not schema_property.type in annotation.properties:
                msg = 'missing required property {0!r} of annotation type {1!r}'
                raise SchemaValidationError(msg.format(schema_property.type, annotation.type))
        for name, value in annotation.properties.items():
            if name not in schema_properties:
                msg = 'no property {0!r} defined for annotation type {1!r}'
                raise SchemaValidationError(msg.format(name, annotation.type))
            schema_property = schema_properties[name]
            if schema_property.instance_of is not None:
                if value is None:
                    if schema_property.required:
                        msg = 'missing value for property {0!r} of annotation type {1!r}'
                        raise SchemaValidationError(msg.format(schema_property.type, annotation.type))
                elif not isinstance(value, anafora.AnaforaAnnotation):
                    msg = 'invalid value {0!r} for property {1!r} of annotation type {2!r}'
                    raise SchemaValidationError(msg.format(value, schema_property.type, annotation.type))
                elif not value.type in schema_property.instance_of:
                    msg = 'invalid type {0!r} for property {1!r} of annotation type {2!r}'
                    raise SchemaValidationError(msg.format(value.type, schema_property.type, annotation.type))
            if schema_property.choices is not None:
                if isinstance(value, anafora.AnaforaAnnotation):
                    msg = 'invalid value {0!r} for property {1!r} of annotation type {2!r}'
                    raise SchemaValidationError(msg.format(value, schema_property.type, annotation.type))
                elif value not in schema_property.choices:
                    msg = 'invalid value {0!r} for property {1!r} of annotation type {2!r}'
                    raise SchemaValidationError(msg.format(value, schema_property.type, annotation.type))

    def errors(self, data):
        """
        :param AnaforaData data: the data to be validated
        :return: a list of (invalid annotation, explanation string)
        """
        errors = []
        for annotation in data.annotations:
            try:
                self.validate(annotation)
            except SchemaValidationError as error:
                errors.append((annotation, str(error)))
        return errors


class SchemaProperty(object):
    def __init__(self, xml, default_attributes):
        """
        :param xml.etree.ElementTree.Element xml: the <property> element
        :param dict default_attributes: a mapping holding default attribute (name, value) pairs
        """

        def get(name, default):
            return xml.attrib.get(name, default_attributes.get(name, default))

        self.type = get("type", None)
        self.required = get("required", None) == "True"
        self.instance_of = get("instanceOf", None)
        if self.instance_of is not None:
            self.instance_of = self.instance_of.split(",")
        if get("input", None) == "choice":
            self.choices = xml.text.split(",")
        else:
            self.choices = None


class SchemaValidationError(RuntimeError):
    pass


def log_schema_errors(schema, anafora_dir, xml_name_regex):
    """
    :param Schema schema: the schema to validate against
    :param string anafora_dir: the Anafora directory containing directories to validate
    """
    for sub_dir, text_name, xml_names in anafora.walk(anafora_dir, xml_name_regex):
        for xml_name in xml_names:
            xml_path = os.path.join(anafora_dir, sub_dir, xml_name)
            try:
                data = anafora.AnaforaData.from_file(xml_path)
            except anafora.ElementTree.ParseError:
                logging.error("%s: invalid XML", xml_path)
            except Exception as e:
                logging.error("%s: %s", xml_path, e)
            else:
                for annotation, error in schema.errors(data):
                    logging.warn("%s: %s", xml_path, error)


def find_entities_with_identical_spans(data):
    """
    :param AnaforaData data: the Anafora data to be searched
    """
    span_entities = collections.defaultdict(lambda: [])
    for ann in data.annotations:
        if isinstance(ann, anafora.AnaforaEntity):
            span_entities[ann.spans].append(ann)
    for span, annotations in span_entities.items():
        if len(annotations) > 1:
            yield span, annotations


def log_entities_with_identical_spans(anafora_dir, xml_name_regex):
    """
    :param AnaforaData data: the Anafora data to be searched
    """
    for sub_dir, text_name, xml_names in anafora.walk(anafora_dir, xml_name_regex):
        for xml_name in xml_names:
            xml_path = os.path.join(anafora_dir, sub_dir, xml_name)
            try:
                data = anafora.AnaforaData.from_file(xml_path)
            except anafora.ElementTree.ParseError:
                pass
            else:
                for span, annotations in find_entities_with_identical_spans(data):
                    logging.warn("%s: multiple entities for span %s:\n%s",
                                 xml_path, span, "\n".join(str(ann).rstrip() for ann in annotations))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""%(prog)s validates Anafora XML files against an Anafora schema and
        logs any errors. It can also identify other potential errors such as the presence of distinct entities with
        identical text spans.""")
    parser.add_argument("-s", "--schema", metavar="FILE", required=True,
                        help="An Anafora schema XML file against which Anafora annotation XML files should be " +
                             "validated.")
    parser.add_argument("-i", "--input", metavar="DIR", required=True, dest="anafora_dir",
                        help="The root of a set of Anafora annotation XML directories.")
    parser.add_argument("-x", "--xml-name-regex", metavar="REGEX", default="[.]xml$",
                        help="A regular expression for matching XML files, typically used to restrict the validation " +
                             "to a subset of the available files (default: %(default)r)")
    parser.add_argument("--identical-spans", action='store_true',
                        help="Also log any pairs of entities that span the exact same text offsets.")
    args = parser.parse_args()
    logging.basicConfig(format="%(levelname)s:%(message)s")

    log_schema_errors(Schema.from_file(args.schema), args.anafora_dir, args.xml_name_regex)
    if args.identical_spans:
        log_entities_with_identical_spans(args.anafora_dir, args.xml_name_regex)
