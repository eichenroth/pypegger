from .results import ParsingSuccess


class Rule:
    """
    Abstract base class every rule inherits from.
    This class should not be used directly to generate a grammar.
    """

    def __init__(self):
        self.memoization_dict = {}

    def match(self, string):
        """
        Check if a prefix of a string matches the grammar defined by this rule.
        :param string: The string to match.
        :return: Boolean whether the string prefix matches or not.
        """
        if self.parse(string):
            return True
        return False

    def match_whole(self, string):
        """
        Check if a whole string matches the grammar defined by this rule.
        :param string: The string to match.
        :return: Boolean whether the string matches or not.
        """
        parse_result = self.parse(string)
        if parse_result and parse_result.end_pos == len(string):
            return True
        return False

    def parse(self, string, start_pos = 0):
        """
        Parses an input string to an abstract syntax tree.
        :param string: The string to parse.
        :param start_pos: Starting position within the string.
        :return: The AST.
        """
        key = (hash(string), start_pos)

        if key in self.memoization_dict:
            return self.memoization_dict[key]
        return self.memoization_dict.setdefault(key, self._parse(string, start_pos))

    def _parse(self, string, start_pos):
        """
        Abstract method which is implemented by the subclasses doing the main parsing magic.
        :param string: The string to parse.
        :param start_pos: Starting position whithin the string.
        :return: The AST.
        """
        raise NotImplementedError


class RuleCollection(Rule):
    """
    Abstract base class for rules that consist of multiple subrules.
    """

    def __init__(self, *rules):
        super().__init__()
        self.rules = rules

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, rules):
        for rule in rules:
            assert isinstance(rule, Rule) or type(rule) == str
        self._rules = [String(rule) if type(rule) == str else rule for rule in rules]


class RuleWrapper(Rule):
    """
    Abstract base class for rules that consist of a single subrule.
    """

    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, rule):
        assert isinstance(rule, Rule) or type(rule) == str
        self._rule = String(rule) if type(rule) == str else rule


class String(Rule):
    """
    Rule consisting of just a string to match.
    """

    def __init__(self, s):
        assert type(s) == str
        super().__init__()
        self.s = s

    def _parse(self, string, start_pos):
        if string[start_pos:start_pos + len(self.s)] == self.s:
            return ParsingSuccess(string, self.__class__, start_pos, start_pos + len(self.s), [])
        else:
            return False


class Choice(RuleCollection):
    """
    Prioritized choice rule, e.g, `(A | B | C)`.
    """

    def _parse(self, string, start_pos):
        for rule in self.rules:
            rule_result = rule.parse(string, start_pos)
            if rule_result:
                ParsingSuccess(string, self.__class__, start_pos, rule_result.end_pos, rule_result)
                return rule_result
        return False


class Sequence(RuleCollection):
    """
    Sequence of rules, e.g. `A B C`.
    """

    def _parse(self, string, start_pos):
        pos = start_pos
        children = []
        for rule in self.rules:
            rule_result = rule.parse(string, pos)
            if rule_result:
                children.append(rule_result)
                pos = rule_result.end_pos
            else:
                return False
        return ParsingSuccess(string, self.__class__, start_pos, pos, children)


class And(RuleWrapper):
    """
    And (lookahead) rule that allows to check the string without consuming it, e.g. `&A`.
    """

    def _parse(self, string, start_pos):
        rule_result = self.rule.parse(string, start_pos)
        if rule_result:
            return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])
        return False


class Not(RuleWrapper):
    """
    Not rule that checks the string if a rule is not applicable, e.g. `!A`.
    """

    def _parse(self, string, start_pos):
        if self.rule.parse(string, start_pos):
            return False
        return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])


class ZeroOrMore(RuleWrapper):
    """
    Zero or more rule, e.g. `A*`.
    """

    def _parse(self, string, start_pos):
        pos = start_pos
        children = []
        while True:
            rule_result = self.rule.parse(string, pos)
            if rule_result:
                children.append(rule_result)
                pos = rule_result.end_pos
            else:
                break
        return ParsingSuccess(string, self.__class__, start_pos, pos, children)


# maybe think this code over, adds one iteration over the children list
class OneOrMore(RuleWrapper):
    """
    One or more rule, e.g. `A+`.
    """

    def __init__(self, rule):
        super().__init__(rule)
        self.zero_or_more_rule = ZeroOrMore(rule)

    def _parse(self, string, start_pos):
        rule_result = self.rule.parse(string, start_pos)
        if rule_result:
            zero_or_more_result = self.zero_or_more_rule.parse(string, rule_result.end_pos)
            if zero_or_more_result:
                return ParsingSuccess(string, self.__class__, start_pos, zero_or_more_result.end_pos, [rule_result] + zero_or_more_result.children)
            else:
                return ParsingSuccess(string, self.__class__, start_pos, rule_result.end_pos, [rule_result])
        return False


class Optional(RuleWrapper):
    """
    Optional rule, e.g. `A?`.
    """

    def _parse(self, string, start_pos):
        rule_result = self.rule.parse(string, start_pos)
        if rule_result:
            return ParsingSuccess(string, self.__class__, start_pos, rule_result.end_pos, [rule_result])
        else:
            return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])
