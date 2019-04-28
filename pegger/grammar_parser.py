# Pairs are used as parsing success objects.
# They consist of a parsing result object (which can be a Boolean) and an end_pos element.
from . import RuleAlias, String, Range, Any, Choices, Sequence, And, Not, ZeroOrMore, OneOrMore, Optional


class GrammarDefinitionNotParsableException(Exception):
    pass

def generate_grammar(string):
    parsed_grammar = _grammar(string, 0)
    if not parsed_grammar:
        raise GrammarDefinitionNotParsableException()

    # create alias to rule dict
    aliases = {}
    visited = set()
    for alias, rule in parsed_grammar[0]:
        alias.rule = rule
        aliases[alias.name] = alias

    for alias in aliases.values():
        _replace_aliases(alias.rule, aliases, visited)

    # return first alias
    return aliases[parsed_grammar[0][0][0].name]

def _replace_aliases(rule, aliases, visited):
    if rule in visited:
        return
    visited.add(rule)
    if hasattr(rule, 'rule'):
        if isinstance(rule.rule, RuleAlias):
            rule.rule = aliases[rule.rule.name]
        _replace_aliases(rule.rule, aliases, visited)
    if hasattr(rule, 'rules'):
        for i, child_rule in enumerate(rule.rules):
            if isinstance(child_rule, RuleAlias):
                child_rule = rule.rules[i] = aliases[child_rule.name]
            _replace_aliases(child_rule, aliases, visited)

def memoize(f):
    memoization_dict = {}
    def helper(*args):
        if args in memoization_dict:
            return memoization_dict[args]
        return memoization_dict.setdefault(args, f(*args))
    return helper

### Hierarchical syntax
@memoize
def _grammar(string, start_pos):
    spacing_success = _spacing(string, start_pos)
    if spacing_success:
        definition_success = _definition(string, spacing_success[1])
        if definition_success:
            definitions = [definition_success[0]]
            while True:
                definition_success_2 = _definition(string, definition_success[1])
                if definition_success_2:
                    definition_success = definition_success_2
                    definitions.append(definition_success_2[0])
                    continue
                break
            end_of_file_success = _end_of_file(string, definition_success[1])
            if end_of_file_success:
                return definitions, end_of_file_success[1]

@memoize
def _definition(string, start_pos):
    identifier_success = _identifier(string, start_pos)
    if identifier_success:
        left_arrow_success = _substring(string, identifier_success[1], ':=')
        if left_arrow_success:
            expression_success = _expression(string, left_arrow_success[1])
            if expression_success:
                return (identifier_success[0], expression_success[0]), expression_success[1]

@memoize
def _expression(string, start_pos):
    sequence_success = _sequence(string, start_pos)
    choices = Choices(sequence_success[0])
    if sequence_success:
        while True:
            slash_success = _substring(string, sequence_success[1], '/')
            if slash_success:
                sequence_success_2 = _sequence(string, slash_success[1])
                if sequence_success_2:
                    sequence_success = sequence_success_2
                    choices.add_rule(sequence_success_2[0])
                    continue
                break
            break
        return choices, sequence_success[1]

@memoize
def _sequence(string, start_pos):
    prefix_success = True, start_pos
    sequence = Sequence()
    while True:
        prefix_success_2 = _prefix(string, prefix_success[1])
        if prefix_success_2:
            prefix_success = prefix_success_2
            sequence.add_rule(prefix_success_2[0])
            continue
        break
    return sequence, prefix_success[1]

@memoize
def _prefix(string, start_pos):
    and_success = _substring(string, start_pos, '&')
    if and_success:
        suffix_success = _suffix(string, and_success[1])
        if suffix_success:
            return And(suffix_success[0]), suffix_success[1]
    not_success = _substring(string, start_pos, '!')
    if not_success:
        suffix_success = _suffix(string, not_success[1])
        if suffix_success:
            return Not(suffix_success[0]), suffix_success[1]
    suffix_success = _suffix(string, start_pos)
    if suffix_success:
        return suffix_success

@memoize
def _suffix(string, start_pos):
    primary_success = _primary(string, start_pos)
    if primary_success:
        question_success = _substring(string, primary_success[1], '?')
        if question_success:
            return Optional(primary_success[0]), question_success[1]
        star_success = _substring(string, primary_success[1], '*')
        if star_success:
            return ZeroOrMore(primary_success[0]), star_success[1]
        plus_success = _substring(string, primary_success[1], '+')
        if plus_success:
            return OneOrMore(primary_success[0]), plus_success[1]
        return primary_success

@memoize
def _primary(string, start_pos):
    identifier_success = _identifier(string, start_pos)
    if identifier_success:
        left_arrow_success = _substring(string, identifier_success[1], ':=')
        if not left_arrow_success:
            return identifier_success
    open_success = _substring(string, start_pos, '(')
    if open_success:
        expression_success = _expression(string, open_success[1])
        if expression_success:
            close_success = _substring(string, expression_success[1], ')')
            if close_success:
                return expression_success[0], close_success[1]
    literal_success = _literal(string, start_pos)
    if literal_success:
        return literal_success
    class_success = _class(string, start_pos)
    if class_success:
        return class_success
    dot_success = _substring(string, start_pos, '.')
    if dot_success:
        return Any(), dot_success[1]

