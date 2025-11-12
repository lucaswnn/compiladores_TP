import sys

from Expression import *
from Lexer import Token, TokenType

"""
Precedence table:
    1: not ~ ()
    2: *   /
    3: +   -
    4: <   <=   >=   >
    5: =
    6: and
    7: or
    8: if-then-else

Notice that not 2 < 3 must be a type error, as we are trying to apply a boolean
operation (not) onto a number. However, in assembly code this program works,
because not 2 is 0. The bottom line is: don't worry about programs like this
one: the would have been ruled out by type verification anyway.

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
        return self.IfExp()

    def IfExp(self):
        token = self.current_token
        if token.kind == TokenType.IFX:
            self.consumeToken(TokenType.IFX)
            cond_exp = self.IfExp()
            token = self.current_token
            if token.kind != TokenType.THN:
                raise ValueError("Expressão if sem then")
            self.consumeToken(TokenType.THN)
            then_exp = self.IfExp()
            token = self.current_token
            if token.kind != TokenType.ELS:
                raise ValueError("Expressão if sem else")
            self.consumeToken(TokenType.ELS)
            else_exp = self.IfExp()
            return IfThenElse(cond_exp, then_exp, else_exp)
        return self.Or()

    def Or(self):
        exp = self.And()
        return self.OrExp(exp)

    def OrExp(self, left):
        token = self.current_token
        if token.kind == TokenType.ORX:
            self.consumeToken(TokenType.ORX)
            right = self.And()
            return self.OrExp(Or(left, right))

        return left

    def And(self):
        exp = self.B()
        return self.AndExp(exp)

    def AndExp(self, left):
        token = self.current_token
        if token.kind == TokenType.AND:
            self.consumeToken(TokenType.AND)
            right = self.B()
            return self.AndExp(And(left, right))

        return left

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
            next_token = self.current_token
            if not (next_token.kind == TokenType.TRU
                    or next_token.kind == TokenType.FLS
                    or next_token.kind == TokenType.VAR
                    or next_token.kind == TokenType.NUM
                    or next_token.kind == TokenType.LPR
                    or next_token.kind == TokenType.LET):
                sys.exit("Parse error")
            node = self.F()
            return Neg(node)

        elif token.kind == TokenType.NOT:
            self.consumeToken(TokenType.NOT)
            next_token = self.current_token
            if not (next_token.kind == TokenType.TRU
                    or next_token.kind == TokenType.FLS
                    or next_token.kind == TokenType.VAR
                    or next_token.kind == TokenType.NUM
                    or next_token.kind == TokenType.LPR
                    or next_token.kind == TokenType.LET):
                sys.exit("Parse error")
            node = self.F()
            return Not(node)

        elif token.kind == TokenType.LPR:  # '('
            self.consumeToken(TokenType.LPR)
            node = self.IfExp()
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
            e0 = self.IfExp()
            token = self.current_token
            if token.kind != TokenType.INX:
                raise ValueError("Bloco let sem in")
            self.consumeToken(TokenType.INX)
            e1 = self.IfExp()
            token = self.current_token
            if token.kind != TokenType.END:
                raise ValueError("Bloco let sem end")
            self.consumeToken(TokenType.END)
            return Let(name, e0, e1)
