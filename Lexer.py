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


class Lexer:

    var_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    def __init__(self, source):
        if source is None or source == "":
            raise ValueError("Source cannot be None or empty")

        self.source = source
        self.cur_pos = 0
        self.length = len(source)
        self.buffer = ""
        self.state_table = self.state_table()

    def state_table(self):
        return {
            "start": {
                "\n": self.state_NLN,
                " ": self.state_WSP,
                "=": self.state_EQL,
                "+": self.state_ADD,
                "*": self.state_MUL,
                "/": self.state_DIV,
                "~": self.state_NEG,
                ")": self.state_RPR,
                "-": self.state_single_comment0,
                "(": self.state_left_parenthesis,
                "<": self.state_less_eq_or_assign,
                "n": self.state_not0,
                "t": self.state_true0,
                "f": self.state_false0,
                "l": self.state_let0,
                "e": self.state_end0,
                "o": self.state_or0,
                "a": self.state_and0,
                "i": self.state_in0,
                "0": self.state_zero,
                "digit_not_zero": self.state_integer,
                "alpha": self.state_variable,
                "else": self.state_error
            },
            "state_let0": {
                "e": self.state_let1,
                "var": self.state_variable,
            },
            "state_let1": {
                "t": self.state_let2,
                "var": self.state_variable,
            },
            "state_let2": {
                "var": self.state_variable,
                "else": self.state_LET,
            },
            "state_and0": {
                "n": self.state_and1,
                "var": self.state_variable,
            },
            "state_and1": {
                "d": self.state_and2,
                "var": self.state_variable,
            },
            "state_and2": {
                "var": self.state_variable,
                "else": self.state_AND,
            },
            "state_or0": {
                "r": self.state_or1,
                "var": self.state_variable,
            },
            "state_or1": {
                "var": self.state_variable,
                "else": self.state_ORX,
            },
            "state_end0": {
                "n": self.state_end1,
                "l": self.state_else0,
                "var": self.state_variable,
            },
            "state_end1": {
                "d": self.state_end2,
                "var": self.state_variable,
            },
            "state_end2": {
                "var": self.state_variable,
                "else": self.state_END,
            },
            "state_else0": {
                "s": self.state_else1,
                "var": self.state_variable,
            },
            "state_else1": {
                "e": self.state_else2,
                "var": self.state_variable,
            },
            "state_else2": {
                "var": self.state_variable,
                "else": self.state_ELS,
            },
            "state_in0": {
                "n": self.state_in1,
                "f": self.state_if0,
                "var": self.state_variable,
            },
            "state_in1": {
                "var": self.state_variable,
                "else": self.state_IN,
            },
            "state_if0": {
                "var": self.state_variable,
                "else": self.state_IF,
            },
            "state_single_comment0": {
                "-": self.state_single_comment1,
                "else": self.state_SUB,
            },
            "state_single_comment1": {
                "\n": self.state_single_COM,
                "else": self.state_single_comment1,
            },
            "state_full_comment0": {
                "*": self.state_full_comment1,
                "else": self.state_full_comment0,
            },
            "state_full_comment1": {
                ")": self.state_full_COM,
                "*": self.state_full_comment1,
                "else": self.state_full_comment0,
            },
            "state_left_parenthesis": {
                "*": self.state_full_comment0,
                "else": self.state_LPR,
            },
            "state_less_eq": {
                "=": self.state_LEQ,
                "-": self.state_ASN,
                "else": self.state_LTH,
            },
            "state_not0": {
                "o": self.state_not1,
                "var": self.state_variable,
            },
            "state_not1": {
                "t": self.state_not2,
                "var": self.state_variable,
            },
            "state_not2": {
                "var": self.state_variable,
                "else": self.state_NOT,
            },
            "state_true0": {
                "r": self.state_true1,
                "h": self.state_then0,
                "var": self.state_variable,
            },
            "state_true1": {
                "u": self.state_true2,
                "var": self.state_variable,
            },
            "state_true2": {
                "e": self.state_true3,
                "var": self.state_variable,
            },
            "state_true3": {
                "var": self.state_variable,
                "else": self.state_TRU,
            },

            "state_then0": {
                "e": self.state_then1,
                "var": self.state_variable,
            },
            "state_then1": {
                "n": self.state_then2,
                "var": self.state_variable,
            },
            "state_then2": {
                "var": self.state_variable,
                "else": self.state_THN,
            },
            "state_false0": {
                "a": self.state_false1,
                "var": self.state_variable,
            },
            "state_false1": {
                "l": self.state_false2,
                "var": self.state_variable,
            },
            "state_false2": {
                "s": self.state_false3,
                "var": self.state_variable,
            },
            "state_false3": {
                "e": self.state_false4,
                "var": self.state_variable,
            },
            "state_false4": {
                "var": self.state_variable,
                "else": self.state_FLS,
            },
            "state_zero": {
                "0-7": self.state_octal,
                "x|X": self.state_hexadecimal,
                "b|B": self.state_binary,
                "else": self.state_INT,
            },
            "state_octal": {
                "0-7": self.state_octal,
                "else": self.state_OCT,
            },
            "state_hexadecimal": {
                "0-9|a-f|A-F": self.state_hexadecimal,
                "else": self.state_HEX,
            },
            "state_binary": {
                "0|1": self.state_binary,
                "else": self.state_BIN,
            },
            "state_integer": {
                "0-9": self.state_integer,
                "else": self.state_INT,
            },
            "state_variable": {
                "var_characters": self.state_variable,
                "else": self.state_VAR,
            }
        }

    def state_NLN(self):
        self.cur_pos += 1
        return "start", None, Token("\n", TokenType.NLN)

    def state_WSP(self):
        self.cur_pos += 1
        return "start", None, Token(" ", TokenType.WSP)

    def state_EQL(self):
        self.cur_pos += 1
        return "start", None, Token("=", TokenType.EQL)

    def state_ADD(self):
        self.cur_pos += 1
        return "start", None, Token("+", TokenType.ADD)

    def state_SUB(self):
        self.cur_pos += 1
        return "start", None, Token("-", TokenType.SUB)

    def state_MUL(self):
        self.cur_pos += 1
        return "start", None, Token("*", TokenType.MUL)

    def state_DIV(self):
        self.cur_pos += 1
        return "start", None, Token("/", TokenType.DIV)

    def state_NEG(self):
        self.cur_pos += 1
        return "start", None, Token("~", TokenType.NEG)

    def state_LPR(self):
        self.cur_pos += 1
        return "start", None, Token("(", TokenType.LPR)

    def state_RPR(self):
        self.cur_pos += 1
        return "start", None, Token(")", TokenType.RPR)

    def state_single_COM(self):
        self.cur_pos += 1
        comment = f"--{self.buffer}"
        self.buffer = ""
        return "start", None, Token(comment, TokenType.COM)

    def state_full_COM(self):
        self.cur_pos += 1
        comment = f"(*{self.buffer})"
        self.buffer = ""
        return "start", None, Token(comment, TokenType.COM)

    def state_LEQ(self):
        self.cur_pos += 1
        return "start", None, Token("<=", TokenType.LEQ)

    def state_LTH(self):
        self.cur_pos += 1
        return "start", None, Token("<", TokenType.LTH)

    def state_LET(self):
        self.cur_pos += 1
        return "start", None, Token("let", TokenType.LET)
    
    def state_AND(self):
        self.cur_pos += 1
        return "start", None, Token("and", TokenType.AND)
    
    def state_ORX(self):
        self.cur_pos += 1
        return "start", None, Token("or", TokenType.ORX)

    def state_END(self):
        self.cur_pos += 1
        return "start", None, Token("end", TokenType.END)

    def state_ELS(self):
        self.cur_pos += 1
        return "start", None, Token("else", TokenType.ELS)

    def state_IN(self):
        self.cur_pos += 1
        return "start", None, Token("in", TokenType.INX)

    def state_IF(self):
        self.cur_pos += 1
        return "start", None, Token("if", TokenType.IFX)

    def state_NOT(self):
        self.cur_pos += 1
        return "start", None, Token("not", TokenType.NOT)

    def state_TRU(self):
        self.cur_pos += 1
        return "start", None, Token("true", TokenType.TRU)

    def state_THN(self):
        self.cur_pos += 1
        return "start", None, Token("then", TokenType.THN)

    def state_FLS(self):
        self.cur_pos += 1
        return "start", None, Token("false", TokenType.FLS)

    def state_INT(self):
        self.cur_pos += 1
        number = self.buffer
        self.buffer = ""
        return "start", None, Token(number, TokenType.NUM)

    def state_OCT(self):
        self.cur_pos += 1
        number = self.buffer
        self.buffer = ""
        return "start", None, Token(number, TokenType.OCT)

    def state_HEX(self):
        self.cur_pos += 1
        number = self.buffer
        self.buffer = ""
        return "start", None, Token(number, TokenType.HEX)

    def state_BIN(self):
        self.cur_pos += 1
        number = self.buffer
        self.buffer = ""
        return "start", None, Token(number, TokenType.BIN)

    def state_VAR(self):
        self.cur_pos += 1
        var = self.buffer
        self.buffer = ""
        return "start", None, Token(var, TokenType.VAR)

    def state_ASN(self):
        self.cur_pos += 1
        return "start", None, Token("<-", TokenType.ASN)

    def state_single_comment0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_single_comment0", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "-":
            return "state_single_comment1", "else", None

        self.cur_pos -= 1
        return "state_single_comment0", "else", None

    def state_single_comment1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_single_comment1", "\n", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        self.buffer += cur_char
        if cur_char == "\n":
            self.cur_pos -= 1
            return "state_single_comment1", "\n", None

        return "state_single_comment1", "else", None

    def state_left_parenthesis(self):
        if self.cur_pos + 1 >= self.length:
            return "state_left_parenthesis", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "*":
            return "state_full_comment0", "else", None

        self.cur_pos -= 1
        return "state_left_parenthesis", "else", None

    def state_full_comment0(self):
        if self.cur_pos + 1 >= self.length:
            return "start", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        self.buffer += cur_char
        if cur_char == "*":
            return "state_full_comment1", "*", None

        return "state_full_comment0", "else", None

    def state_full_comment1(self):
        if self.cur_pos + 1 >= self.length:
            return "start", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == ")":
            return "state_full_comment1", ")", None

        self.buffer += cur_char
        if cur_char == "*":
            return "state_full_comment1", "*", None

        return "state_full_comment1", "else", None

    def state_less_eq_or_assign(self):
        if self.cur_pos + 1 >= self.length:
            return "state_less_eq", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "=":
            return "state_less_eq", "=", None
        if cur_char == "-":
            return "state_less_eq", "-", None

        self.cur_pos -= 1
        return "state_less_eq", "else", None

    def state_let0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_let0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "e":
            return "state_let0", "e", None

        if cur_char in Lexer.var_characters or cur_char.isspace():
            return "state_let0", "var", None

        return "start", "else", None

    def state_let1(self):
        if self.cur_pos + 1 >= self.length:
            return "start", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "t":
            return "state_let1", "t", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_let1", "var", None

        return "start", "else", None

    def state_let2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_let2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_let2", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_let2", "var", None

        return "start", "else", None
    
    def state_and0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_and0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "n":
            return "state_and0", "n", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_and0", "var", None

        return "start", "else", None

    def state_and1(self):
        if self.cur_pos + 1 >= self.length:
            return "start", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "d":
            return "state_and1", "d", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_and1", "var", None

        return "start", "else", None

    def state_and2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_and2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_and2", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_and2", "var", None

        return "start", "else", None
    
    def state_or0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_or0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "r":
            return "state_or0", "r", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_or0", "var", None

        return "start", "else", None


    def state_or1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_or1", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_or1", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_or1", "var", None

        return "start", "else", None

    def state_end0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_end0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "n" or cur_char == "l":
            return "state_end0", cur_char, None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_end0", "var", None

        return "start", "else", None

    def state_end1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_end1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "d":
            return "state_end1", "d", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_end1", "var", None

        return "start", "else", None

    def state_end2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_end2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_end2", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_end2", "var", None

        return "start", "else", None

    def state_else0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_else0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "s":
            return "state_else0", "s", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_else0", "var", None

        return "start", "else", None

    def state_else1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_else1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "e":
            return "state_else1", "e", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_else1", "var", None

        return "start", "else", None

    def state_else2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_else2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_else2", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_else2", "var", None

        return "start", "else", None

    def state_in0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_in0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "n" or cur_char == "f":
            return "state_in0", cur_char, None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_in0", "var", None

        return "start", "else", None

    def state_in1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_in1", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_in1", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_in1", "var", None

        return "start", "else", None

    def state_if0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_if0", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_if0", "else", None

        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_if0", "var", None

        return "start", "else", None

    def state_not0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_not0", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "o":
            return "state_not0", "o", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_not0", "var", None

        return "start", "else", None

    def state_not1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_not1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "t":
            return "state_not1", "t", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_not1", "var", None

        return "start", "else", None

    def state_not2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_not2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char == "(":
            return "state_not2", "else", None

        return "start", "else", None

    def state_true0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_true0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "r" or cur_char == "h":
            return "state_true0", cur_char, None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_true0", "var", None

        return "start", "else", None

    def state_true1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_true1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "u":
            return "state_true1", "u", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_true1", "var", None

        return "start", "else", None

    def state_true2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_true2", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "e":
            return "state_true2", "e", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_true2", "var", None

        return "start", "else", None

    def state_true3(self):
        if self.cur_pos + 1 >= self.length:
            return "state_true3", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char in "()":
            self.cur_pos -= 1
            return "state_true3", "else", None

        return "start", "else", None

    def state_then0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_then0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "e":
            return "state_then0", "e", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_then0", "var", None

        return "start", "else", None

    def state_then1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_then1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "n":
            return "state_then1", "n", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_then1", "var", None

        return "start", "else", None

    def state_then2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_then2", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char in "()":
            self.cur_pos -= 1
            return "state_then2", "else", None

        return "start", "else", None

    def state_false0(self):
        if self.cur_pos + 1 >= self.length:
            return "state_false0", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "a":
            return "state_false0", "a", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_false0", "var", None

        return "start", "else", None

    def state_false1(self):
        if self.cur_pos + 1 >= self.length:
            return "state_false1", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "l":
            return "state_false1", "l", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_false1", "var", None

        return "start", "else", None

    def state_false2(self):
        if self.cur_pos + 1 >= self.length:
            return "state_false2", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "s":
            return "state_false2", "s", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_false2", "var", None

        return "start", "else", None

    def state_false3(self):
        if self.cur_pos + 1 >= self.length:
            return "state_false3", "var", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char == "e":
            return "state_false3", "e", None
        
        if cur_char in Lexer.var_characters  or cur_char.isspace():
            return "state_false3", "var", None

        return "start", "else", None

    def state_false4(self):
        if self.cur_pos + 1 >= self.length:
            return "state_false4", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isspace() or cur_char in "()":
            self.cur_pos -= 1
            return "state_false4", "else", None

        return "start", "else", None

    def state_zero(self):
        self.buffer = "0"
        if self.cur_pos + 1 >= self.length:
            return "state_zero", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]

        if cur_char in "01234567":
            self.buffer += cur_char
            return "state_zero", "0-7", None
        elif cur_char in "xX":
            self.buffer += cur_char
            return "state_zero", "x|X", None
        elif cur_char in "bB":
            self.buffer += cur_char
            return "state_zero", "b|B", None
        elif cur_char.isalpha():
            return "start", "else", None

        self.cur_pos -= 1
        return "state_zero", "else", None

    def state_octal(self):
        if self.cur_pos + 1 >= self.length:
            return "state_octal", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char in "01234567":
            self.buffer += cur_char
            return "state_octal", "0-7", None
        if cur_char.isalpha():
            return "start", "else", None

        self.cur_pos -= 1
        return "state_octal", "else", None

    def state_hexadecimal(self):
        if self.cur_pos + 1 >= self.length:
            return "state_hexadecimal", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char in "0123456789abcdefABCDEF":
            self.buffer += cur_char
            return "state_hexadecimal", "0-9|a-f|A-F", None
        if cur_char.isalpha():
            return "start", "else", None

        self.cur_pos -= 1
        return "state_hexadecimal", "else", None

    def state_binary(self):
        if self.cur_pos + 1 >= self.length:
            return "state_binary", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char in "01":
            self.buffer += cur_char
            return "state_binary", "0|1", None
        if cur_char.isalpha():
            return "start", "else", None

        self.cur_pos -= 1
        return "state_binary", "else", None

    def state_integer(self):
        if self.cur_pos + 1 >= self.length:
            return "state_integer", "else", None

        self.cur_pos += 1
        cur_char = self.source[self.cur_pos]
        if cur_char.isdigit():
            self.buffer += cur_char
            return "state_integer", "0-9", None
        if cur_char.isalpha():
            return "start", "else", None

        self.cur_pos -= 1
        return "state_integer", "else", None

    def state_variable(self):
        if self.cur_pos + 1 >= self.length:
            return "state_variable", "else", None

        cur_char = self.source[self.cur_pos]
        self.cur_pos += 1
        if cur_char in Lexer.var_characters:
            self.buffer += cur_char
            return "state_variable", "var_characters", None
        if not (cur_char.isspace() or cur_char == ')'):
            return "start", "else", None

        self.cur_pos -= 2
        return "state_variable", "else", None

    def dispatch(self, state, input_state=None):
        if self.cur_pos >= self.length:
            return None, None, Token("", TokenType.EOF)

        cur_char = self.source[self.cur_pos]
        if input_state is None:
            if cur_char == "0":
                action = self.state_table[state]["0"]
            elif cur_char.isdigit():
                self.buffer += cur_char
                action = self.state_table[state]["digit_not_zero"]
            elif cur_char in self.state_table[state]:
                action = self.state_table[state][cur_char]
            elif cur_char.isalpha():
                action = self.state_table[state]["alpha"]
            else:
                action = self.state_error
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
                return token
