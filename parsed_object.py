"""
Classes storing components of parsed expression, and utility function to
walk over all elements
"""


__unary_dict = {'-': (lambda x: -x),
                '|': (lambda x: abs(x))}
__binary_dict = {'+': (lambda x, y: x + y),
                 '-': (lambda x, y: x - y),
                 '*': (lambda x, y: x * y),
                 '/': (lambda x, y: x / y),
                 '^': (lambda x, y: x**y)}

class UnaryOp():
    def __init__(self, op, arg):
        self.op = op
        self.arg = arg
    
    def __str__(self):
        if isinstance(self.arg, list) and len(self.arg) == 1:
            arg = self.arg[0]
        else:
            arg = self.arg
        if self.op == '|':
            return '|{!s}|'.format(arg)
        else:
            return '({}{!s})'.format(self.op, arg)
    
    def __repr__(self):
        return 'UnaryOp({!r},{!r})'.format(self.op, self.arg)


class BinaryOp():
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    
    def __str__(self):
        if isinstance(self.left, list) and len(self.left) == 1:
            left = self.left[0]
        else:
            left = self.left
        if isinstance(self.right, list) and len(self.right) == 1:
            right = self.right[0]
        else:
            right = self.right
        return '({1!s}{0}{2!s})'.format(self.op, left, right)
    
    def __repr__(self):
        return 'BinaryOp({},{!r},{!r})'.format(self.op, self.left, self.right)


def walk(input_item):
    if isinstance(input_item, list):
        item = input_item
    else:
        item = [input_item]
    if isinstance(item[0], UnaryOp):
        recurse = walk(item[0].arg)
        for rec_item in recurse:
            yield rec_item
    elif isinstance(item[0], BinaryOp):
        recurse = walk(item[0].left)
        for rec_item in recurse:
            yield rec_item
        recurse = walk(item[0].right)
        for rec_item in recurse:
            yield rec_item
    else:
        yield item


def gen_calc(parsed, translate_values,
             unary_dict=__unary_dict, binary_dict=__binary_dict):
    
    fields, values = zip(*translate_values)
    
    def func(*args, **kwargs):
        if 'item' in kwargs:
            item = kwargs['item']
        else:
            item = parsed
        if isinstance(item, UnaryOp):
            op = unary_dict[item.op]
            arg = func(*args, item=item.arg[0])
            return op(arg)
        elif isinstance(item, BinaryOp):
            op = binary_dict[item.op]
            left = func(*args, item=item.left[0])
            right = func(*args, item=item.right[0])
            return op(left, right)
        elif isinstance(item, float):
            return item
        else:
            index = fields.index(item)
            if callable(values[index]):
                return values[index](*args)
            else:
                return values[index]

    return func













