#!/usr/bin/env python3
"""
Contains a class to perform parsing on simple mathematical expressions
"""

import string
from parsed_object import *


def word(letters):
    for letter in letters:
        yield letter

def ensure_list(item):
    if not isinstance(item, list):
        return [item]
    else:
        return item


class PythonMathParser():
    """
    Main parser class, implements parsing
    """
    
    string_chars = string.ascii_letters + '_'
    number_chars = string.digits + '.'
    single_token_chars = '+-*/^()|'
    precedence_order = [['^'], ['*', '/'], ['+', '-']]
    
    def __init__(self, locals_list=None):
        self.locals_list = locals_list

    def set_locals(self, locals_list):
        """Set the list of allowed variables"""
        self.locals_list = locals_list
    
    def parse(self, expression):
        """Parse the input expression, return a nested list parsed object"""
        expression = expression.replace('**', '^')
        
        tokens = self.tokenize(expression)
        
        nodes = self.build_nodes(tokens)
        
        if isinstance(nodes[0], str):
            nodes[0] = [nodes[0]]
        return nodes[0]
        
    def tokenize(self, expression):
        """Convert the input expression (+!) into a series of tokens"""
        
        if len(expression) == 0:
            raise ValueError('Empty string!')
        if "!" in expression:
            raise ValueError("'!' not permitted in expression!")
        
        expword = word(expression + '!')
        token_list = []
        
        c = next(expword)
        while True:
            if c==' ':
                # Ignore whitespace, but break token here
                c = next(expword)
            elif c=='!':
                # we are done
                return token_list
            elif c in self.single_token_chars:
                token_list.append(c)
                c = next(expword)
            elif c in self.number_chars:
                # scan through numbers
                num_token = ''
                while True:
                    if (c in self.number_chars):
                        # still a number
                        num_token = num_token + c
                    elif (c=='e'):
                        # read exponent (check for minus sign)
                        c = next(expword)
                        if c == '!':
                            raise ValueError('Incorrectly formatted exponent!')
                        elif c in self.number_chars or c == '-':
                            # all good
                            num_token = num_token + 'e' + c
                        else:
                            raise ValueError('Incorrectly formatted exponent!')
                    elif c == '!':
                        token_list.append(float(num_token))
                        return token_list
                    else:
                        break
                    c = next(expword)
                token_list.append(float(num_token))
            elif c in self.string_chars:
                # scan through string
                string_token = c
                c = next(expword)
                if c == '!':
                    if not string_token in self.locals_list:
                        raise ValueError('Unknown variable {}!'.format(
                            string_token))
                    token_list.append(string_token)
                    return token_list
                while c in self.string_chars:
                    string_token = string_token + c
                    c = next(expword)
                if not string_token in self.locals_list:
                    raise ValueError('Unknown variable {}!'.format(
                        string_token))
                token_list.append(string_token)
            else:
                raise ValueError('Invalid character {}!'.format(c))
    
    def build_nodes(self, tokens):
        """
        Transform the list of tokens into nested objects, obeying precedence
        rules and stripping brackets
        """
        
        token_list = list(tokens)
        self.nest_brackets(token_list)
        self.square_brackets(token_list)
        wrap_function = lambda x: UnaryOp('|', x)
        self.nest_brackets(token_list, brackets='curly', wrap=wrap_function)
        self.unary_plus_minus(token_list)
        self.precedence(token_list)
        return token_list
        
    def nest_brackets(self, tokens, brackets='round', wrap=None):
        """
        Cut out sections of tokens wrapped in brackets. Recurse into those
        brackets.
        """
        
        if brackets == 'round':
            l_bracket = '('
            r_bracket = ')'
        elif brackets == 'curly':
            l_bracket = '{'
            r_bracket = '}'
        else:
            raise ValueError('Unknown bracket option {}'.format(brackets))
        
        bracket_depth = 0
        left_bracket_pos = None
        
        pos = 0
        while True:
            c = tokens[pos]
            if isinstance(c, list):
                # recurse into list
                self.nest_brackets(c, brackets, wrap)
                if len(c) == 1 and isinstance(c, list):
                    tokens[pos] = c[0]
            elif c == l_bracket:
                bracket_depth = bracket_depth + 1
                if bracket_depth == 1:
                    left_bracket_pos = pos
            elif c == r_bracket:
                bracket_depth = bracket_depth - 1
                if bracket_depth < 0:
                    raise ValueError('Unmatched parentheses!')
                if bracket_depth == 0:
                    # cut out this section (including brackets)
                    list_section = tokens[left_bracket_pos:pos+1]
                    # strip brackets
                    del list_section[0]
                    del list_section[-1]
                    # recurse into new list_section
                    self.nest_brackets(list_section, brackets, wrap)
                    while (isinstance(list_section[0], list) and
                           len(list_section) == 1):
                        list_section = list_section[0]
                    if wrap is not None:
                        list_section = wrap(list_section)
                    # set section of tokens = [list_section] (the nesting)
                    #tokens[left_bracket_pos:pos+1] = [list_section]
                    del tokens[left_bracket_pos:pos+1]
                    tokens.insert(left_bracket_pos, list_section)
                    # reset pos
                    pos = pos = left_bracket_pos
                    left_bracket_pos = None
            
            pos = pos + 1
            if pos >= len(tokens):
                break
        
        if len(tokens) == 1 and isinstance(tokens[0], list):
            tokens[:] = tokens[0]
        
        if bracket_depth != 0:
            raise ValueError('Unmatched {} brackets!'.format(brackets))
        
        return None
    
    def square_brackets(self, tokens):
        """
        Convert magnitude symbols to square brackets
        """
        
        for i in range(len(tokens)):
            if (not isinstance(tokens[i], str) and
                not isinstance(tokens[i], float)):
                # recurse
                self.square_brackets(tokens[i])
            if tokens[i] == '|':
                if i==0:
                    tokens[i] = '{'
                elif i==len(tokens)-1:
                    tokens[i] = '}'
                else:
                    next_token = tokens[i+1]
                    if (
                            isinstance(next_token, str) and
                            next_token in self.single_token_chars):
                        if next_token == '|':
                            raise ValueError("'||' not allowed!")
                        tokens[i] = '}'
                    else:
                        tokens[i] = '{'

    def unary_plus_minus(self, tokens):
        """
        Run over tokens. Find unary plus/minus and bind.
        """
        
        pos = 0
        while True:
            token = tokens[pos]
            if isinstance(token, list):
                # recurse
                self.unary_plus_minus(token)
            elif isinstance(token, UnaryOp):
                #recurse
                self.unary_plus_minus(token.arg)
            elif isinstance(token, str) and token in ['-', '+']:
                # plus/minus
                unary = False
                if pos == len(tokens) - 1:
                    raise ValueError('Cannot end with operator!')
                elif pos == 0 or (isinstance(last_token, str) and
                                  last_token in self.single_token_chars):
                    # unary plus/minus
                    next_token = tokens[pos+1]
                    if (
                            isinstance(next_token, str) and
                            next_token in self.single_token_chars):
                        raise ValueError('Too many sequential operators!')
                    if token == '+':
                        # can just drop the token
                        del tokens[pos]
                        pos = pos - 1
                        token = tokens[pos]
                    else:
                        # new unary minus
                        op = UnaryOp(token, [next_token])
                        tokens[pos] = op
                        del tokens[pos+1]
            #else:
                #pass
                # either a unary/binary operation, or a value
            
            last_token = tokens[pos]
            pos = pos + 1
            if pos >= len(tokens):
                break

    def precedence(self, tokens):
        """
        Run over tokens. Bind objects according to precedence and left to right
        order. Binary operations only!
        """
        
        for cur_prec in self.precedence_order:
            
            pos = 0
            while True:
                token = tokens[pos]
                if isinstance(token, list):
                    # recurse
                    self.precedence(token)
                elif isinstance(token, UnaryOp):
                    #recurse
                    self.precedence(token.arg)
                elif isinstance(token, BinaryOp):
                    #recurse
                    self.precedence(token.left)
                    self.precedence(token.right)
                elif isinstance(token, str) and token in cur_prec:
                    # binary operator
                    if pos == 0 or pos >= len(tokens):
                        raise ValueError("Can't begin or end with "
                                         "binary operator!")
                    left_token = ensure_list(tokens[pos-1])
                    right_token = ensure_list(tokens[pos+1])
                    op = BinaryOp(token, left_token, right_token)
                    del tokens[pos+1]
                    del tokens[pos]
                    tokens[pos-1] = op
                    pos = pos - 2
                #else:
                    #pass
                    # either a unary/binary operation, or a value
                pos = pos + 1
                if pos >= len(tokens):
                    break
                    
    
    
    
    
    
    
    
    
    
    