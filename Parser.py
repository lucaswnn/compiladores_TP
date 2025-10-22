import sys

from Expression import *
from Lexer import Token, TokenType
from Visitor import ArrowType

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
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('42', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('21', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('+', TokenType.ADD)
        >>> t9 = Token('v', TokenType.VAR)
        >>> tA = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

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
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token(':', TokenType.COL)
        >>> tk3 = Token('int', TokenType.INT)
        >>> tk4 = Token('=>', TokenType.ARW)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> print(exp.accept(ev, {}))
        <class 'int'> -> <class 'int'>

        >>> t0 = Token('(', TokenType.LPR)
        >>> t1 = Token('fn', TokenType.FNX)
        >>> t2 = Token('v', TokenType.VAR)
        >>> t3 = Token(':', TokenType.COL)
        >>> t4 = Token('int', TokenType.INT)
        >>> t5 = Token('=>', TokenType.ARW)
        >>> t6 = Token('v', TokenType.VAR)
        >>> t7 = Token('+', TokenType.ADD)
        >>> t8 = Token('1', TokenType.NUM)
        >>> t9 = Token(')', TokenType.RPR)
        >>> tA = Token('2', TokenType.NUM)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>
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
            if token.kind != TokenType.COL:
                sys.exit("Parse error")
            self.consumeToken(TokenType.COL)

            tp_var = self.TYPES()

            token = self.current_token
            if token.kind != TokenType.ARW:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ARW)
            body_exp = self.FN_EXP()
            return Fn(var_name, tp_var, body_exp)
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

            token = self.current_token
            if token.kind != TokenType.VAR:
                sys.exit("Parse error")
            self.consumeToken(TokenType.VAR)
            identifier = token.text

            token = self.current_token
            if token.kind != TokenType.COL:
                sys.exit("Parse error")
            self.consumeToken(TokenType.COL)

            tp_var = self.TYPES()

            token = self.current_token
            if token.kind != TokenType.ASN:
                sys.exit("Parse error")
            self.consumeToken(TokenType.ASN)

            exp_def = self.FN_EXP()

            token = self.current_token
            if token.kind != TokenType.INX:
                sys.exit("Parse error")
            self.consumeToken(TokenType.INX)

            exp_body = self.FN_EXP()

            token = self.current_token
            if token.kind != TokenType.END:
                sys.exit("Parse error")
            self.consumeToken(TokenType.END)

            return Let(identifier, tp_var, exp_def, exp_body)
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

    def TYPES(self):
        tp = self.TYPE()
        token = self.current_token
        if token.kind == TokenType.TPF:
            self.consumeToken(TokenType.TPF)
            tp = ArrowType(tp, self.TYPES())

        return tp

    def TYPE(self):
        token = self.current_token
        if token.kind == TokenType.INT:
            self.consumeToken(TokenType.INT)
            return type(1)
        elif token.kind == TokenType.LGC:
            self.consumeToken(TokenType.LGC)
            return type(True)
        elif token.kind == TokenType.LPR:
            self.consumeToken(TokenType.LPR)
            tp = self.TYPES()
            token = self.current_token
            if token.kind != TokenType.RPR:
                sys.exit("Parse error")
            self.consumeToken(TokenType.RPR)
            return tp
