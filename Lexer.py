import sys
import enum


class Token:
    """
    This class contains the definition of Tokens. A token has two fields: its
    text and its kind. The "kind" of a token is a constant that identifies it
    uniquely. See the TokenType to know the possible identifiers (if you want).
    You don't need to change this class.
    """

    def __init__(self, tokenText, tokenKind):
        # The token's actual text. Used for identifiers, strings, and numbers.
        self.text = tokenText
        # The TokenType that this token is classified as.
        self.kind = tokenKind

    def __repr__(self):
        return self.text


class TokenType(enum.Enum):
    """
    These are the possible tokens. You don't need to change this class at all.
    """
    EOF = -1  # End of file
    NLN = 0   # New line
    WSP = 1   # White Space
    COM = 2   # Comment
    NUM = 3   # Number (integers)
    STR = 4   # Strings
    TRU = 5   # The constant true
    FLS = 6   # The constant false
    VAR = 7   # An identifier
    LET = 8   # The 'let' of the let expression
    INX = 9   # The 'in' of the let expression
    END = 10  # The 'end' of the let expression
    EQL = 201  # x = y
    ADD = 202  # x + y
    SUB = 203  # x - y
    MUL = 204  # x * y
    DIV = 205  # x / y
    LEQ = 206  # x <= y
    LTH = 207  # x < y
    NEG = 208  # ~x
    NOT = 209  # not x
    LPR = 210  # (
    RPR = 211  # )
    ASN = 212  # The assignment '<-' operator
    ORX = 213  # x or y
    AND = 214  # x and y
    IFX = 215  # The 'if' of a conditional expression
    THN = 216  # The 'then' of a conditional expression
    ELS = 217  # The 'else' of a conditional expression
    FNX = 218  # The 'fn' that declares an anonymous function
    ARW = 219  # The '=>' that separates the parameter from the body of function