### Lexical syntax
@memoize
def _identifier(string, start_pos):
    if string[start_pos:start_pos + 1] == '<':
        ident_start_success = _ident_start(string, start_pos + 1)
        if ident_start_success:
            ident_cont_success = True, ident_start_success[1]
            while True:
                ident_cont_success_2 = _ident_cont(string, ident_cont_success[1])
                if ident_cont_success_2:
                    ident_cont_success = ident_cont_success_2
                    continue
                break
            if string[ident_cont_success[1]:ident_cont_success[1] + 1] == '>':
                spacing_success = _spacing(string, ident_cont_success[1] + 1)
                if spacing_success:
                    return RuleAlias(string[start_pos + 1:ident_cont_success[1]]), spacing_success[1]

@memoize
def _ident_start(string, start_pos):
    if len(string) > start_pos:
        char_code = ord(string[start_pos])
        if 65 <= char_code <= 90 or 97 <= char_code <= 122 or char_code == 95:
            return True, start_pos + 1

@memoize
def _ident_cont(string, start_pos):
    if len(string) > start_pos:
        char_code = ord(string[start_pos])
        if 65 <= char_code <= 90 or 97 <= char_code <= 122 or char_code == 95 or 48 <= char_code <= 57:
            return True, start_pos + 1

@memoize
def _literal(string, start_pos):
    def literal_helper(string, start_pos, quotation_mark):
        if string[start_pos:start_pos + 1] == quotation_mark:
            char_success = True, start_pos + 1
            while True:
                if string[char_success[1]:char_success[1] + 1] != quotation_mark:
                    char_success_2 = _char(string, char_success[1])
                    if char_success_2:
                        char_success = char_success_2
                        continue
                    break
                break
            if string[char_success[1]:char_success[1] + 1] == quotation_mark:
                spacing_success = _spacing(string, char_success[1] + 1)
                if spacing_success:
                    return String(string[start_pos + 1:char_success[1]]), spacing_success[1]
    literal_success = literal_helper(string, start_pos, '\'')
    if literal_success:
        return literal_success
    literal_success = literal_helper(string, start_pos, '\"')
    if literal_success:
        return literal_success

@memoize
def _class(string, start_pos):
    if string[start_pos:start_pos + 1] == '[':
        range_success = True, start_pos + 1
        choices = Choices()
        while True:
            if string[range_success[1]:range_success[1] + 1] != ']':
                range_success_2 = _range(string, range_success[1])
                if range_success_2:
                    range_success = range_success_2
                    choices.add_rule(range_success_2[0])
                    continue
                break
            break
        if string[range_success[1]:range_success[1] + 1] == ']':
            spacing_success = _spacing(string, range_success[1] + 1)
            if spacing_success:
                return choices, spacing_success[1]

@memoize
def _range(string, start_pos):
    char_success = _char(string, start_pos)
    if char_success:
        if string[char_success[1]:char_success[1] + 1] == '-':
            char2_success = _char(string, char_success[1] + 1)
            if char2_success:
                return Range(string[start_pos], string[start_pos + 2]), char2_success[1]
        return Range(string[start_pos]), char_success[1]

@memoize
def _char(string, start_pos):
    if string[start_pos:start_pos + 1] == '\\':
        if len(string) > start_pos + 1:
            escaped_char_code = ord(string[start_pos + 1:start_pos + 2])
            # 110 = n, 114 = r, 116 = t, 39 = ', 34 = ", 91 = [, 93 = ], 92 = \
            if escaped_char_code in [110, 114, 116, 39, 34, 91, 93, 92]:
                return True, start_pos + 2
    else:
        if len(string[start_pos:start_pos + 1]):
            return True, start_pos + 1

@memoize
def _substring(string, start_pos, substring):
    if string[start_pos:start_pos + len(substring)] == substring:
        spacing_success = _spacing(string, start_pos + len(substring))
        if spacing_success:
            return True, spacing_success[1]

@memoize
def _spacing(string, start_pos):
    spacing_success = True, start_pos
    while True:
        space_success = _space(string, spacing_success[1])
        if space_success:
            spacing_success = True, space_success[1]
            continue
        comment_success = _comment(string, spacing_success[1])
        if comment_success:
            spacing_success = True, comment_success[1]
            continue
        break
    return spacing_success

@memoize
def _comment(string, start_pos):
    if string[start_pos:start_pos + 1] == '#':
        comment_success = True, start_pos + 1
        while True:
            if not _end_of_line(string, comment_success[1]):
                if not _end_of_file(string, comment_success[1]):
                    comment_success = True, comment_success[1] + 1
                    continue
            break
        end_of_line_success = _end_of_line(string, comment_success[1])
        if end_of_line_success:
            return True, end_of_line_success[1]
        return True, comment_success[1]

@memoize
def _space(string, start_pos):
    if string[start_pos:start_pos + 1] == ' ':
        return True, start_pos + 1
    if string[start_pos:start_pos + 1] == '\t':
        return True, start_pos + 1
    end_of_line_success = _end_of_line(string, start_pos)
    if end_of_line_success:
        return True, end_of_line_success[1]

@memoize
def _end_of_line(string, start_pos):
    if string[start_pos:start_pos + 2] == '\r\n':
        return True, start_pos + 2
    if string[start_pos:start_pos + 1] == '\n':
        return True, start_pos + 1
    if string[start_pos:start_pos + 1] == '\r':
        return True, start_pos + 1


def _end_of_file(string, start_pos):
    if len(string) <= start_pos:
        return True, start_pos
