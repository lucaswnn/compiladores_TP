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
    text = """
    let
        fun sumSq n = if n = 0 then 0 else n * n + sumSq (n-1)
    in
        sumSq 4
    end
    """
    lexer = Lexer(text)
    tokens = list(lexer.tokens())
    print(tokens)
    parser = Parser(lexer.tokens())
    exp = parser.parse()
    visitor = EvalVisitor()
    print(f"{exp.accept(visitor, {})}")