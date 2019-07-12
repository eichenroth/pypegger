import pytest

from pegger.grammar import Grammar
from pegger.rules import *


def test_grammar():
    # {a^n b^n c^n | n \in N}
    A = Choices()
    A.add_rule(Sequence('a', A, 'b'))
    A.add_rule('ab')
    B = Choices()
    B.add_rules(Sequence('b', B, 'c'), 'bc')
    D = Choices(Not(Any()),  Sequence(And(Sequence(A, Not('b'))), ZeroOrMore('a'), B, Not(Any())))

    grammar = Grammar(D)
    assert grammar.match_whole('')
    assert grammar.match_whole('aaabbbccc')
    assert grammar.match_whole('aaaaaabbbbbbcccccc')

    assert not grammar.match_whole('a')
    assert not grammar.match_whole('b')
    assert not grammar.match_whole('c')

    assert not grammar.match_whole('aabbbccc')
    assert not grammar.match_whole('aaabbccc')
    assert not grammar.match_whole('aaabbbcc')
