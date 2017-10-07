import argparse
import os

import anafora


def _flatten_to_ints(items):
    for item in items:
        if not isinstance(item, int):
            for sub_item in _flatten_to_ints(item):
                yield sub_item
        else:
            yield item


def add_relations_to_closest(data, source_type, target_type,
                             relation_type, relation_source_property_name, relation_target_property_name,
                             relation_other_properties=None):
    """
    Adds a relation from each `source_type` annotation to the closest `target_type` annotation.

    :param anafora.AnaforaData data: the Anafora data where relations should be added
    :param str source_type: the type of the source annotations
    :param str target_type: the type of the target annotations
    :param str relation_type: the type of relation annotation to be created
    :param str relation_source_property_name: the name of the property on the relation annotation that should point to
        the source annotation
    :param str relation_target_property_name: the name of the property on the relation annotation that should point to
        the target annotation
    :param list relation_other_properties: a list of (name, value) tuples of other properties that should be set on the
        relation annotations that are created
    """

    # map the id of each source/target annotation to its character offsets
    points = {}
    for source_entity in data.annotations.select_type(source_type):
        points[source_entity.id] = list(_flatten_to_ints(source_entity.spans))
    for target_entity in data.annotations.select_type(target_type):
        points[target_entity.id] = list(_flatten_to_ints(target_entity.spans))

    # add a relation for each source entity
    target_entities = list(data.annotations.select_type(target_type))
    if target_entities:
        source_entities = list(data.annotations.select_type(source_type))
        for source_entity in source_entities:

            # distance to an annotation is the minimum distance to any one of its character offsets
            def distance_to_source_entity(entity):
                return min(abs(p1 - p2) for p1 in points[source_entity.id] for p2 in points[entity.id])

            # find the target entity that is closest to the source entity
            target_entity = min(target_entities, key=distance_to_source_entity)

            # create a relation annotation per the various arguments to this function
            relation = anafora.AnaforaRelation()
            relation.id = "{0}@{1}@{2}".format(source_entity.id, relation_type, target_entity.id)
            data.annotations.append(relation)
            relation.type = relation_type
            relation.properties[relation_source_property_name] = source_entity
            relation.properties[relation_target_property_name] = target_entity
            if relation_other_properties is not None:
                for name, value in relation_other_properties:
                    relation.properties[name] = value

    data.indent()


if __name__ == "__main__":
    def _pair(value):
        return value.split("=")

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", metavar="DIR", required=True, dest="input_dir",
                        help="The root of a set of Anafora annotation XML directories.")
    parser.add_argument("-x", "--xml-name-regex", metavar="REGEX", default="[.]xml$",
                        help="A regular expression for matching XML files, typically used to restrict the validation " +
                             "to a subset of the available files (default: %(default)r)")
    parser.add_argument("-o", "--output", metavar="DIR", required=True, dest="output_dir",
                        help="The directory where the predictions should be written (as Anafora XML files). The " +
                             "directory structure will mirror the input directory structure.")

    subparsers = parser.add_subparsers()

    relations_to_closest_parser = subparsers.add_parser('closest', help="Link each source annotation to the target " +
                                                                        "annotation with the closest character offsets")
    relations_to_closest_parser.set_defaults(func=add_relations_to_closest)
    relations_to_closest_parser.add_argument("-s", "--source", metavar="TYPE", dest="source_type", required=True,
                                             help="The <type> of the source annotations.")
    relations_to_closest_parser.add_argument("-t", "--target", metavar="TYPE", dest="target_type", required=True,
                                             help="The <type> of the target annotations.")
    relations_to_closest_parser.add_argument("-r", "--relation", metavar="TYPE", dest="relation_type", required=True,
                                             help="The <type> of relation annotation to be created.")
    relations_to_closest_parser.add_argument("-rs", "--relation-source", metavar="NAME", required=True,
                                             dest="relation_source_property_name",
                                             help="The name of the property on the relation annotation that should " +
                                                  "point to the source annotation.")
    relations_to_closest_parser.add_argument("-rt", "--relation-target", metavar="NAME", required=True,
                                             dest="relation_target_property_name",
                                             help="The name of the property on the relation annotation that should " +
                                                  "point to the target annotation.")
    relations_to_closest_parser.add_argument("-ro", "--relation-other", metavar="NAME=VALUE", nargs='+', type=_pair,
                                             dest="relation_other_properties",
                                             help="Other properties that should be added to the relation annotation.")

    args = parser.parse_args()
    kwargs = vars(args)
    func = kwargs.pop("func")
    input_dir = kwargs.pop('input_dir')
    xml_name_regex = kwargs.pop('xml_name_regex')
    output_dir = kwargs.pop('output_dir')

    for sub_dir, _, xml_file_names in anafora.walk(input_dir, xml_name_regex):
        for xml_file_name in xml_file_names:
            input_data = anafora.AnaforaData.from_file(os.path.join(input_dir, sub_dir, xml_file_name))
            func(input_data, **kwargs)
            output_sub_dir = os.path.join(output_dir, sub_dir)
            if not os.path.exists(output_sub_dir):
                os.makedirs(output_sub_dir)
            input_data.to_file(os.path.join(output_dir, sub_dir, xml_file_name))
