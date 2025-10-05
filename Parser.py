import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements a parser for SML with anonymous functions. The grammar is
as follows:

fn_exp  ::= fn <var> => fn_exp
          | if_exp
if_exp  ::= <if> if_exp <then> fn_exp <else> fn_exp
          | or_exp
or_exp  ::= and_exp (or and_exp)*
and_exp ::= eq_exp (and eq_exp)*
eq_exp  ::= cmp_exp (= cmp_exp)*
cmp_exp ::= add_exp ([<=|<] add_exp)*
add_exp ::= mul_exp ([+|-] mul_exp)*
mul_exp ::= uny_exp ([*|div|mod] uny_exp)*
uny_exp ::= <not> uny_exp
          | ~ uny_exp
          | let_exp
let_exp ::= <let> decl <in> fn_exp <end>
          | val_exp
val_exp ::= val_tk (val_tk)*
val_tk  ::= <var> | ( fn_exp ) | <num> | <true> | <false>

decl    ::= val <var> = fn_exp
          | fun <var> <var> = fn_exp

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
        >>> tk1 = Token('div', TokenType.DIV)
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
        >>> tk1 = Token('val', TokenType.VAL)
        >>> tk2 = Token('v', TokenType.VAR)
        >>> tk3 = Token('=', TokenType.EQL)
        >>> tk4 = Token('42', TokenType.NUM)
        >>> tk5 = Token('in', TokenType.INX)
        >>> tk6 = Token('v', TokenType.VAR)
        >>> tk7 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('val', TokenType.VAL)
        >>> tk2 = Token('v', TokenType.VAR)
        >>> tk3 = Token('=', TokenType.EQL)
        >>> tk4 = Token('21', TokenType.NUM)
        >>> tk5 = Token('in', TokenType.INX)
        >>> tk6 = Token('v', TokenType.VAR)
        >>> tk7 = Token('+', TokenType.ADD)
        >>> tk8 = Token('v', TokenType.VAR)
        >>> tk9 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8, tk9])
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

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('=>', TokenType.ARW)
        >>> tk3 = Token('v', TokenType.VAR)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> print(exp.accept(ev, None))
        Fn(v)

        >>> tk0 = Token('(', TokenType.LPR)
        >>> tk1 = Token('fn', TokenType.FNX)
        >>> tk2 = Token('v', TokenType.VAR)
        >>> tk3 = Token('=>', TokenType.ARW)
        >>> tk4 = Token('v', TokenType.VAR)
        >>> tk5 = Token('+', TokenType.ADD)
        >>> tk6 = Token('1', TokenType.NUM)
        >>> tk7 = Token(')', TokenType.RPR)
        >>> tk8 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        3

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('fun', TokenType.FUN)
        >>> t2 = Token('f', TokenType.VAR)
        >>> t3 = Token('v', TokenType.VAR)
        >>> t4 = Token('=', TokenType.EQL)
        >>> t5 = Token('v', TokenType.VAR)
        >>> t6 = Token('+', TokenType.ADD)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('in', TokenType.INX)
        >>> t9 = Token('f', TokenType.VAR)
        >>> tA = Token('2', TokenType.NUM)
        >>> tB = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA, tB])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        4
        """

        return self.FN_EXP()

    def FN_EXP(self):
        token = self.current_token
        if token.kind == TokenType.FNX:
            self.consumeToken(TokenType.FNX)
            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            self.consumeToken(TokenType.VAR)
            var_name = token.text
            token = self.current_token
            if token.kind != TokenType.ARW:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ARW)
            body_exp = self.FN_EXP()
            return Fn(var_name, body_exp)
        else:
            return self.IF_EXP()

    def IF_EXP(self):
        token = self.current_token
        if token.kind == TokenType.IFX:
            self.consumeToken(TokenType.IFX)
            if_exp = self.IF_EXP()
            token = self.current_token
            if token.kind != TokenType.THN:
                sys.exit("Parse error")
            self.consumeToken(TokenType.THN)
            then_exp = self.FN_EXP()
            token = self.current_token
            if token.kind != TokenType.ELS:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ELS)
            else_exp = self.FN_EXP()
            return IfThenElse(if_exp, then_exp, else_exp)
        else:
            return self.OR_EXP()

    def OR_EXP(self):
        exp = self.AND_EXP()
        return self.Disjunction(exp)

    def Disjunction(self, left):
        token = self.current_token
        if token.kind == TokenType.ORX:
            self.consumeToken(TokenType.ORX)
            right = self.AND_EXP()
            return self.Disjunction(Or(left, right))
        else:
            return left

    def AND_EXP(self):
        exp = self.EQ_EXP()
        return self.Conjunction(exp)

    def Conjunction(self, left):
        token = self.current_token
        if token.kind == TokenType.AND:
            self.consumeToken(TokenType.AND)
            right = self.EQ_EXP()
            return self.Conjunction(And(left, right))
        else:
            return left

    def EQ_EXP(self):
        exp = self.CMP_EXP()
        return self.Equal(exp)

    def Equal(self, left):
        token = self.current_token
        if token.kind == TokenType.EQL:
            self.consumeToken(TokenType.EQL)
            right = self.CMP_EXP()
            return self.Equal(Eql(left, right))
        else:
            return left

    def CMP_EXP(self):
        exp = self.ADD_EXP()
        return self.Comparison(exp)

    def Comparison(self, left):
        token = self.current_token
        if token.kind == TokenType.LTH:
            self.consumeToken(TokenType.LTH)
            right = self.ADD_EXP()
            return self.Comparison(Lth(left, right))
        elif token.kind == TokenType.LEQ:
            self.consumeToken(TokenType.LEQ)
            right = self.ADD_EXP()
            return self.Comparison(Leq(left, right))
        else:
            return left

    def ADD_EXP(self):
        exp = self.MUL_EXP()
        return self.SumSub(exp)

    def SumSub(self, left):
        token = self.current_token
        if token.kind == TokenType.ADD:
            self.consumeToken(TokenType.ADD)
            right = self.MUL_EXP()
            return self.SumSub(Add(left, right))
        elif token.kind == TokenType.SUB:
            self.consumeToken(TokenType.SUB)
            right = self.MUL_EXP()
            return self.SumSub(Sub(left, right))
        else:
            return left

    def MUL_EXP(self):
        exp = self.UNARY_EXP()
        return self.MulDiv(exp)

    def MulDiv(self, left):
        token = self.current_token
        if token.kind == TokenType.MUL:
            self.consumeToken(TokenType.MUL)
            right = self.UNARY_EXP()
            return self.MulDiv(Mul(left, right))
        elif token.kind == TokenType.DIV:
            self.consumeToken(TokenType.DIV)
            right = self.UNARY_EXP()
            return self.MulDiv(Div(left, right))
        elif token.kind == TokenType.MOD:
            self.consumeToken(TokenType.MOD)
            right = self.UNARY_EXP()
            return self.MulDiv(Mod(left, right))
        else:
            return left

    def UNARY_EXP(self):
        token = self.current_token
        if token.kind == TokenType.NOT:
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
            exp = self.UNARY_EXP()

            return Not(exp)
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
            exp = self.UNARY_EXP()
            return Neg(exp)
        else:
            return self.LET_EXP()

    def LET_EXP(self):
        token = self.current_token
        if token.kind == TokenType.LET:
            self.consumeToken(TokenType.LET)
            declaration = self.DECL()
            token = self.current_token
            if token.kind != TokenType.INX:
                sys.exit("Parse error")
            self.consumeToken(TokenType.INX)
            e1 = self.FN_EXP()
            token = self.current_token
            if token.kind != TokenType.END:
                sys.exit("Parse error")
            self.consumeToken(TokenType.END)
            return Let(declaration.name, declaration.value, e1)
        else:
            return self.VAL_EXP()

    def VAL_EXP(self):
        exp = self.VAL_TK()
        return self.Value(exp)

    def Value(self, left):
        token = self.current_token
        if token.kind in {TokenType.VAR,
                          TokenType.NUM,
                          TokenType.TRU,
                          TokenType.FLS,
                          TokenType.LPR}:
            right = self.VAL_TK()
            return self.Value(App(left, right))
        else:
            return left

    def VAL_TK(self):
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

        elif token.kind == TokenType.LPR:  # '('
            self.consumeToken(TokenType.LPR)
            node = self.FN_EXP()
            token = self.current_token
            if token.kind != TokenType.RPR:
                sys.exit("Parse error")
            self.consumeToken(TokenType.RPR)  # ')'
            return node

    def DECL(self):
        token = self.current_token
        if token.kind == TokenType.VAL:
            self.consumeToken(TokenType.VAL)
            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            name = token.text
            self.consumeToken(TokenType.VAR)
            token = self.current_token
            if token.kind != TokenType.EQL:
                sys.exit("Parse error")
            self.consumeToken(TokenType.EQL)
            value = self.FN_EXP()
            return Declaration(name, value)
        elif token.kind == TokenType.FUN:
            self.consumeToken(TokenType.FUN)
            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            name = token.text
            self.consumeToken(TokenType.VAR)
            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            formal = token.text
            self.consumeToken(TokenType.VAR)
            token = self.current_token
            if token.kind != TokenType.EQL:
                sys.exit("Parse error")
            self.consumeToken(TokenType.EQL)
            body = self.FN_EXP()
            return Declaration(name, Fun(name, formal, body))
        else:
            sys.exit("Parse error")

class Declaration:
    def __init__(self, name, value):
        self.name = name
        self.value = value