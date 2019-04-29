[![build-status](https://img.shields.io/travis/friedrichschoene/pegger.svg)](https://travis-ci.org/friedrichschoene/pegger)
![license](https://img.shields.io/github/license/friedrichschoene/pegger.svg)

# Pegger - a small PEG Parsing Tool

    >>> from pegger import *
    >>>
    >>> A = RuleAlias('A')
    >>> A.rule = Choices(Sequence('(', A, ')', A), '')
    >>>
    >>> A.match_whole('()(()(()))()')
    True

We just defined a grammar that can detect if a string of chars consists of well-formed parenthesis.  
The same could be acchived with the following textual definition:

    >>> from pegger.grammar_parser import generate_grammar
    >>>
    >>> grammar = generate_grammar('<A> := "(" <A> ")" <A> / ""')
    >>>
    >>> A.match_whole('()(()(()))()')
    True

Have a look on [all the rules](docs/grammar.md) for grammar generation.

## Todo
 - solve left recursion
 - clean memoization cache
 - ast walker & custom nodes
