# Pairs are used as parsing success objects.
# They consist of a ParsingResult and a end_pos element.

def memoize(f):
    memoization_dict = {}
    def helper(*args):
        key = (hash(arg) for arg in args)
        if key in memoization_dict:
            return memoization_dict[key]
        return memoization_dict.setdefault(key, f(*args))
    return helper


### Hierarchical syntax
@memoize
def grammar(string, start_pos):
    spacing_success = spacing(string, start_pos)
    if spacing_success:
        definition_success = definition(string, spacing_success[1])
        if definition_success:
            while True:
                definition_success_2 = definition(string, definition_success[1])
                if definition_success_2:
                    definition_success = definition_success_2
                    continue
                break
            end_of_file_success = end_of_file(string, definition_success[1])
            if end_of_file_success:
                return True, end_of_file_success[1]

@memoize
def definition(string, start_pos):
    identifier_success = identifier(string, start_pos)
    if identifier_success:
        left_arrow_success = substring(string, identifier_success[1], ':=')
        if left_arrow_success:
            expression_success = expression(string, left_arrow_success[1])
            if expression_success:
                return True, expression_success[1]

@memoize
def expression(string, start_pos):
    sequence_success = sequence(string, start_pos)
    if sequence_success:
        while True:
            slash_success = substring(string, sequence_success[1], '/')
            if slash_success:
                sequence_success_2 = sequence(string, slash_success[1])
                if sequence_success_2:
                    sequence_success = sequence_success_2
                    continue
                break
            break
        return True, sequence_success[1]

@memoize
def sequence(string, start_pos):
    prefix_success = True, start_pos
    while True:
        prefix_success_2 = prefix(string, prefix_success[1])
        if prefix_success_2:
            prefix_success = prefix_success_2
            continue
        break
    return True, prefix_success[1]

@memoize
def prefix(string, start_pos):
    and_success = substring(string, start_pos, '&')
    if and_success:
        suffix_success = suffix(string, and_success[1])
        if suffix_success:
            return True, suffix_success[1]
    not_success = substring(string, start_pos, '!')
    if not_success:
        suffix_success = suffix(string, not_success[1])
        if suffix_success:
            return True, suffix_success[1]
    suffix_success = suffix(string, start_pos)
    if suffix_success:
        return True, suffix_success[1]

@memoize
def suffix(string, start_pos):
    primary_success = primary(string, start_pos)
    if primary_success:
        question_success = substring(string, primary_success[1], '?')
        if question_success:
            return True, question_success[1]
        star_success = substring(string, primary_success[1], '*')
        if star_success:
            return True, star_success[1]
        plus_success = substring(string, primary_success[1], '+')
        if plus_success:
            return True, plus_success[1]
        return True, primary_success[1]

@memoize
def primary(string, start_pos):
    identifier_success = identifier(string, start_pos)
    if identifier_success:
        left_arrow_success = substring(string, identifier_success[1], ':=')
        if not left_arrow_success:
            return True, identifier_success[1]
    open_success = substring(string, start_pos, '(')
    if open_success:
        expression_success = expression(string, open_success[1])
        if expression_success:
            close_success = substring(string, expression_success[1], ')')
            if close_success:
                return True, close_success[1]
    literal_success = literal(string, start_pos)
    if literal_success:
        return True, literal_success[1]
    class_success = class_(string, start_pos)
    if class_success:
        return True, class_success[1]
    dot_success = substring(string, start_pos, '.')
    if dot_success:
        return True, dot_success[1]

### Lexical syntax
@memoize
def identifier(string, start_pos):
    if string[start_pos:start_pos + 1] == '<':
        ident_start_success = ident_start(string, start_pos + 1)
        if ident_start_success:
            ident_cont_success = True, ident_start_success[1]
            while True:
                ident_cont_success_2 = ident_cont(string, ident_cont_success[1])
                if ident_cont_success_2:
                    ident_cont_success = ident_cont_success_2
                    continue
                break
            if string[ident_cont_success[1]:ident_cont_success[1] + 1] == '>':
                spacing_success = spacing(string, ident_cont_success[1] + 1)
                if spacing_success:
                    return True, spacing_success[1]

