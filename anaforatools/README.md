anaforatools
============

The anaforatools project provides utilities for working with [Anafora](https://github.com/weitechen/anafora) annotations including:
* `anafora.validate` - checks Anafora XML files for syntactic and semantic errors
* `anafora.evaluate` - compares two sets of Anafora XML files in terms of precision, recall, etc.
* `anafora.regex` - trains and applies simple regular expression models from Anafora XML files

For details on the command line interfaces to these modules, use the `--help` argument. For example:
```
$ python -m anafora.validate --help
```

Requirements:
* Python 2.7 or later
* Python [regex](https://pypi.python.org/pypi/regex) module
