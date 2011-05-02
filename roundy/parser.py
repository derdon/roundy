#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import sys
# this import is only senseful for python version 2.x and is only supported
# since 2.6
if (3, 0) > sys.version_info[:2] >= (2, 6):
    from future_builtins import map

import cgi
import itertools
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
            '%s="%s"' % (k, v) for k, v in attrs if k != self.text_attr)
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
            return '<%s%s>' % (self.name, self.formatted_attributes)

    def format_end_tag(self, is_xhtml=False):
        if self.is_standalone_tag:
            if is_xhtml:
                return '<%s%s />' % (self.name, self.formatted_attributes)
            else:
                return '<%s%s>' % (self.name, self.formatted_attributes)
        else:
            return '</%s>' % self.name

    def flatten(self):
        for child in self:
            if child.children:
                for subchild in self.flatten(child):
                    yield subchild
            else:
                yield child


def get_doctype(name):
    capitalized_name = name.upper()
    if capitalized_name.startswith('HTML'):
        html = 'HTML'
    elif capitalized_name.startswith('XHTML'):
        html = 'html'
    else:
        raise ValueError(
            'invalid doctype: only the following values are supported:'
            ' %s' % (', '.join(VALID_DOCTYPE_VALUES)))
    prefix = '<!DOCTYPE '
    suffix = '>'
    returned_tuple = DocType.get(name)
    if returned_tuple is None:
        return None
    name, pubid, sysid = returned_tuple
    if not (pubid or sysid):
        return ''.join((prefix, html, suffix)), ''
    else:
        first_line = '%s %s "%s"' % (prefix, html, pubid)
        second_line = '"%s"%s' % (sysid, suffix)
        return first_line, second_line


def parse_string(src, text_attribute='text'):
    return parse_aml_string(src, partial(HTMLNode, text_attr=text_attribute))


def parse_file(filename, text_attribute='text'):
    return parse_aml_file(
        filename,
        NodeClass=partial(HTMLNode, text_attr=text_attribute))


def tokenize(node, is_xhtml=False):
    if node.start_tag:
        yield node.start_tag
    for n in node.flatten():
        if n.start_tag:
            yield n.start_tag
        if n.text:
            yield n.text
        yield n.format_end_tag(is_xhtml)


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
