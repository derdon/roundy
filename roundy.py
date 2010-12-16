import sys
import codecs
from itertools import imap

from aml import Scanner, Parser as AMLParser, Node


class HTMLNode(Node):
    def __init__(self, name, attributes=None, children=(), text_attr='text'):
        Node.__init__(self, name, attributes, children)
        self.text_attr = text_attr

    def __str__(self):
        str_children = ' '.join(imap(str, self.children))
        return ''.join([self.start_tag, self.text, str_children, self.end_tag])

    @property
    def text(self):
        attributes = self.attributes.iteritems()
        texts = [v for k, v in attributes if k == self.text_attr]
        assert len(texts) in (0, 1)
        try:
            text = texts[0]
        except IndexError:
            text = ''
        return text

    @property
    def start_tag(self):
        attributes = self.attributes.iteritems()
        formatted_attributes = ' '.join(
            '{0}="{1}"'.format(key, value)
            for key, value in attributes if key != self.text_attr
        )
        if formatted_attributes:
            formatted_attributes = ' ' + formatted_attributes
        return '<{0}{1}>'.format(self.name, formatted_attributes)

    @property
    def end_tag(self):
        return '</{0}>'.format(self.name)


def parse_string(src):
    return AMLParser(Scanner(src), HTMLNode).parse()


def parse_file(name, encoding='utf-8'):
    with codecs.open(name, 'r', encoding) as f:
        return parse_string(f.read().encode(encoding))


def main(argv=None, stdin=sys.stdin):
    if not argv:
        argv = sys.argv
    try:
        filename = argv[1]
        return parse_file(filename)
    except IndexError:
        input = sys.stdin.read()
        return parse_string(input)


if __name__ == '__main__':
    print main()
