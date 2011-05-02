from __future__ import with_statement

import sys

from roundy.parser import parse_file, parse_string
from roundy.formatting import pprint
from roundy.cli import parse_args


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
        except ValueError, e:
            errmsg = 'Error: %s' % e
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
