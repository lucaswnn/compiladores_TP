import sys
from Expression import *
from Visitor import *
from Lexer import Lexer
from Parser import Parser

if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do parser.
    """
    #text = sys.stdin.read()
    text = "~ if 2 < 3 then 1 else 0"
    lexer = Lexer(text)
    tks = [x for x in lexer.tokens()]
    parser = Parser(tks)
    exp = parser.parse()
    visitor = EvalVisitor()
    print(f"{exp.accept(visitor, {})}")