class Lexer:
    var_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    whitespace_characters = " \t\r"

    def __init__(self, source):
        if source is None or source == "":
            raise ValueError("Source cannot be None or empty")

        self.source = source
        self.cur_pos = 0
        self.length = len(source)
        self.buffer = ""
        self.state_table = self.state_table()

    def consumeChar(self):
        if self.cur_pos >= self.length:
            return None

        cur_char = self.source[self.cur_pos]
        self.buffer += cur_char
        self.cur_pos += 1
        return cur_char

    def getChar(self):
        if self.cur_pos >= self.length:
            return None

        return self.source[self.cur_pos]

    def state_table(self):
        return {
            "start": {
                "\n": self.state_NLN,
                " ": self.state_WSP,
                "\t": self.state_WSP,
                "\r": self.state_WSP,
                "=": self.state_eql_or_arw,
                "+": self.state_ADD,
                "*": self.state_MUL,
                "/": self.state_DIV,
                "~": self.state_NEG,
                ")": self.state_RPR,
                "-": self.state_single_comment_or_sub,
                "(": self.state_left_parenthesis_or_full_comment,
                "<": self.state_less_eq_or_assign,
                "n": self.state_not0,
                "t": self.state_true_or_then,
                "f": self.state_false_or_fn,
                "l": self.state_let0,
                "e": self.state_end_or_else,
                "o": self.state_or0,
                "a": self.state_and0,
                "i": self.state_in_or_if,
                "0": self.state_zero,
                "1": self.state_integer,
                "2": self.state_integer,
                "3": self.state_integer,
                "4": self.state_integer,
                "5": self.state_integer,
                "6": self.state_integer,
                "7": self.state_integer,
                "8": self.state_integer,
                "9": self.state_integer,
                "else": self.state_variable
            },
            "state_eql_or_arw": {
                ">": self.state_ARW,
                "else": self.state_EQL,
            },
            "state_let0": {
                "e": self.state_let1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_let1": {
                "t": self.state_let2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_let2": {
                " ": self.state_LET,
                "\n": self.state_LET,
                "\t": self.state_LET,
                "\r": self.state_LET,
                "else": self.state_variable,
            },
            "state_and0": {
                "n": self.state_and1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_and1": {
                "d": self.state_and2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_and2": {
                "(": self.state_AND,
                " ": self.state_AND,
                "\n": self.state_AND,
                "\t": self.state_AND,
                "\r": self.state_AND,
                "else": self.state_variable,
            },
            "state_or0": {
                "r": self.state_or1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_or1": {
                "(": self.state_ORX,
                " ": self.state_ORX,
                "\n": self.state_ORX,
                "\t": self.state_ORX,
                "\r": self.state_ORX,
                "else": self.state_variable,
            },
            "state_end_or_else": {
                "n": self.state_end1,
                "l": self.state_else1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_end1": {
                "d": self.state_end2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_end2": {
                "(": self.state_END,
                ")": self.state_END,
                " ": self.state_END,
                "\n": self.state_END,
                "\t": self.state_END,
                "\r": self.state_END,
                "else": self.state_variable,
            },
            "state_else1": {
                "s": self.state_else2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_else2": {
                "e": self.state_else3,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_else3": {
                "(": self.state_ELS,
                " ": self.state_ELS,
                "\n": self.state_ELS,
                "\t": self.state_ELS,
                "\r": self.state_ELS,
                "else": self.state_variable,
            },
            "state_in_or_if": {
                "n": self.state_in1,
                "f": self.state_if1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_in1": {
                "(": self.state_INX,
                " ": self.state_INX,
                "\n": self.state_INX,
                "\t": self.state_INX,
                "\r": self.state_INX,
                "else": self.state_variable,
            },
            "state_if1": {
                "(": self.state_IFX,
                " ": self.state_IFX,
                "\n": self.state_IFX,
                "\t": self.state_IFX,
                "\r": self.state_IFX,
                "else": self.state_variable,
            },
            "state_single_comment_or_sub": {
                "-": self.state_single_comment1,
                "else": self.state_SUB,
            },
            "state_single_comment1": {
                "\n": self.state_single_COM,
                "else": self.state_single_comment1,
            },
            "state_full_comment1": {
                "*": self.state_full_comment2,
                "else": self.state_full_comment1,
            },
            "state_full_comment2": {
                ")": self.state_full_COM,
                "*": self.state_full_comment2,
                "else": self.state_full_comment1,
            },
            "state_left_parenthesis_or_full_comment": {
                "*": self.state_full_comment1,
                "else": self.state_LPR,
            },
            "state_less_eq_or_assign": {
                "=": self.state_LEQ,
                "-": self.state_ASN,
                "else": self.state_LTH,
            },
            "state_not0": {
                "o": self.state_not1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_not1": {
                "t": self.state_not2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_not2": {
                "(": self.state_NOT,
                " ": self.state_NOT,
                "\n": self.state_NOT,
                "\t": self.state_NOT,
                "\r": self.state_NOT,
                "else": self.state_variable,
            },
            "state_true_or_then": {
                "r": self.state_true1,
                "h": self.state_then1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_true1": {
                "u": self.state_true2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_true2": {
                "e": self.state_true3,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_true3": {
                "(": self.state_TRU,
                ")": self.state_TRU,
                " ": self.state_TRU,
                "\n": self.state_TRU,
                "\t": self.state_TRU,
                "\r": self.state_TRU,
                "else": self.state_variable,
            },
            "state_then1": {
                "e": self.state_then2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_then2": {
                "n": self.state_then3,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_then3": {
                "(": self.state_THN,
                " ": self.state_THN,
                "\n": self.state_THN,
                "\t": self.state_THN,
                "\r": self.state_THN,
                "else": self.state_variable,
            },
            "state_false_or_fn": {
                "a": self.state_false1,
                "n": self.state_fn1,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_false1": {
                "l": self.state_false2,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_false2": {
                "s": self.state_false3,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_false3": {
                "e": self.state_false4,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_variable,
            },
            "state_false4": {
                "(": self.state_FLS,
                ")": self.state_FLS,
                " ": self.state_FLS,
                "\n": self.state_FLS,
                "\t": self.state_FLS,
                "\r": self.state_FLS,
                "else": self.state_variable,
            },
            "state_fn1": {
                " ": self.state_FNX,
                "\n": self.state_FNX,
                "\t": self.state_FNX,
                "\r": self.state_FNX,
                "else": self.state_variable,
            },
            "state_zero": {
                "0": self.state_octal,
                "1": self.state_octal,
                "2": self.state_octal,
                "3": self.state_octal,
                "4": self.state_octal,
                "5": self.state_octal,
                "6": self.state_octal,
                "7": self.state_octal,
                "x": self.state_hexadecimal,
                "X": self.state_hexadecimal,
                "b": self.state_binary,
                "B": self.state_binary,
                "else": self.state_INT,
            },
            "state_octal": {
                "0": self.state_octal,
                "1": self.state_octal,
                "2": self.state_octal,
                "3": self.state_octal,
                "4": self.state_octal,
                "5": self.state_octal,
                "6": self.state_octal,
                "7": self.state_octal,
                "else": self.state_OCT,
            },
            "state_hexadecimal": {
                "0": self.state_hexadecimal,
                "1": self.state_hexadecimal,
                "2": self.state_hexadecimal,
                "3": self.state_hexadecimal,
                "4": self.state_hexadecimal,
                "5": self.state_hexadecimal,
                "6": self.state_hexadecimal,
                "7": self.state_hexadecimal,
                "8": self.state_hexadecimal,
                "9": self.state_hexadecimal,
                "a": self.state_hexadecimal,
                "b": self.state_hexadecimal,
                "c": self.state_hexadecimal,
                "d": self.state_hexadecimal,
                "e": self.state_hexadecimal,
                "f": self.state_hexadecimal,
                "A": self.state_hexadecimal,
                "B": self.state_hexadecimal,
                "C": self.state_hexadecimal,
                "D": self.state_hexadecimal,
                "E": self.state_hexadecimal,
                "F": self.state_hexadecimal,
                "else": self.state_HEX,
            },
            "state_binary": {
                "0": self.state_binary,
                "1": self.state_binary,
                "else": self.state_BIN,
            },
            "state_integer": {
                "0": self.state_integer,
                "1": self.state_integer,
                "2": self.state_integer,
                "3": self.state_integer,
                "4": self.state_integer,
                "5": self.state_integer,
                "6": self.state_integer,
                "7": self.state_integer,
                "8": self.state_integer,
                "9": self.state_integer,
                "else": self.state_INT,
            },
            "state_variable": {
                "continue": self.state_variable,
                "(": self.state_VAR,
                ")": self.state_VAR,
                " ": self.state_VAR,
                "\n": self.state_VAR,
                "\t": self.state_VAR,
                "\r": self.state_VAR,
                "else": self.state_VAR,
            },
        }

    def state_NLN(self):
        self.consumeChar()
        return "start", None, Token("\n", TokenType.NLN)

    def state_WSP(self):
        self.consumeChar()
        return "start", None, Token(" ", TokenType.WSP)

    def state_EQL(self):
        return "start", None, Token("=", TokenType.EQL)

    def state_FNX(self):
        return "start", None, Token("fn", TokenType.FNX)

    def state_ARW(self):
        self.consumeChar()
        return "start", None, Token("=>", TokenType.ARW)

    def state_ADD(self):
        self.consumeChar()
        return "start", None, Token("+", TokenType.ADD)

    def state_SUB(self):
        return "start", None, Token("-", TokenType.SUB)

    def state_MUL(self):
        self.consumeChar()
        return "start", None, Token("*", TokenType.MUL)

    def state_DIV(self):
        self.consumeChar()
        return "start", None, Token("/", TokenType.DIV)

    def state_NEG(self):
        self.consumeChar()
        return "start", None, Token("~", TokenType.NEG)

    def state_LPR(self):
        return "start", None, Token("(", TokenType.LPR)

    def state_RPR(self):
        self.consumeChar()
        return "start", None, Token(")", TokenType.RPR)

    def state_single_COM(self):
        comment = f"--{self.buffer}"
        return "start", None, Token(comment, TokenType.COM)

    def state_full_COM(self):
        self.consumeChar()
        comment = f"(*{self.buffer}*)"
        return "start", None, Token(comment, TokenType.COM)

    def state_LEQ(self):
        self.consumeChar()
        return "start", None, Token("<=", TokenType.LEQ)

    def state_LTH(self):
        return "start", None, Token("<", TokenType.LTH)

    def state_LET(self):
        return "start", None, Token("let", TokenType.LET)

    def state_AND(self):
        return "start", None, Token("and", TokenType.AND)

    def state_ORX(self):
        return "start", None, Token("or", TokenType.ORX)

    def state_END(self):
        return "start", None, Token("end", TokenType.END)

    def state_ELS(self):
        return "start", None, Token("else", TokenType.ELS)

    def state_INX(self):
        return "start", None, Token("in", TokenType.INX)

    def state_IFX(self):
        return "start", None, Token("if", TokenType.IFX)

    def state_NOT(self):
        return "start", None, Token("not", TokenType.NOT)

    def state_TRU(self):
        return "start", None, Token("true", TokenType.TRU)

    def state_THN(self):
        return "start", None, Token("then", TokenType.THN)

    def state_FLS(self):
        return "start", None, Token("false", TokenType.FLS)

    def state_FNX(self):
        return "start", None, Token("fn", TokenType.FNX)

    def state_INT(self):
        number = self.buffer
        return "start", None, Token(number, TokenType.NUM)

    def state_OCT(self):
        number = self.buffer
        return "start", None, Token(number, TokenType.OCT)

    def state_HEX(self):
        number = self.buffer
        return "start", None, Token(number, TokenType.HEX)

    def state_BIN(self):
        number = self.buffer
        return "start", None, Token(number, TokenType.BIN)

    def state_VAR(self):
        var = self.buffer
        return "start", None, Token(var, TokenType.VAR)

    def state_ASN(self):
        self.consumeChar()
        return "start", None, Token("<-", TokenType.ASN)

    def state_eql_or_arw(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_eql_or_arw"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_single_comment_or_sub(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_single_comment_or_sub"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_single_comment1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_single_comment1"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_left_parenthesis_or_full_comment(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_left_parenthesis_or_full_comment"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_full_comment1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_full_comment1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_full_comment2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_full_comment2"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_less_eq_or_assign(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_less_eq_or_assign"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_let0(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_let0"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_let1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_let1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_let2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_let2"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_and0(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_and0"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_and1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_and1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_and2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_and2"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_or0(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_or0"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_or1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_or1"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_end_or_else(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_end_or_else"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_end1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_end1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_end2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_end2"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_else1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_else1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_else2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_else2"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_else3(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_else3"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_in_or_if(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_in_or_if"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_in1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_in1"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_if1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_if1"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_not0(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_not0"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_not1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_not1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_not2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_not2"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_true_or_then(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_true_or_then"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_true1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_true1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_true2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_true2"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_true3(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_true3"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_then1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_then1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_then2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_then2"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_then3(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_then3"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_false_or_fn(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_false_or_fn"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_false1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_false1"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_false2(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_false2"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_false3(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_false3"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_false4(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_false4"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_fn1(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_fn1"
        if cur_char is None:
            return self_state, "\n", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None


    def state_zero(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_zero"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_octal(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_octal"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_hexadecimal(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_hexadecimal"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_binary(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_binary"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_integer(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_integer"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None
        
        return self_state, "else", None

    def state_variable(self):
        self.consumeChar()
        cur_char = self.getChar()
        self_state = "state_variable"
        if cur_char is None:
            return self_state, "else", None
        if cur_char in Lexer.var_characters:
            return self_state, "continue", None
        if cur_char in self.state_table[self_state]:
            return self_state, cur_char, None

        return self_state, "else", None

    def dispatch(self, state, input_state):
        if input_state is None and self.cur_pos >= self.length:
            return None, None, Token("", TokenType.EOF)

        if input_state is None:
            cur_char = self.getChar()
            if cur_char in self.state_table[state]:
                action = self.state_table[state][cur_char]
            else:
                action = self.state_table[state]["else"]
        else:
            action = self.state_table[state][input_state]

        return action()

    def state_error(self):
        raise ValueError(
            f"Unexpected character '{self.source[self.cur_pos]}' at position {self.cur_pos}")

    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Examples:

        >>> l = Lexer("1 + 3")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2 -- 3\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer("1 + var")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.VAR: 7>]

        >>> l = Lexer("let v <- 2 in v end")
        >>> [tk.kind.name for tk in l.tokens()]
        ['LET', 'VAR', 'ASN', 'NUM', 'INX', 'VAR', 'END']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if (
                token.kind != TokenType.WSP
                and token.kind != TokenType.COM
                and token.kind != TokenType.NLN
            ):
                yield token
            token = self.getToken()

    def getToken(self):
        state = 'start'
        input_state = None
        while state:
            state, input_state, token = self.dispatch(state, input_state)
            if token:
                self.buffer = ""
                return token