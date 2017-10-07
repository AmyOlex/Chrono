import argparse
import os
import re

import sys

import anafora
import anafora.timeml


def copy_timeml_text(text_dir, anafora_dir, xml_name_regex, write_dct):
    text_name_to_path = {}
    for dir_path, _, file_names in os.walk(text_dir):
        for file_name in file_names:
            if file_name.endswith(".tml"):
                file_path = os.path.join(dir_path, file_name)
                text_name_to_path[file_name[:-4]] = file_path

    def get_dct(path):
        dct = anafora.timeml.to_document_creation_time(path)
        return dct[:10]

    _copy_text(text_name_to_path=text_name_to_path,
               get_text=anafora.timeml.to_text,
               get_dct=get_dct if write_dct else None,
               anafora_dir=anafora_dir,
               xml_name_regex=xml_name_regex)


def copy_plain_text(text_dir, anafora_dir, xml_name_regex, write_dct):
    if write_dct:
        raise ValueError("write_dct is not supported for plain text")
    text_name_to_path = {}
    for dir_path, _, file_names in os.walk(text_dir):
        for file_name in file_names:
            text_name_to_path[file_name] = os.path.join(dir_path, file_name)
    _copy_text(text_name_to_path=text_name_to_path,
               get_text=lambda path: open(path).read(),
               get_dct=None,
               anafora_dir=anafora_dir,
               xml_name_regex=xml_name_regex)


def copy_mayo_text(text_dir, anafora_dir, xml_name_regex, write_dct):
    text_name_to_path = {}
    for dir_path, _, file_names in os.walk(text_dir):
        for file_name in file_names:
            text_name_to_path[file_name] = os.path.join(dir_path, file_name)

    def get_dct(path):
        dct_pattern = r"\[meta rev_date=\"(?P<m>\d+)/(?P<d>\d+)/(?P<y>\d+)\""
        with open(path) as f:
            match = re.match(dct_pattern, f.read())
        kwargs = {name: int(value) for name, value in match.groupdict().items()}
        return "{y}-{m:02}-{d:02}".format(**kwargs)

    _copy_text(text_name_to_path=text_name_to_path,
               get_text=lambda path: open(path).read(),
               get_dct=get_dct if write_dct else None,
               anafora_dir=anafora_dir,
               xml_name_regex=xml_name_regex)


def _copy_text(text_name_to_path,
               get_text,
               get_dct,
               anafora_dir,
               xml_name_regex):
    for sub_dir, text_file_name, _ in anafora.walk(
            anafora_dir, xml_name_regex=xml_name_regex):
        if text_file_name not in text_name_to_path:
            sys.exit("No text file found for " + text_file_name)
        text_path = os.path.join(anafora_dir, sub_dir, text_file_name)
        if os.path.exists(text_path):
            sys.exit("Text file already exists: " + text_path)
        input_path = text_name_to_path[text_file_name]
        text = get_text(input_path)
        with open(text_path, 'w') as text_file:
            text_file.write(text)
        if get_dct is not None:
            dct_path = text_path + ".dct"
            if os.path.exists(dct_path):
                sys.exit("DCT file already exists: " + dct_path)
            dct = get_dct(input_path)
            with open(dct_path, 'w') as dct_file:
                dct_file.write(dct)
                dct_file.write("\n")


if __name__ == "__main__":
    format_funcs = dict(plain=copy_plain_text,
                        mayo=copy_mayo_text,
                        timeml=copy_timeml_text)

    parser = argparse.ArgumentParser(
        description="Copies text files to their expected locations in an " +
                    "Anafora XML directory hierarchy. That is, each text " +
                    "file that exactly matches the name of a directory in " +
                    "the Anafora XML directory hierarchy will be copied into " +
                    "that directory.")
    parser.add_argument(
        "-x", "--xml-name-regex",
        metavar="REGEX", default=".*completed.*[.]xml$",
        help="The regular expression which identifies Anafora XML files " +
             "(default: %(default)r).")
    parser.add_argument(
        "--format", choices=format_funcs, default="plain",
        help="The format of files in the text directory " +
             "(default: %(default)r). When the 'timeml' format is selected, " +
             "TimeML files are expected to have the extension '.tml', and " +
             "the text of a '.tml' file is the result of stripping that file " +
             "of all its XML tags. The 'mayo' and 'plain' formats both " +
             "simply copy over the text files directly; the only difference " +
             "is that the 'mayo' format also supports the --dct flag.")
    parser.add_argument(
        "--dct", action="store_true", dest="write_dct",
        help="Also write out a file for the document creation time.")
    parser.add_argument("text_dir")
    parser.add_argument("anafora_dir")

    kwargs = vars(parser.parse_args())
    format_funcs[kwargs.pop("format")](**kwargs)