@memoize
def ident_start(string, start_pos):
    if len(string) > start_pos:
        char_code = ord(string[start_pos])
        if 65 <= char_code <= 90 or 97 <= char_code <= 122 or char_code == 95:
            return True, start_pos + 1

@memoize
def ident_cont(string, start_pos):
    if len(string) > start_pos:
        char_code = ord(string[start_pos])
        if 65 <= char_code <= 90 or 97 <= char_code <= 122 or char_code == 95 or 48 <= char_code <= 57:
            return True, start_pos + 1

@memoize
def literal(string, start_pos):
    def literal_helper(string, start_pos, quotation_mark):
        if string[start_pos:start_pos + 1] == quotation_mark:
            char_success = True, start_pos + 1
            while True:
                if string[char_success[1]:char_success[1] + 1] != quotation_mark:
                    char_success_2 = char(string, char_success[1])
                    if char_success_2:
                        char_success = char_success_2
                        continue
                    break
                break
            if string[char_success[1]:char_success[1] + 1] == quotation_mark:
                spacing_success = spacing(string, char_success[1] + 1)
                if spacing_success:
                    return True, spacing_success[1]
    literal_success = literal_helper(string, start_pos, '\'')
    if literal_success:
        return literal_success
    literal_success = literal_helper(string, start_pos, '\"')
    if literal_success:
        return literal_success

@memoize
def class_(string, start_pos):
    if string[start_pos:start_pos + 1] == '[':
        range_success = True, start_pos + 1
        while True:
            if string[range_success[1]:range_success[1] + 1] != ']':
                range_success_2 = range_(string, range_success[1])
                if range_success_2:
                    range_success = range_success_2
                    continue
                break
            break
        if string[range_success[1]:range_success[1] + 1] == ']':
            spacing_success = spacing(string, range_success[1] + 1)
            if spacing_success:
                return True, spacing_success[1]

@memoize
def range_(string, start_pos):
    char_success = char(string, start_pos)
    if char_success:
        if string[char_success[1]:char_success[1] + 1] == '-':
            char2_success = char(string, char_success[1] + 1)
            if char2_success:
                return True, char2_success[1]
        return True, char_success[1]

@memoize
def char(string, start_pos):
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
def substring(string, start_pos, substring):
    if string[start_pos:start_pos + len(substring)] == substring:
        spacing_success = spacing(string, start_pos + len(substring))
        if spacing_success:
            return True, spacing_success[1]

@memoize
def spacing(string, start_pos):
    spacing_success = True, start_pos
    while True:
        space_success = space(string, spacing_success[1])
        if space_success:
            spacing_success = True, space_success[1]
            continue
        comment_success = comment(string, spacing_success[1])
        if comment_success:
            spacing_success = True, comment_success[1]
            continue
        break
    return spacing_success

@memoize
def comment(string, start_pos):
    if string[start_pos:start_pos + 1] == '#':
        comment_success = True, start_pos + 1
        while True:
            if not end_of_line(string, comment_success[1]):
                if not end_of_file(string, comment_success[1]):
                    comment_success = True, comment_success[1] + 1
                    continue
            break
        end_of_line_success = end_of_line(string, comment_success[1])
        if end_of_line_success:
            return True, end_of_line_success[1]
        return True, comment_success[1]

@memoize
def space(string, start_pos):
    if string[start_pos:start_pos + 1] == ' ':
        return True, start_pos + 1
    if string[start_pos:start_pos + 1] == '\t':
        return True, start_pos + 1
    end_of_line_success = end_of_line(string, start_pos)
    if end_of_line_success:
        return True, end_of_line_success[1]

@memoize
def end_of_line(string, start_pos):
    if string[start_pos:start_pos + 2] == '\r\n':
        return True, start_pos + 2
    if string[start_pos:start_pos + 1] == '\n':
        return True, start_pos + 1
    if string[start_pos:start_pos + 1] == '\r':
        return True, start_pos + 1


def end_of_file(string, start_pos):
    if len(string) <= start_pos:
        return True, start_pos
