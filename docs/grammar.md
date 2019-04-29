# Grammar

## Examples

### Well-formed Brackets

_Plain Python Definition_

    from pegger import *
    
    brackets = RuleAlias('Brackets')
    round = RuleAlias('Round')
    curly = RuleAlias('Curly')
    square = RuleAlias('Square')
    
    brackets.rule = ZeroOrMore(Choices(round, curly, square))
    round.rule = Sequence('(', brackets, ')')
    curly.rule = Sequence('{', brackets, '}')
    square.rule = Sequence('[', brackets, ']')
    
    brackets.match_whole('()({}[{}{}])({})') # Checks if the whole string matches the grammar.
    brackets.match('()({}[{}{}])({})') # Checks if a prefix of the string matches the grammar.
    brackets.parse('()({}[{}{}])({})') # Parses the string into a syntax tree.

_Textual definition_  
Consider the variable `string` defined as:

    <Brackets> := (<Round> / <Curly> / <Square>)*
    <Round> := "(" <Brackets> ")"
    <Curly> := "{" <Brackets> "}"
    <Square> := "[" <Brackets> "]"

We can use the `generate_grammar` function.

    from pegger.grammar_parser import generate_grammar

    grammar = generate_grammar(string)

    brackets.match_whole('()({}[{}{}])({})') # Checks if the whole string matches the grammar.
    brackets.match('()({}[{}{}])({})') # Checks if a prefix of the string matches the grammar.
    brackets.parse('()({}[{}{}])({})') # Parses the string into a syntax tree.

### {a<sup>n</sup>b<sup>n</sup>c<sup>n</sup> | n ∈ ℕ}
    
    grammar = RuleAlias('Grammar')
    A = RuleAlias('A')
    B = RuleAlias('B')

    grammar.rule = Choices(Not(Any()), Sequence(And(Sequence(A, Not('b'))), ZeroOrMore('a'), B, Not(Any())))
    A.rule = Choices(Sequence('a', A, 'b'), 'ab')
    B.rule = Choices(Sequence('b', B, 'c'), 'bc')

    grammar.match_whole('aaabbbccc')

As seen in the first example you also can use a grammar definition as string

    <Grammar> := !. / &(<A>!"b")"a"*<B>!.
    <A> := "a" <A> "b" / "ab"
    <B> := "b" <B> "c" / "bc"

## Rules

| Rule | String Definition | Python Definition
| --- | --- | --- |
| String | `"abc"`, `'abc'` | `String('abc')`, `'abc'` |
| Character class | `[a-z0-9]` | Choices(Range('a', 'z'), Range('0', '9')) |
| Any | `.` | `Any()` |
| Optional | `<A>?` | `Optional(A)` |
| Zero-or-more | `<A>*` | `ZeroOrMore(A)` |
| One-or-more | `<A>+` | `OneOrMore(A)` |
| And | `&<A>` | `And(A)` |
| Not | `!<A>` | `Not(A)` |
| Sequence | `<First> <Second> 'string' <Fourth>` | `Sequence(first, second, 'string', fourth)` |
| Choices | `<First> / <Second> / 'string' / <Fourth>` | `Choices(first, second, 'string', fourth)` |

## The Grammar

The grammar can be defined using its own syntax. The grammar is defined very closely to the grammar of [the first PEG pager by Bryan Ford](https://dl.acm.org/citation.cfm?id=964011).

    # Hierarchical syntax
    Grammar     := Spacing Definition+ EndOfFile
    Definition  := Identifier ASSIGN Expression
    Expression  := Sequence (SLASH Sequence)*
    Sequence    := Prefix*
    Prefix      := (AND / NOT)? Suffix
    Suffix      := Primary (QUESTION / STAR / PLUS)?
    Primary     := Identifier !ASSIGN
                   / OPEN Expression CLOSE
                   / Literal
                   / Class
                   / DOT

    # Lexical syntax
    Identifier  := '<' IdentStart IdentCont* '>' Spacing
    IdentStart  := [a-zA-Z_]
    IdentCont   := IdentStart / [0-9]
    Literal     := ['] (!['] Char)* ['] Spacing
                   / ["] (!["] Char)* ["] Spacing
    Class       := '[' (!']' Range)* ']' Spacing
    Range       := Char '-' Char / Char
    Char        := '\\' [nrt'"\[\]\\]
                   / !'\\' .
    ASSIGN      := ':=' Spacing
    SLASH       := '/' Spacing
    AND         := '&' Spacing
    NOT         := '!' Spacing
    QUESTION    := '?' Spacing
    STAR        := '*' Spacing
    PLUS        := '+' Spacing
    OPEN        := '(' Spacing
    CLOSE       := ')' Spacing
    DOT         := '.' Spacing
    Spacing     := (Space / Comment)*
    Comment     := '#' (!(EndOfLine / EndOfFile) .)* EndOfLine
    Space       := ' ' / '\t' / EndOfLine
    EndOfLine   := '\r\n' / '\n' / '\r'
    EndOfFile   := !.
