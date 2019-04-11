class ParsingSuccess:
    def __init__(self, string, rule_type, start_pos, end_pos, children):
        self.string = string
        self.rule_type = rule_type
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.children = children

    @property
    def match_string(self):
        return self.string[self.start_pos:self.end_pos]
