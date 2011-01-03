#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if (3, 0) > sys.version_info[:2] >=  (2, 6):
    from future_builtins import map

import cgi
import argparse
import itertools
from os import path
from functools import partial

from aml import (Node, parse_string as parse_aml_string,
    parse_file as parse_aml_file)
try:
    from genshi.output import DocType
except ImportError:
    # use a local version if Genshi is not installed
    from genshi_util import DocType

VALID_DOCTYPE_VALUES = frozenset([
    '"html" or "html-strict"',
    '"html-transitional"',
    '"html-frameset"',
    '"html5"',
    '"xhtml" or "xhtml-strict"',
    '"xhtml-transitional"',
    '"xhtml-frameset"',
    '"xhtml11"'
])

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

    def __unicode__(self):
        return ''.join(map(unicode.lstrip, pprint(self)))

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
        return cgi.escape(texts[0]) if texts else ''

    @property
    def start_tag(self):
        if self.is_standalone_tag:
            return ''
        else:
            return '<{}{}>'.format(self.name, self.formatted_attributes)

    def format_end_tag(self, is_xhtml=False):
        if self.is_standalone_tag:
            if is_xhtml:
                return '<{}{} />'.format(self.name, self.formatted_attributes)
            else:
                return '<{}{}>'.format(self.name, self.formatted_attributes)
        else:
            return '</{}>'.format(self.name)


def get_doctype(name):
    capitalized_name = name.upper()
    if capitalized_name.startswith('HTML'):
        html = 'HTML'
    elif capitalized_name.startswith('XHTML'):
        html = 'html'
    else:
        raise ValueError(
            'invalid doctype: only the following values are supported:'
            '\n- {}'.format('\n- '.join(VALID_DOCTYPE_VALUES)))
    prefix = '<!DOCTYPE '
    suffix = '>'
    returned_tuple = DocType.get(name)
    if returned_tuple is None:
        return None
    name, pubid, sysid = returned_tuple
    if not (pubid or sysid):
        return ''.join((prefix, html, suffix)), ''
    else:
        first_line = '{} {} "{}"'.format(prefix, html, pubid)
        second_line = '"{}"{}'.format(sysid, suffix)
        return first_line, second_line


def parse_string(src, text_attribute='text'):
    return parse_aml_string(src, partial(HTMLNode, text_attr=text_attribute))


def parse_file(filename, text_attribute='text'):
    return parse_aml_file(
        filename,
        NodeClass=partial(HTMLNode, text_attr=text_attribute))


def flatten_node(node):
    for child in node:
        if child.children:
            for subchild in flatten_node(child):
                yield subchild
        else:
            yield child


def tokenize(node, is_xhtml=False):
    if node.start_tag:
        yield node.start_tag
    flattened_node = flatten_node(node)
    for node in flattened_node:
        if node.start_tag:
            yield node.start_tag
        if node.text:
            yield node.text
        yield node.format_end_tag(is_xhtml)


def token2tag_name(token):
    '''
    >>> token2tag_name('<img src="tree.jpg" alt="A photo of a tree">')
    >>> 'img'
    >>> token2tag_name('<H1>')
    >>> 'H1'
    '''
    return token.lstrip('</').rstrip('>').split(None, 1)[0]


def guess_token_type(token, is_xhtml=False):
    is_standalone = token2tag_name(token).upper() in STANDALONE_TAGS
    if token.startswith('<'):
        if token.startswith('</') and token.endswith('>'):
            return 'end'
        elif token.endswith('/>') and is_xhtml and is_standalone:
            return 'standalone'
        elif token.endswith('>'):
            # looks like a start tag, but is a standalone tag if HTML is used
            # and the tag is in STANDALONE_TAGS
            if not is_xhtml and is_standalone:
                return 'standalone'
            else:
                return 'start'
        else:
            raise SyntaxError
    else:
        return 'text'


def pprint(node, indent=4):
    is_xhtml = False
    # first thing to do: yield a doctype (splitted up into two lines) if the
    # root node has the attribute "doctype"
    if node.get_attr('doctype'):
        shorthand = node['doctype']
        if shorthand.lower().startswith('xhtml'):
            is_xhtml = True
        first_line, second_line = get_doctype(shorthand)
        yield first_line
        if second_line:
            # empty in HTML5
            yield second_line
        # remove this attribute because it was only used as a helper to
        # describe the doctype
        del node['doctype']
    depth = 0
    tokens, copy_of_tokens = itertools.tee(tokenize(node, is_xhtml))
    copy_of_tokens = list(copy_of_tokens)
    for line, token in enumerate(tokens):
        base_indentation = ' ' * indent
        indentation = base_indentation * depth
        tok_type = guess_token_type(token)
        assert tok_type in ('start', 'text', 'standalone', 'end')
        try:
            next_token = copy_of_tokens[line + 1]
        except IndexError:
            # this tag is already the last token in the list, so there
            # is no next token
            next_token = ''
        next_tok_type = guess_token_type(next_token)
        assert next_tok_type in ('start', 'text', 'standalone', 'end')
        if tok_type == 'start':
            # only indent if the next line is not an end tag
            if next_tok_type != 'end':
                depth += 1
            yield indentation + token
        elif tok_type == 'text':
            depth -= 1
            yield indentation + token
        elif tok_type in ('standalone', 'end'):
            # look at the following token and check if it is an end tag. If it
            # is, the next line has to be outdented
            if next_tok_type == 'end':
                depth -= 1
            yield indentation + token
    # depth should be 0 again, as before the iteration
    #assert depth == 0


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
                'the path {} does not exist'.format(value))
        if not path.isfile(value):
            raise argparse.ArgumentTypeError(
                'the path {} is not a file'.format(value))
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


def main(argv=None, stdin=sys.stdin):
    if not argv:
        argv = sys.argv[1:]
    args = parse_args(argv)
    if args.filename:
        nodes = parse_file(args.filename, args.text_attribute)
    else:
        nodes = parse_string(stdin.read(), args.text_attribute)
    if args.pretty:
        try:
            output = '\n'.join(pprint(nodes, args.indent))
        except ValueError as e:
            errmsg = 'Error: {}'.format(e)
            # prepend a newline before the error message if no filename was
            # given to distinguish it from the input
            if not args.filename:
                errmsg = '\n' + errmsg
            return errmsg
    else:
        output = nodes
    if args.outputfile:
        with open(args.outputfile, 'w') as f:
            f.write(unicode(output).encode('utf-8'))
    else:
        return output

if __name__ == '__main__':
    print(unicode(main()).encode('utf-8') or '', end='')
