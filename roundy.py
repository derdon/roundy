from __future__ import print_function

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if sys.version_info.major == 2 and sys.version_info.minor >= 6:
    from future_builtins import map

from aml import Node, parse_string, parse_file


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


def main(argv=None, stdin=sys.stdin):
    if not argv:
        argv = sys.argv
    try:
        filename = argv[1]
        return parse_file(filename, NodeClass=HTMLNode)
    except IndexError:
        input = sys.stdin.read()
        return parse_string(input, HTMLNode)

if __name__ == '__main__':
    print(main())
