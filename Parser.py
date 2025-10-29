import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements a parser for SML with anonymous functions and type
annotations. The grammar is as follows:

fn_exp  ::= fn <var>: types => fn_exp
          | if_exp
if_exp  ::= <if> if_exp <then> fn_exp <else> fn_exp
          | or_exp
or_exp  ::= and_exp (or and_exp)*
and_exp ::= eq_exp (and eq_exp)*
eq_exp  ::= cmp_exp (= cmp_exp)*
cmp_exp ::= add_exp ([<=|<] add_exp)*
add_exp ::= mul_exp ([+|-] mul_exp)*
mul_exp ::= unary_exp ([*|/] unary_exp)*
unary_exp ::= <not> unary_exp
             | ~ unary_exp
             | let_exp
let_exp ::= <let> <var>: types <- fn_exp <in> fn_exp <end>
          | val_exp
val_exp ::= val_tk (val_tk)*
val_tk ::= <var> | ( fn_exp ) | <num> | <true> | <false>

types ::= type -> types | type

type ::= int | bool | ( types )

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""


class Parser:
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token. For instance:
        """
        self.tokens = list(tokens)
        self.cur_token_idx = 0  # This is just a suggestion!

    def consumeToken(self, token_type):
        if self.current_token.kind == token_type:
            if self.cur_token_idx < len(self.tokens) - 1:
                self.cur_token_idx += 1
            else:
                self.cur_token_idx = -1
        else:
            raise ValueError(f"Unexpected token: {self.current_token.kind}")

    @property
    def current_token(self):
        if self.cur_token_idx == -1:
            return Token('eof', TokenType.EOF)

        return self.tokens[self.cur_token_idx]

    def parse(self):
        """
        Returns the expression associated with the stream of tokens.

        Examples:
        >>> parser = Parser([Token('123', TokenType.NUM)])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('4', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('42', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        42

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('21', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('v', TokenType.VAR)
        >>> tk8 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        42
        """

        return self.Exp()

    def Exp(self):
        return self.Not()

    def Not(self):
        token = self.current_token
        if token.kind == TokenType.NOT:
            self.consumeToken(TokenType.NOT)
            exp = self.B()
            return Not(exp)

        return self.B()

    def B(self):
        exp = self.P()
        return self.Bool(exp)

    def Bool(self, left):
        token = self.current_token
        if token.kind == TokenType.EQL:
            self.consumeToken(TokenType.EQL)
            right = self.P()
            return self.Bool(Eql(left, right))
        elif token.kind == TokenType.LEQ:
            self.consumeToken(TokenType.LEQ)
            right = self.P()
            return self.Bool(Leq(left, right))
        elif token.kind == TokenType.LTH:
            self.consumeToken(TokenType.LTH)
            right = self.P()
            return self.Bool(Lth(left, right))

        return left

    def P(self):
        exp = self.M()
        return self.Plus(exp)

    def Plus(self, left):
        token = self.current_token
        if token.kind == TokenType.ADD:
            self.consumeToken(TokenType.ADD)
            right = self.M()
            return self.Plus(Add(left, right))
        elif token.kind == TokenType.SUB:
            self.consumeToken(TokenType.SUB)
            right = self.M()
            return self.Plus(Sub(left, right))

        return left

    def M(self):
        exp = self.F()
        return self.Mul(exp)

    def Mul(self, left):
        token = self.current_token
        if token.kind == TokenType.MUL:
            self.consumeToken(TokenType.MUL)
            right = self.F()
            return self.Mul(Mul(left, right))
        elif token.kind == TokenType.DIV:
            self.consumeToken(TokenType.DIV)
            right = self.F()
            return self.Mul(Div(left, right))

        return left

    def F(self):
        token = self.current_token
        if token.kind == TokenType.NUM:
            self.consumeToken(TokenType.NUM)
            return Num(int(token.text))

        if token.kind == TokenType.VAR:
            self.consumeToken(TokenType.VAR)
            return Var(token.text)

        elif token.kind == TokenType.TRU:
            self.consumeToken(TokenType.TRU)
            return Bln(True)

        elif token.kind == TokenType.FLS:
            self.consumeToken(TokenType.FLS)
            return Bln(False)

        elif token.kind == TokenType.NEG:
            self.consumeToken(TokenType.NEG)
            node = self.F()
            return Neg(node)

        elif token.kind == TokenType.LPR:  # '('
            self.consumeToken(TokenType.LPR)
            node = self.Exp()
            self.consumeToken(TokenType.RPR)  # ')'
            return node

        elif token.kind == TokenType.LET:
            self.consumeToken(TokenType.LET)
            token = self.current_token
            if token.kind != TokenType.VAR:
                raise ValueError("Bloco let não começa com variável")
            self.consumeToken(TokenType.VAR)
            name = token.text
            token = self.current_token
            if token.kind != TokenType.ASN:
                raise ValueError("Variável sem símbolo de assign")
            self.consumeToken(TokenType.ASN)
            e0 = self.Exp()
            token = self.current_token
            if token.kind != TokenType.INX:
                raise ValueError("Bloco let sem in")
            self.consumeToken(TokenType.INX)
            e1 = self.Exp()
            token = self.current_token
            if token.kind != TokenType.END:
                raise ValueError("Bloco let sem end")
            self.consumeToken(TokenType.END)
            return Let(name, e0, e1)
