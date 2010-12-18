from __future__ import print_function

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if sys.version_info.major == 2 and sys.version_info.minor >= 6:
    from future_builtins import map

import argparse

from aml import (Node, parse_string as parse_aml_string,
    parse_file as parse_aml_file)


class HTMLNode(Node):
    def __init__(self, name, attributes=None, children=(), text_attr='text'):
        Node.__init__(self, name, attributes, children)
        self.text_attr = text_attr

    def __str__(self):
        str_children = ' '.join(map(str, self.children))
        return ''.join([self.start_tag, self.text, str_children, self.end_tag])

    @property
    def text(self):
        attributes = list(self.attributes.items())
        texts = [v for k, v in attributes if k == self.text_attr]
        assert len(texts) in (0, 1)
        return texts[0] if texts else ''

    @property
    def start_tag(self):
        attrs = list(self.attributes.items())
        formatted_attributes = ' '.join(
            '{}="{}"'.format(k, v) for k, v in attrs if k != self.text_attr)
        if formatted_attributes:
            formatted_attributes = ' ' + formatted_attributes
        return '<{}{}>'.format(self.name, formatted_attributes)

    @property
    def end_tag(self):
        return '</{}>'.format(self.name)


def parse_string(src):
    return parse_aml_string(src, HTMLNode)


def parse_file(filename):
    return parse_aml_file(filename, NodeClass=HTMLNode)


def pprint(node, indent=4):

    def pprint_format(node):
        start_nodes = []
        end_nodes = []
        texts = []

        def inner(node):
            start_nodes.append(node.start_tag)
            end_nodes.append(node.end_tag)
            texts.append(node.text)
            for node in node.children:
                inner(node)
        inner(node)
        return start_nodes, texts, end_nodes
    start_tags, texts, end_tags = pprint_format(node)
    for (i, tag), text in zip(enumerate(start_tags), texts):
        base_indentation = ' ' * indent
        indentation = base_indentation * i
        yield indentation + tag
        if text:
            yield indentation + base_indentation + text
    for i, tag in reversed(list(enumerate(end_tags))):
        indentation = (' ' * indent) * i
        yield indentation + tag


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            'Convert a lisp-like file into HTML and'
            'print its output to STDOUT by default.'))
    parser.add_argument(
        'filename', help='path to the file which has to be parsed.')
    parser.add_argument(
        '-p', '--pretty', action='store_true',
        help='Enable pretty printing of the HTML output')
    parser.add_argument(
        '-i', '--indent', type=int, default=4,
        help=(
            'The number of spaces to use for indenting the output (only used '
            'in combination with the option -p --pretty). '
            'The lowest possible value is 0.'))
    # this option must be here because it's warm and cuddly :-)
    parser.add_argument(
        '-o', '--outputfile', help='write the output to the file')
    return parser.parse_args(argv)


def main(argv=None, stdin=sys.stdin):
    if not argv:
        argv = sys.argv[1:]
    args = parse_args(argv)
    if args.filename:
        nodes = parse_file(args.filename)
        if args.pretty:
            output = '\n'.join(pprint(nodes, args.indent))
        else:
            output = nodes
        if args.outputfile:
            with open(args.outputfile, 'w') as f:
                f.write(str(output))
        else:
            return output
    else:
        return parse_string(stdin.read())

if __name__ == '__main__':
    print(main())
