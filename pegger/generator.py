from pegger import *


class RuleRepresentation:
    def __init__(self, rule):
        self.rule_nonterminals = {rule: 'A'}
        self.rule_representations = {}
        self.last_nonterminal_ord = ord('A')

        self._rule_queue = [rule]
        while len(self._rule_queue):
            rule = self._rule_queue.pop()
            self._generate_representation(rule)

    def _generate_representation(self, rule):
        if rule in self.rule_representations:
            return self.rule_representations[rule]

        method = 'rep_' + rule.__class__.__name__
        representor = getattr(self, method)
        return self.rule_representations.setdefault(rule, representor(rule))

    def rep_String(self, rule):
        return f'"{rule.s}"'

    def rep_Choices(self, rule):
        return ' | '.join([self._generate_nonterminal(sub_rule)[0] for sub_rule in rule.rules])

    def rep_Sequence(self, rule):
        return ' '.join([self._generate_nonterminal(sub_rule)[0] for sub_rule in rule.rules])

    def rep_And(self, rule):
        return f'&{self._generate_nonterminal(rule.rule)}'

    def rep_Not(self, rule):
        return f'&{self._generate_nonterminal(rule.rule)}'

    def rep_ZeroOrMore(self, rule):
        return f'{self._generate_nonterminal(rule.rule)}*'

    def rep_OneOrMore(self, rule):
        return f'{self._generate_nonterminal(rule.rule)}+'

    def rep_Optional(self, rule):
        return f'{self._generate_nonterminal(rule.rule)}?'

    def _generate_nonterminal(self, rule):
        if rule in self.rule_nonterminals:
            return self.rule_nonterminals[rule]

        self._rule_queue.append(rule)
        self.last_nonterminal_ord += 1
        nonterminal = chr(self.last_nonterminal_ord)
        self.rule_nonterminals[rule] = nonterminal
        return nonterminal

    def __str__(self):
        result = ''
        for key, value in self.rule_nonterminals.items():
            result = f'{result}\n{value} <- {self.rule_representations[key]}'
        return result

# One Rule per line
#
# Nonterminal symbols     <Nonterminal>
# Strings                 'string' "string"
# Choice                  <Nonterminal> | "string" | <Nonterminal>
# Sequence                <Nonterminal "string" <Nonterminal>
# And (lookahead)         &"string" &<Nonterminal> &("string" | <Nonterminal>)
# Not                     !"string" !<Nonterminal> !("string" | <Nonterminal>) !!"string"
# ZeroOrMore              <Nonterminal>* "string"* (<Nonterminal> "string")*
# OneOrMore               <Nonterminal>+ "string"+ (<Nonterminal> "string")+
# Optional                <Nonterminal>? "string"? (<Nonterminal> "string")?


