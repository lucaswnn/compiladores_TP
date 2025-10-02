import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of arithmetic expressions.

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
operation (not) onto a number.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
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
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        26

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('42', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
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
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('2', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('then', TokenType.THN)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> tk6 = Token('else', TokenType.ELS)
        >>> tk7 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        1

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        2
        """

        return self.Exp()

    def Exp(self):
        return self.ITE()

    def ITE(self):
        token = self.current_token
        if token.kind == TokenType.IFX:
            self.consumeToken(TokenType.IFX)
            if_exp = self.ITE()
            token = self.current_token
            if token.kind != TokenType.THN:
                sys.exit("Parse error")
            self.consumeToken(TokenType.THN)
            then_exp = self.DIS()
            token = self.current_token
            if token.kind != TokenType.ELS:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ELS)
            else_exp = self.DIS()
            return IfThenElse(if_exp, then_exp, else_exp)

        return self.DIS()

    def DIS(self):
        exp = self.CON()
        return self.Disjunction(exp)

    def Disjunction(self, left):
        token = self.current_token
        if token.kind == TokenType.ORX:
            self.consumeToken(TokenType.ORX)
            right = self.CON()
            return self.Disjunction(Or(left, right))
        return left

    def CON(self):
        exp = self.B()
        return self.Conjunction(exp)

    def Conjunction(self, left):
        token = self.current_token
        if token.kind == TokenType.AND:
            self.consumeToken(TokenType.AND)
            right = self.B()
            return self.Conjunction(And(left, right))
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
            token = self.current_token
            if (not
                (token.kind == TokenType.LPR or
                         token.kind == TokenType.VAR or
                         token.kind == TokenType.NUM or
                         token.kind == TokenType.LET)
                ):
                sys.exit("Parse error")
            node = self.F()
            return Neg(node)

        elif token.kind == TokenType.LPR:  # '('
            self.consumeToken(TokenType.LPR)
            node = self.Exp()
            self.consumeToken(TokenType.RPR)  # ')'
            return node

        elif token.kind == TokenType.NOT:
            self.consumeToken(TokenType.NOT)
            token = self.current_token
            if (not
                    (token.kind == TokenType.LPR
                     or token.kind == TokenType.VAR
                     or token.kind == TokenType.TRU
                     or token.kind == TokenType.FLS
                     or token.kind == TokenType.NUM
                     or token.kind == TokenType.LET)
                    ):
                sys.exit("Parse error")
            node = self.F()
            return Not(node)

        elif token.kind == TokenType.LET:
            self.consumeToken(TokenType.LET)
            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            self.consumeToken(TokenType.VAR)
            name = token.text
            token = self.current_token
            if token.kind != TokenType.ASN:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ASN)
            e0 = self.Exp()
            token = self.current_token
            if token.kind != TokenType.INX:
                sys.exit("Parse error")
            self.consumeToken(TokenType.INX)
            e1 = self.Exp()
            token = self.current_token
            if token.kind != TokenType.END:
                sys.exit("Parse error")
            self.consumeToken(TokenType.END)
            return Let(name, e0, e1)
