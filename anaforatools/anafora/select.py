import argparse
import os

import anafora


class Select(object):
    def __init__(self, include=None, exclude=None):
        self.include = None
        if include is not None:
            self.include = set()
            for item in include:
                self.include.add(item if isinstance(item, tuple) else (item,))
        self.exclude = None
        if exclude is not None:
            self.exclude = set()
            for item in exclude:
                self.exclude.add(item if isinstance(item, tuple) else (item,))

    def __call__(self, type_name, prop_name=None, prop_value=None):
        def expand(*args):
            args = [a for a in args if a is not None]
            result = set()
            if len(args) == 1:
                result.add((args[0],))
                result.add(('*',))
            else:
                for rest in expand(*args[1:]):
                    result.add((args[0],) + rest)
                    result.add(('*',) + rest)
            return result

        if self.include is not None:
            if not (expand(type_name) & self.include):
                if not (expand(type_name, prop_name) & self.include):
                    if not (expand(type_name, prop_name, prop_value) & self.include):
                        return False
        if self.exclude is not None:
            if expand(type_name) & self.exclude:
                return False
            if expand(type_name, prop_name) & self.exclude:
                return False
            if expand(type_name, prop_name, prop_value) & self.exclude:
                return False
        return True


def _main(input_dir, output_dir, xml_name_regex="[.]xml$", include=None, exclude=None):
    select = Select(include, exclude)

    for sub_dir, text_name, xml_names in anafora.walk(input_dir, xml_name_regex):
        for xml_name in xml_names:

            # reads in the data from the input file
            xml_path = os.path.join(input_dir, sub_dir, xml_name)
            data = anafora.AnaforaData.from_file(xml_path)

            # find annotations and properties to remove
            annotations_to_remove = []
            annotation_properties_to_remove = []
            for annotation in data.annotations:

                # remove the annotation if its type has not been selected
                if not select(annotation.type):
                    annotations_to_remove.append(annotation)
                else:
                    for name, value in annotation.properties.items():

                        # remove the property if its name or value has not been selected
                        if not select(annotation.type, name, value):
                            annotation_properties_to_remove.append((annotation, name))

            # if we're overwriting, save a backup of the original
            if annotations_to_remove or annotation_properties_to_remove:
                data.to_file(xml_path + ".bak")

            # do the actual removal of annotations here
            for annotation in annotations_to_remove:
                data.annotations.remove(annotation)
            for annotation, name in annotation_properties_to_remove:
                del annotation.properties[name]

            # writes out the modified data to the output file
            output_sub_dir = os.path.join(output_dir or input_dir, sub_dir)
            if not os.path.exists(output_sub_dir):
                os.makedirs(output_sub_dir)
            output_path = os.path.join(output_sub_dir, xml_name)
            data.to_file(output_path)


if __name__ == "__main__":
    def split_tuple_on_colons(string):
        return tuple(string.split(":"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", metavar="DIR", required=True, dest="input_dir",
                        help="The root of a set of Anafora annotation XML directories.")
    parser.add_argument("-o", "--output", metavar="DIR", dest="output_dir",
                        help="The directory where the cleaned versions of the Anafora annotation XML files should be " +
                             "written. The directory structure will mirror the input directory structure.")
    parser.add_argument("-x", "--xml-name-regex", metavar="REGEX", default="[.]xml$",
                        help="A regular expression for matching XML files in the input subdirectories " +
                             "(default: %(default)r)")
    parser.add_argument("--include", metavar="EXPR", nargs="+", type=split_tuple_on_colons,
                        help="An expression identifying types of annotations to be included in the data. " +
                             "The expression takes the form type[:property[:value]. For example, TLINK would only " +
                             "include TLINK annotations (and TLINK properties and property values) in the " +
                             "evaluation, while TLINK:Type:CONTAINS would only include TLINK annotations with a Type " +
                             "property that has the value CONTAINS.")
    parser.add_argument("--exclude", metavar="EXPR", nargs="+", type=split_tuple_on_colons,
                        help="An expression identifying types of annotations to be excluded from the data. " +
                             "The expression takes the form type[:property[:value] (see --include).")

    args = parser.parse_args()
    _main(**vars(args))