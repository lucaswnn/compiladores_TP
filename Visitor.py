import sys
from abc import ABC, abstractmethod
from Expression import *
import Asm as AsmModule


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


class GenVisitor(Visitor):
    """
    The GenVisitor class compiles arithmetic expressions into a low-level
    language.
    """

    def __init__(self):
        self.next_var_counter = 0

    def next_var_name(self):
        self.next_var_counter += 1
        return f"v{self.next_var_counter}"

    def visit_var(self, exp, prog):
        """
        Usage:
            >>> e = Var('x')
            >>> p = AsmModule.Program({"x":1}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1
        """
        return exp.identifier

    def visit_bln(self, exp, prog):
        """
        Usage:
            >>> e = Bln(True)
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Bln(False)
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            0
        """
        if exp.bln:
            var_name = self.next_var_name()
            prog.add_inst(AsmModule.Addi(var_name, "x0", 1))
            return var_name
        else:
            return "x0"

    def visit_num(self, exp, prog):
        """
        Usage:
            >>> e = Num(13)
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            13
        """
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Addi(v_name, "x0", exp.num))
        return v_name

    def visit_eql(self, exp, prog):
        """
        >>> e = Eql(Num(13), Num(13))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Eql(Num(13), Num(10))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Eql(Num(-1), Num(1))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)

        l_less_r_name = self.next_var_name()
        prog.add_inst(AsmModule.Slt(l_less_r_name, l_name, r_name))

        r_less_l_name = self.next_var_name()
        prog.add_inst(AsmModule.Slt(r_less_l_name, r_name, l_name))

        is_different_name = self.next_var_name()
        prog.add_inst(AsmModule.Add(is_different_name,
                      l_less_r_name, r_less_l_name))

        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v_name, is_different_name, 1))
        return v_name

    def visit_and(self, exp, prog):
        """
        >>> e = And(Bln(True), Bln(True))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = And(Bln(False), Bln(True))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = And(Bln(True), Bln(False))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = And(Bln(False), Bln(False))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = And(Bln(False), Div(Num(3), Num(0)))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left = exp.left.accept(self, prog)
        beq_left = AsmModule.Beq(left, "x0")
        prog.add_inst(beq_left)
        right = exp.right.accept(self, prog)
        beq_right = AsmModule.Beq(right, "x0")
        prog.add_inst(beq_right)
        r = self.next_var_name()
        prog.add_inst(AsmModule.Addi(r, "x0", 1))
        end = AsmModule.Jal("x0")
        prog.add_inst(end)
        n_inst = prog.get_number_of_instructions()
        beq_left.set_target(n_inst)
        beq_right.set_target(n_inst)
        prog.add_inst(AsmModule.Addi(r, "x0", 0))
        n_inst = prog.get_number_of_instructions()
        end.set_target(n_inst)
        return r

    def visit_or(self, exp, prog):
        """
        >>> e = Or(Bln(True), Bln(True))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Or(Bln(False), Bln(True))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Or(Bln(True), Bln(False))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Or(Bln(False), Bln(False))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Or(Bln(True), Div(Num(3), Num(0)))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        one = self.next_var_name()
        prog.add_inst(AsmModule.Addi(one, "x0", 1))
        left = exp.left.accept(self, prog)
        beq_left = AsmModule.Beq(left, one)
        prog.add_inst(beq_left)
        right = exp.right.accept(self, prog)
        beq_right = AsmModule.Beq(right, one)
        prog.add_inst(beq_right)
        r = self.next_var_name()
        prog.add_inst(AsmModule.Addi(r, "x0", 0))
        end = AsmModule.Jal("x0")
        prog.add_inst(end)
        n_inst = prog.get_number_of_instructions()
        beq_left.set_target(n_inst)
        beq_right.set_target(n_inst)
        prog.add_inst(AsmModule.Addi(r, "x0", 1))
        n_inst = prog.get_number_of_instructions()
        end.set_target(n_inst)
        return r

    def visit_add(self, exp, prog):
        """
        >>> e = Add(Num(13), Num(-13))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Add(Num(13), Num(10))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        23
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Add(v_name, l_name, r_name))
        return v_name

    def visit_sub(self, exp, prog):
        """
        >>> e = Sub(Num(13), Num(-13))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Sub(Num(13), Num(10))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Sub(v_name, l_name, r_name))
        return v_name

    def visit_mul(self, exp, prog):
        """
        >>> e = Mul(Num(13), Num(2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Mul(Num(13), Num(10))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        130
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Mul(v_name, l_name, r_name))
        return v_name

    def visit_div(self, exp, prog):
        """
        >>> e = Div(Num(13), Num(2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        6

        >>> e = Div(Num(13), Num(10))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Div(v_name, l_name, r_name))
        return v_name

    def visit_leq(self, exp, prog):
        """
        >>> e = Leq(Num(3), Num(2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Leq(Num(3), Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(2), Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-2), Num(-3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)

        is_r_less_l_name = self.next_var_name()
        prog.add_inst(AsmModule.Slt(is_r_less_l_name, r_name, l_name))

        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v_name, is_r_less_l_name, 1))
        return v_name

    def visit_lth(self, exp, prog):
        """
        >>> e = Lth(Num(3), Num(2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(3), Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(2), Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        l_name = exp.left.accept(self, prog)
        r_name = exp.right.accept(self, prog)

        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v_name, l_name, r_name))
        return v_name

    def visit_neg(self, exp, prog):
        """
        >>> e = Neg(Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -3

        >>> e = Neg(Num(0))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Neg(Num(-3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        name = exp.exp.accept(self, prog)
        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Sub(v_name, "x0", name))
        return v_name

    def visit_not(self, exp, prog):
        """
        >>> e = Not(Bln(True))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Bln(False))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(0))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(-2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Num(2))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        val = exp.exp.accept(self, prog)

        is_neg = self.next_var_name()
        is_pos = self.next_var_name()

        prog.add_inst(AsmModule.Slt(is_neg, val, "x0"))
        prog.add_inst(AsmModule.Slt(is_pos, "x0", val))

        is_not_zero = self.next_var_name()
        prog.add_inst(AsmModule.Add(is_not_zero, is_neg, is_pos))

        v_name = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v_name, is_not_zero, 1))
        return v_name

    def visit_let(self, exp, prog):
        """
        Usage:
            >>> e = Let('v', Not(Bln(False)), Var('v'))
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Let('v', Num(2), Add(Var('v'), Num(3)))
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            5

            >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
            >>> e1 = Let('y', e0, Mul(Var('y'), Num(10)))
            >>> p = AsmModule.Program({}, [])
            >>> g = GenVisitor()
            >>> v = e1.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            50
        """
        exp_def_name = exp.exp_def.accept(self, prog)
        prog.add_inst(AsmModule.Add(exp.identifier, exp_def_name, "x0"))

        exp_body_name = exp.exp_body.accept(self, prog)

        return exp_body_name

    def visit_ifThenElse(self, exp, prog):
        """
        >>> e = IfThenElse(Bln(True), Num(3), Num(5))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3

        >>> e = IfThenElse(Bln(False), Num(3), Num(5))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        5

        >>> e = IfThenElse(And(Bln(True), Bln(True)), Num(3), Num(5))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3

        >>> e0 = Mul(Num(2), Add(Num(3), Num(4)))
        >>> e1 = IfThenElse(And(Bln(True), Bln(False)), Num(3), e0)
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e1.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        14

        >>> e0 = Div(Num(2), Num(0))
        >>> e1 = IfThenElse(Bln(True), Num(3), e0)
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e1.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3

        >>> e0 = Div(Num(2), Num(0))
        >>> e1 = IfThenElse(Bln(False), e0, Num(3))
        >>> p = AsmModule.Program({}, [])
        >>> g = GenVisitor()
        >>> v = e1.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        cond_name = exp.cond.accept(self, prog)
        else_beq = AsmModule.Beq(cond_name, "x0")
        prog.add_inst(else_beq)
        then_name = exp.e0.accept(self, prog)
        r = self.next_var_name()
        prog.add_inst(AsmModule.Add(r, then_name, "x0"))
        end = AsmModule.Jal("x0")
        prog.add_inst(end)
        n_inst = prog.get_number_of_instructions()
        else_beq.set_target(n_inst)
        else_name = exp.e1.accept(self, prog)
        prog.add_inst(AsmModule.Add(r, else_name, "x0"))
        n_inst = prog.get_number_of_instructions()
        end.set_target(n_inst)
        return r


class RenameVisitor(ABC):
    """
    This visitor traverses the AST of a program, renaming variables to ensure
    that they all have different names.

    Usage:
        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> e0.identifier == e1.identifier
        True

        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> e0.identifier == e1.identifier
        False

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> x0.identifier == x1.identifier
        True

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> x0.identifier == x1.identifier
        False
    """

    def generate_unique_name(self, var_name, scope):
        """
        Generates a unique name for the variable to avoid shadowing.
        """
        if var_name not in scope:
            scope[var_name] = []

        # Create a unique name by appending a counter or unique suffix
        unique_name = f"{var_name}_{len(scope[var_name])}"

        # Push the unique name onto the stack for this variable
        scope[var_name].append(unique_name)

        return unique_name

    def pop_variable(self, var_name, scope):
        """
        Pops the variable name off the stack when exiting a scope.
        """
        if var_name in scope and scope[var_name]:
            scope[var_name].pop()

    def get_current_var_name(self, var_name, scope):
        """
        Returns the current variable name (the one on top of the stack).
        """
        if var_name in scope and scope[var_name]:
            return scope[var_name][-1]
        return var_name  # If no stack entry, return the original nam

    def visit_var(self, exp, arg):
        exp.identifier = self.get_current_var_name(exp.identifier, arg)

    def visit_bln(self, exp, arg):
        pass

    def visit_num(self, exp, arg):
        pass

    def visit_eql(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_and(self, exp, name_map):
        """
        Example:
            >>> y0 = Var('x')
            >>> y1 = Var('x')
            >>> x0 = And(Lth(y0, Num(2)), Leq(Num(2), y1))
            >>> x1 = Var('x')
            >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
            >>> e1 = Let('x', e0, Mul(x1, Num(10)))
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> y0.identifier == y1.identifier
            True

            >>> y0 = Var('x')
            >>> y1 = Var('x')
            >>> x0 = And(Lth(y0, Num(2)), Leq(Num(2), y1))
            >>> x1 = Var('x')
            >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
            >>> e1 = Let('x', e0, Mul(x1, Num(10)))
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> y0.identifier == x1.identifier
            False
        """
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_or(self, exp, name_map):
        """
        Example:
            >>> y0 = Var('x')
            >>> y1 = Var('x')
            >>> x0 = Or(Lth(y0, Num(2)), Leq(Num(2), y1))
            >>> x1 = Var('x')
            >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
            >>> e1 = Let('x', e0, Mul(x1, Num(10)))
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> y0.identifier == y1.identifier
            True

            >>> y0 = Var('x')
            >>> y1 = Var('x')
            >>> x0 = Or(Lth(y0, Num(2)), Leq(Num(2), y1))
            >>> x1 = Var('x')
            >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
            >>> e1 = Let('x', e0, Mul(x1, Num(10)))
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> y0.identifier == x1.identifier
            False
        """
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_add(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_sub(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_mul(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_div(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_leq(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_lth(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_neg(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_not(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_ifThenElse(self, exp, name_map):
        """
        Example:
            >>> x0 = Var('x')
            >>> x1 = Var('x')
            >>> e0 = IfThenElse(Lth(x0, x1), Num(1), Num(2))
            >>> e1 = Let('x', Num(3), e0)
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> x0.identifier == x1.identifier
            True

            >>> x0 = Var('x')
            >>> x1 = Var('x')
            >>> e0 = IfThenElse(Lth(x0, x1), Num(1), Num(2))
            >>> e1 = Let('x', Num(3), e0)
            >>> e2 = Let('x', e1, Num(3))
            >>> r = RenameVisitor()
            >>> e1.accept(r, {})
            >>> e2.identifier != x1.identifier == e1.identifier
            True
        """
        exp.cond.accept(self, name_map)
        exp.e0.accept(self, name_map)
        exp.e1.accept(self, name_map)

    def visit_let(self, exp, arg):
        exp.exp_def.accept(self, arg)
        unique_name = self.generate_unique_name(exp.identifier, arg)
        exp.exp_body.accept(self, arg)
        self.pop_variable(exp.identifier, arg)
        exp.identifier = unique_name


if __name__ == "__main__":
    e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
    e1 = Let('x', e0, Mul(Var('x'), Num(10)))
    r = RenameVisitor()
    e1.accept(r, {})
    e0.identifier == e1.identifier
