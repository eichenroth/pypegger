class Grammar:
    """
    Provides parsing methods for a base Rule
    """

    def __init__(self, base_rule):
        self.base_rule = base_rule

    def parse(self, string):
        """
        Parses an input string to an abstract syntax tree.
        Just a wrapper for the parse method of the base rule.
        :param string: The string to parse.
        :return: The AST.
        """
        return self.base_rule.parse(string)

    def match(self, string):
        """
        Check if a prefix of a string matches the grammar.
        :param string: The string to match.
        :return: Boolean whether the string prefix matches or not.
        """
        return bool(self.parse(string))

    def match_whole(self, string):
        """
        Check if a whole string matches the grammar.
        :param string: The string to match.
        :return: Boolean whether the string matches or not.
        """
        parse_result = self.parse(string)
        return bool(parse_result) and parse_result.end_pos == len(string)
