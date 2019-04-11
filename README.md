# Pegger - small PEG parsing tool

    >>> from pegger import *
    >>>
    >>> grammar = Choice()
    >>> grammar.rules = [Sequence('(', grammar, ')', grammar), '']
    >>> string = '(())()(((()))())(())'
    >>>
    >>> grammar.match_whole(string)
    True

This gets you a grammar able to checks if a string is in  the language of balanced parentheses (each opening parenthesis has a closing one.)

## Todo
 - parsing of grammar given as string
 - solve left recursion
 - clean memoization cache
 - ast walker
 - generate custom ast nodes
 - testing
 - add helper rules, e.g. whitespace