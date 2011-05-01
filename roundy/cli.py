import argparse
from os import path


def parse_args(argv):
    default_indent = 2

    def indent_int(string):
        value = int(string)
        if value < 0:
            value = default_indent
        return value

    def filename(string):
        value = path.abspath(path.expanduser(string))
        if not path.exists(value):
            raise argparse.ArgumentTypeError(
                'the path %s does not exist' % value)
        if not path.isfile(value):
            raise argparse.ArgumentTypeError(
                'the path %s is not a file' % value)
        return value
    parser = argparse.ArgumentParser(
        description=(
            'Convert a lisp-like file into HTML and '
            'print its output to STDOUT by default.'))
    parser.add_argument(
        '-f', '--filename', type=filename,
        help='path to the file which has to be parsed.')
    parser.add_argument(
        '-t', '--text-attribute', default='text',
        help='the name of the attribute to use for marking text')
    parser.add_argument(
        '-p', '--pretty', action='store_true',
        help='Enable pretty printing of the HTML output')
    parser.add_argument(
        '-i', '--indent', type=indent_int, default=default_indent,
        help=(
            'The number of spaces to use for indenting the output (only used '
            'in combination with the option -p --pretty). '
            'Only values which are greater than or equal to 0 will take effect'
            ' (because negative indentations do not make any sense).'))
    # this option must be here because it's warm and cuddly :-)
    parser.add_argument(
        '-o', '--outputfile', type=filename,
        help='write the output to the file OUTPUTFILE instead of STDOUT')
    return parser.parse_args(argv)
