from .results import ParsingSuccess


class Rule:
    def __init__(self):
        self.memoizationDict = {}

    def parse(self, string, start_pos):
        return self.memoizationDict.setdefault((hash(string), start_pos), self._parse(string, start_pos))

    def _parse(self, string, start_pos):
        raise NotImplementedError


class RuleCollection(Rule):
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
    def _parse(self, string, start_pos):
        for rule in self.rules:
            rule_result = rule.parse(string, start_pos)
            if rule_result:
                ParsingSuccess(string, self.__class__, start_pos, rule_result.end_pos, rule_result)
                return rule_result
        return False


class Sequence(RuleCollection):
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
    def _parse(self, string, start_pos):
        rule_result = self.rule.parse(string, start_pos)
        if rule_result:
            return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])
        return False


class Not(RuleWrapper):
    def _parse(self, string, start_pos):
        if self.rule.parse(string, start_pos):
            return False
        return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])


class ZeroOrMore(RuleWrapper):
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
    def _parse(self, string, start_pos):
        rule_result = self.rule.parse(string, start_pos)
        if rule_result:
            return ParsingSuccess(string, self.__class__, start_pos, rule_result.end_pos, [rule_result])
        else:
            return ParsingSuccess(string, self.__class__, start_pos, start_pos, [])
