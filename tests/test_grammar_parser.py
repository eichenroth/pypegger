import pytest

from pegger import grammar_parser


def test_end_of_file():
    string = ''
    assert grammar_parser.end_of_file(string, 0)
    assert grammar_parser.end_of_file(string, 5)

    string = 'hello'
    assert not grammar_parser.end_of_file(string, 0)
    assert not grammar_parser.end_of_file(string, 1)
    end_of_file_success = grammar_parser.end_of_file(string, 5)
    assert end_of_file_success
    assert end_of_file_success[1] == 5

def test_end_of_line():
    assert not grammar_parser.end_of_line('', 0)

    string = 'hello\nhello'
    end_of_line_success = grammar_parser.end_of_line(string, 5)
    assert end_of_line_success
    assert end_of_line_success[1] == 6

    assert not grammar_parser.end_of_line(string, 11)
    assert not grammar_parser.end_of_line(string, 4)

def test_space():
    string = 'abc abc\t'

    space_success = grammar_parser.space(string, 3)
    assert space_success
    assert space_success[1] == 4

    space_success = grammar_parser.space(string, 7)
    assert space_success
    assert space_success[1] == 8

    assert not grammar_parser.space(string, 0)

def test_comment():
    string = '# this is /com\\ment\nand a newline'
    assert grammar_parser.comment(string, 0)[1] == 20

    assert not grammar_parser.comment(string, 1)
    assert not grammar_parser.comment(string, 20)

    string = '# this is /com\\ment\r\nand a newline'
    assert grammar_parser.comment(string, 0)[1] == 21

    string = 'no comment#comment'
    assert grammar_parser.comment(string, 10)[1] == 18

def test_spacing():
    string = 'this is\ta \t\t test string   #with comment'
    assert grammar_parser.spacing(string, 0)[1] == 0
    assert grammar_parser.spacing(string, 4)[1] == 5
    assert grammar_parser.spacing(string, 7)[1] == 8
    assert grammar_parser.spacing(string, 9)[1] == 13
    assert grammar_parser.spacing(string, 17)[1] == 18
    assert grammar_parser.spacing(string, 24)[1] == 40

def test_substring():
    string = 'string with substring'
    assert grammar_parser.substring(string, 0, 'str')[1] == 3
    assert grammar_parser.substring(string, 0, 'string')[1] == 7
    assert not grammar_parser.substring(string, 6, 'with')
    assert grammar_parser.substring(string, 7, 'with')[1] == 12
    assert grammar_parser.substring(string, 12, 'substring')[1] == 21

def test_char():
    string = 'test\\n\\r\\"'
    assert grammar_parser.char(string, 0)[1] == 1
    assert grammar_parser.char(string, 4)[1] == 6
    assert grammar_parser.char(string, 6)[1] == 8
    assert grammar_parser.char(string, 8)[1] == 10
    assert not grammar_parser.char(string, 10)

def test_range():
    string = 'a b-g A-Z '
    assert grammar_parser.range_(string, 0)[1] == 1
    assert grammar_parser.range_(string, 1)[1] == 2
    assert grammar_parser.range_(string, 2)[1] == 5
    assert grammar_parser.range_(string, 6)[1] == 9

def test_class():
    string = 'test[a][ac-d][A-Z1-9] \t [A-Eabc]'
    assert not grammar_parser.class_(string, 0)
    assert grammar_parser.class_(string, 4)[1] == 7
    assert grammar_parser.class_(string, 7)[1] == 13
    assert grammar_parser.class_(string, 13)[1] == 24
    assert grammar_parser.class_(string, 24)[1] == 32

def test_literal():
    string = 'test "teststring \' test \\"" \'test\\\' "" \''
    assert not grammar_parser.literal(string, 0)
    assert not grammar_parser.literal(string, 4)
    assert grammar_parser.literal(string, 5)[1] == 28
    assert grammar_parser.literal(string, 28)[1] == 40

def test_identifier():
    string = '<test> <Test123>\t<123Test> <___abc> <123_test> <_> <Test test>'
    assert grammar_parser.identifier(string, 0)[1] == 7
    assert not grammar_parser.identifier(string, 1)
    assert grammar_parser.identifier(string, 7)[1] == 17
    assert not grammar_parser.identifier(string, 17)
    assert grammar_parser.identifier(string, 27)[1] == 36
    assert not grammar_parser.identifier(string, 36)
    assert grammar_parser.identifier(string, 47)[1] == 51
    assert not grammar_parser.identifier(string, 51)

def test_primary():
    string = '<Test> <_test123> "string\n " <ident>     := [12345] ([1-4][1-9]) .  '
    assert grammar_parser.primary(string, 0)[1] == 7
    assert not grammar_parser.primary(string, 1)
    assert grammar_parser.primary(string, 7)[1] == 18
    assert grammar_parser.primary(string, 18)[1] == 29
    assert not grammar_parser.primary(string, 29)
    assert grammar_parser.primary(string, 44)[1] == 52
    assert grammar_parser.primary(string, 52)[1] == 65
    assert grammar_parser.primary(string, 65)[1] == 68

def test_suffix():
    string = '[0]* .+ "string"? <Test> <123test>'
    assert grammar_parser.suffix(string, 0)[1] == 5
    assert grammar_parser.suffix(string, 5)[1] == 8
    assert grammar_parser.suffix(string, 8)[1] == 18
    assert grammar_parser.suffix(string, 18)[1] == 25
    assert not grammar_parser.suffix(string, 25)
    assert not grammar_parser.suffix(string, 7)
    assert not grammar_parser.suffix(string, 10)

def test_prefix():
    string = '!     <test> &"2" !test <Test>? !<test>+'
    assert grammar_parser.prefix(string, 0)[1] == 13
    assert grammar_parser.prefix(string, 13)[1] == 18
    assert not grammar_parser.prefix(string, 18)
    assert grammar_parser.prefix(string, 24)[1] == 32
    assert grammar_parser.prefix(string, 32)[1] == 40

def test_sequence():
    string = '[123]<String>  "test" <1> := <String> [5-78-9] /\t<test>'
    assert grammar_parser.sequence(string, 0)[1] == 22
    assert grammar_parser.sequence(string, 22)[1] == 22
    assert grammar_parser.sequence(string, 23)[1] == 23
    assert grammar_parser.sequence(string, 26)[1] == 26
    assert grammar_parser.sequence(string, 29)[1] == 47
    assert grammar_parser.sequence(string, 47)[1] == 47
    assert grammar_parser.sequence(string, 48)[1] == 48
    assert grammar_parser.sequence(string, 49)[1] == 55

def test_expression():
    string = '[123]<String>  "test" <1> := <String> [5-78-9] /\t<test>     '
    assert grammar_parser.expression(string, 0)[1] == 22
    assert grammar_parser.expression(string, 29)[1] == 60
    assert grammar_parser.expression(string, 1)[1] == 1
    assert grammar_parser.expression(string, 49)[1] == 60

def test_definition():
    string = '<A> := "string" / (<B>? <C>\t<abc>)+'
    assert grammar_parser.definition(string, 0)[1] == len(string)
    assert not grammar_parser.definition(string, 7)

    string = '<B>     := \n\n\r\n\t <b> <a> 123'
    assert grammar_parser.definition(string, 0)[1] == len(string) - 3

def test_grammar():
    string = '<A> := "a" <A> "b" / ""\n' \
             '<B> := "b" <B> "c" / ""\n' \
             '<D> := &(<A>!"b")"a"*<B>!.'

    assert grammar_parser.grammar(string, 0)[1] == len(string)
