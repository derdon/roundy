from __future__ import print_function

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if sys.version_info.major == 2 and sys.version_info.minor >= 6:
    from future_builtins import map

import argparse
import itertools

from aml import (Node, parse_string as parse_aml_string,
    parse_file as parse_aml_file)

STANDALONE_TAGS = frozenset((
    'AREA',
    'BASE',
    'BASEFONT',
    'BR',
    'COL',
    'FRAME',
    'HR',
    'IMG',
    'INPUT',
    'ISINDEX',
    'LINK',
    'META',
    'PARAM'))


class HTMLNode(Node):
    def __init__(self, name, attributes=None, children=(), text_attr='text'):
        Node.__init__(self, name, attributes, children)
        self.text_attr = text_attr

    def __str__(self):
        str_children = ' '.join(map(str, self.children))
        return ''.join([self.start_tag, self.text, str_children, self.end_tag])

    @property
    def is_standalone_tag(self):
        return self.name.upper() in STANDALONE_TAGS

    @property
    def formatted_attributes(self):
        attrs = list(self.attributes.items())
        formatted_attributes = ' '.join(
            '{}="{}"'.format(k, v) for k, v in attrs if k != self.text_attr)
        if formatted_attributes:
            formatted_attributes = ' ' + formatted_attributes
        return formatted_attributes

    @property
    def text(self):
        attributes = list(self.attributes.items())
        texts = [v for k, v in attributes if k == self.text_attr]
        assert len(texts) in (0, 1)
        return texts[0] if texts else ''

    @property
    def start_tag(self):
        if self.is_standalone_tag:
            return ''
        else:
            return '<{}{}>'.format(self.name, self.formatted_attributes)

    @property
    def end_tag(self):
        if self.is_standalone_tag:
            return '<{}{} />'.format(self.name, self.formatted_attributes)
        else:
            return '</{}>'.format(self.name)


def parse_string(src):
    return parse_aml_string(src, HTMLNode)


def parse_file(filename):
    return parse_aml_file(filename, NodeClass=HTMLNode)


def tokenize(nodes):
    if nodes.start_tag:
        yield nodes.start_tag
    for node in nodes:
        for n in tokenize(node):
            yield n
    if nodes.text:
        yield nodes.text
    yield nodes.end_tag


def guess_token_type(token):
    if token.startswith('<'):
        if token.startswith('</') and token.endswith('>'):
            return 'end'
        elif token.endswith('/>'):
            return 'standalone'
        elif token.endswith('>'):
            return 'start'
        else:
            raise SyntaxError
    else:
        return 'text'


def pprint(node, indent=4):
    depth = 0
    tokens, copy_of_tokens = itertools.tee(tokenize(node))
    copy_of_tokens = list(copy_of_tokens)
    for line, token in enumerate(tokens):
        base_indentation = ' ' * indent
        indentation = base_indentation * depth
        tok_type = guess_token_type(token)
        assert tok_type in ('start', 'text', 'standalone', 'end')
        if tok_type == 'start':
            depth += 1
            yield indentation + token
        elif tok_type == 'text':
            depth -= 1
            yield indentation + token
        elif tok_type in ('standalone', 'end'):
            # look at the following token and check if it is an end tag. If it
            # is, the next line has to be outdented
            try:
                next_token = copy_of_tokens[line + 1]
            except IndexError:
                # this end tag is already the last token in the list, so there
                # is no next token
                next_token = ''
            next_tok_type = guess_token_type(next_token)
            if next_tok_type == 'end':
                depth -= 1
            yield indentation + token
    # depth should be 0 again, as before the iteration
    assert depth == 0


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
        '-i', '--indent', type=int, default=4, choices=xrange(sys.maxsize),
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
    print(main() or '', end='')
