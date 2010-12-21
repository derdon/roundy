from itertools import izip


def handle_for(node):
    # FIXME: may raise IndexError
    variable, num_range = list(node.attributes.items()[0])
    start, end = num_range.split('..')
    numbers = range(*map(int, (start, end)))
    parent = node.parent
    first_child = node.first_child
    return first_child
    #for i in numbers:
        #node.
        #for_(node)
    #parent.remove(node)


def handle_repeat(node):
    raise NotImplementedError


def handle_while(node):
    raise NotImplementedError


def handle_assign(node):
    '''
    (assign foo 42)
    '''
    raise NotImplementedError


def handle_access(node):
    '''access the given variable. The following example uses the variables cls
    and txt:

    (p
        class (access (cls))
        text (access (txt)))
    '''
    raise NotImplementedError

def convert(node):
    if node.name == 'for':
        yield handle_for(node)
    #elif ...:
    #   pass
    else:
        #yield node
        yield None
    for node in node.children:
        for node in convert(node):
            yield node
