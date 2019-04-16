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

        def string_rep(rule):
            return f'"{rule.s}"'

        def choice_rep(rule):
            return ' | '.join([self._generate_nonterminal(sub_rule)[0] for sub_rule in rule.rules])

        def sequence_rep(rule):
            return ' '.join([self._generate_nonterminal(sub_rule)[0] for sub_rule in rule.rules])

        def and_rep(rule):
            return f'&{self._generate_nonterminal(rule.rule)}'

        def not_rep(rule):
            return f'&{self._generate_nonterminal(rule.rule)}'

        def zero_or_more_rep(rule):
            return f'{self._generate_nonterminal(rule.rule)}*'

        def one_or_more_rep(rule):
            return f'{self._generate_nonterminal(rule.rule)}+'

        def optional_rep(rule):
            return f'{self._generate_nonterminal(rule.rule)}?'

        method = {
            String: string_rep,
            Choices: choice_rep,
            Sequence: sequence_rep,
            And: and_rep,
            Not: not_rep,
            ZeroOrMore: zero_or_more_rep,
            OneOrMore: one_or_more_rep,
            Optional: optional_rep,
        }[type(rule)]

        return self.rule_representations.setdefault(rule, method(rule))

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



    ## string

    # def _generate_rep(self, nonterminals):
    #     symbol = chr(nonterminals['last_symbol_code'] + 1)
    #     return nonterminals.setdefault(self, (symbol, f'"{self.s}"'))

    ## allgemein

    # def __str__(self):
    #     """
    #     Generates the string representation of the grammar following the PEG notation.
    #     :return: String representation.
    #     """
    #     nonterminals = {'last_symbol_code': ord('A') - 1}
    #     self._generate_rep(nonterminals)
    #     rule_reps = []
    #     for key, value in nonterminals.items():
    #         if isinstance(key, Rule):
    #             rule_reps.append(f'<{value[0]}> := {value[1]}')
    #     return '\n'.join(rule_reps)
    #
    # def _generate_rep(self, nonterminals):
    #     raise NotImplementedError








def generate_grammar(grammar_string):
    pass






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


