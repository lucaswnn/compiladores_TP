import sys
from abc import ABC, abstractmethod
from Expression import *


class Visitor(ABC):
    """
    The visitor pattern consists of two abstract classes: the Expression and the
    Visitor. The Expression class defines on method: 'accept(visitor, args)'.
    This method takes in an implementation of a visitor, and the arguments that
    are passed from expression to expression. The Visitor class defines one
    specific method for each subclass of Expression. Each instance of such a
    subclasse will invoke the right visiting method.
    """
    @abstractmethod
    def visit_var(self, exp, arg):
        pass

    @abstractmethod
    def visit_bln(self, exp, arg):
        pass

    @abstractmethod
    def visit_num(self, exp, arg):
        pass

    @abstractmethod
    def visit_eql(self, exp, arg):
        pass

    @abstractmethod
    def visit_and(self, exp, arg):
        pass

    @abstractmethod
    def visit_or(self, exp, arg):
        pass

    @abstractmethod
    def visit_add(self, exp, arg):
        pass

    @abstractmethod
    def visit_sub(self, exp, arg):
        pass

    @abstractmethod
    def visit_mul(self, exp, arg):
        pass

    @abstractmethod
    def visit_div(self, exp, arg):
        pass

    @abstractmethod
    def visit_leq(self, exp, arg):
        pass

    @abstractmethod
    def visit_lth(self, exp, arg):
        pass

    @abstractmethod
    def visit_neg(self, exp, arg):
        pass

    @abstractmethod
    def visit_not(self, exp, arg):
        pass

    @abstractmethod
    def visit_let(self, exp, arg):
        pass

    @abstractmethod
    def visit_ifThenElse(self, exp, arg):
        pass

    @abstractmethod
    def visit_fn(self, exp, arg):
        pass

    @abstractmethod
    def visit_app(self, exp, arg):
        pass


class Function():
    """
    This is the class that represents functions. This class lets us distinguish
    the three types that now exist in the language: numbers, booleans and
    functions. Notice that the evaluation of an expression can now be a
    function. For instance:

        >>> f = Fn('v', Mul(Var('v'), Var('v')))
        >>> ev = EvalVisitor()
        >>> fval = f.accept(ev, {})
        >>> type(fval)
        <class 'Visitor.Function'>
    """

    def __init__(self, formal, body, env):
        self.formal = formal
        self.body = body
        self.env = env

    def __str__(self):
        return f"Fn({self.formal})"


class EvalVisitor(Visitor):
    """
    The EvalVisitor class evaluates logical and arithmetic expressions. The
    result of evaluating an expression is the value of that expression. The
    inherited attribute propagated throughout visits is the environment that
    associates the names of variables with values.

    Examples:
    >>> e0 = Let('v', Add(Num(40), Num(2)), Mul(Var('v'), Var('v')))
    >>> e1 = Not(Eql(e0, Num(1764)))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {})
    False

    >>> e0 = Let('v', Add(Num(40), Num(2)), Sub(Var('v'), Num(2)))
    >>> e1 = Lth(e0, Var('x'))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {'x': 41})
    True
    """

    def visit_var(self, exp, env):  # Implemented for you :)
        if exp.identifier in env:
            return env[exp.identifier]
        else:
            sys.exit("Def error")

    def visit_bln(self, exp, env):  # Implemented for you :)
        return exp.bln

    def visit_num(self, exp, env):  # Implemented for you :)
        return exp.num

    def visit_eql(self, exp, env):  # Implemented for you :)
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right):
            return val_left == val_right
        else:
            sys.exit("Type error")

    def visit_and(self, exp, env):
        val_left = exp.left.accept(self, env)
        if type(val_left) != type(True):
            sys.exit("Type error")
        if val_left:
            val_right = exp.right.accept(self, env)
            if type(val_right) != type(True):
                sys.exit("Type error")
            return val_right
        return False

    def visit_or(self, exp, env):
        val_left = exp.left.accept(self, env)
        if type(val_left) != type(True):
            sys.exit("Type error")
        if not val_left:
            val_right = exp.right.accept(self, env)
            if type(val_right) != type(True):
                sys.exit("Type error")
            return val_right
        return True

    def visit_add(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left + val_right
        else:
            sys.exit("Type error")

    def visit_sub(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left - val_right
        else:
            sys.exit("Type error")

    def visit_mul(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left * val_right
        else:
            sys.exit("Type error")

    def visit_div(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left // val_right
        else:
            sys.exit("Type error")

    def visit_leq(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left <= val_right
        else:
            sys.exit("Type error")

    def visit_lth(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right) == type(1):
            return val_left < val_right
        else:
            sys.exit("Type error")

    def visit_neg(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) == type(1):
            return -val
        else:
            sys.exit("Type error")

    def visit_not(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) == type(True):
            return not val
        else:
            sys.exit("Type error")

    def visit_let(self, exp, env):
        e0_val = exp.exp_def.accept(self, env)
        new_env = dict(env)
        new_env[exp.identifier] = e0_val
        return exp.exp_body.accept(self, new_env)

    def visit_ifThenElse(self, exp, env):
        cond_val = exp.cond.accept(self, env)
        if type(cond_val) != type(True):
            sys.exit("Type error")
        if cond_val:
            return exp.e0.accept(self, env)
        else:
            return exp.e1.accept(self, env)

    def visit_fn(self, exp, env):  # Implemented for you :)
        """
        The evaluation of a function is the function itself. Remember: in our
        language, functions are values as well. So, now we have three kinds of
        values: numbers, booleans and functions.
        """
        return Function(exp.formal, exp.body, env)

    def visit_app(self, exp, env):
        """
        Here comes most of the complexity of the homework, in five or six lines
        of code! You must implement the evaluation of a function application.
        """
        function = exp.function.accept(self, env)
        actual = exp.actual.accept(self, env)
        new_env = dict(function.env)
        new_env[function.formal] = actual
        return function.body.accept(self, new_env)
