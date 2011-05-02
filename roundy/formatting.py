import itertools

from roundy.parser import get_doctype, tokenize, guess_token_type


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
