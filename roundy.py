from __future__ import print_function

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if sys.version_info.major == 2 and sys.version_info.minor >= 6:
    from future_builtins import map

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


def pprint(node, indent=4):
    start_tags, texts, end_tags = pprint_format(node)
    for (i, tag), text in zip(enumerate(start_tags), texts):
        base_indentation = ' ' * indent
        indentation = base_indentation * i
        print(indentation + tag)
        if text:
            print(indentation + base_indentation + text)
    for i, tag in reversed(list(enumerate(end_tags))):
        indentation = (' ' * indent) * i
        print(indentation + tag)


def main(argv=None, stdin=sys.stdin):
    if not argv:
        argv = sys.argv
    try:
        filename = argv[1]
        return parse_file(filename)
    except IndexError:
        return parse_string(stdin.read())

if __name__ == '__main__':
    print(main())
