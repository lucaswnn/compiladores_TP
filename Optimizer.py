from abc import ABC, abstractmethod
from Asm import *


class Optimizer(ABC):
    """
    This class implements an "Optimization Pass". The pass receives a sequence
    of instructions stored in a program, and produces a new sequence of
    instructions.
    """

    def __init__(self, prog):
        self.prog = prog

    @abstractmethod
    def optimize(self):
        pass


class RegAllocator(Optimizer):
    """This file implements the register allocation pass."""

    def __init__(self, prog):
        self.reg_set = ["a0", "a1", "a2", "a3"]
        self.reg_map = {reg: None for reg in self.reg_set}
        self.val_map = {}
        self.mem_ptr = 0
        self.reg_counter = 0
        self.mem_map = {}
        self.alloc_action = {
            "add": self.alloc_add,
            "addi": self.alloc_addi,
            "sub": self.alloc_sub,
            "mul": self.alloc_mul,
            "div": self.alloc_div,
            "sw": self.alloc_sw,
            "lw": self.alloc_lw,
            "slt": self.alloc_slt,
            "xori": self.alloc_xori,
        }
        super().__init__(prog)

    def are_regs_busy(self):
        for reg in self.reg_map:
            if self.reg_map[reg] is None:
                return False
        return True

    def get_val(self, var):
        """
        Informs the value that is associated with the variable var within
        the program prog.
        """
        if var in self.reg_set:
            return self.reg_map[var]

        if var in self.val_map:
            reg = self.val_map[var]
            if reg is not None:
                return self.prog.get_val(reg)

        return None

    def get_next_reg(self):
        """
        Returns the next available register for allocation.
        """
        for reg in self.reg_map:
            if self.reg_map[reg] is None:
                return reg

        return None

    def alloc_next_reg(self, val):
        reg = self.get_next_reg()
        if reg is None:
            raise Exception("No register available")
        self.reg_map[reg] = val
        self.val_map[val] = reg
        return reg

    def alloc_next_mem(self, reg):
        if self.reg_map[reg] is None:
            raise Exception("Register not found")

        val = self.reg_map[reg]
        self.mem_ptr += 1
        mem_addr = self.mem_ptr
        val = self.reg_map[reg]
        self.val_map[val] = mem_addr
        self.reg_map[reg] = None
        return mem_addr

    def get_reg_victim(self):
        reg = self.reg_set[self.reg_counter % len(self.reg_set)]
        self.reg_counter += 1
        return reg

    def get_var_loc(self, var):
        if var in self.val_map:
            return self.val_map[var]

        return None

    def ensure_rd_reg(self, insts):
        if self.are_regs_busy():
            reg = self.get_reg_victim()
            addr = self.alloc_next_mem(reg)
            insts.append(Sw("x0", addr, reg))

    def ensure_var_in_reg(self, var, insts):
        val_loc = self.get_var_loc(var)
        reg = None
        if isinstance(val_loc, int):
            if self.are_regs_busy():
                reg = self.get_reg_victim()
                addr = self.alloc_next_mem(reg)
                insts.append(Sw(reg, addr, "x0"))

            reg = self.alloc_next_reg(var)
            insts.append(Lw("x0", val_loc, reg))
        elif val_loc is None:
            reg = "x0"
        else:
            reg = val_loc
        return reg

    def alloc_addi(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        new_insts.append(Addi(reg_rd, reg_rs1, inst.imm))
        return new_insts

    def alloc_xori(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        new_insts.append(Xori(reg_rd, reg_rs1, inst.imm))
        return new_insts

    def alloc_add(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        reg_rs2 = self.ensure_var_in_reg(inst.rs2, new_insts)
        new_insts.append(Add(reg_rd, reg_rs1, reg_rs2))
        return new_insts

    def alloc_sub(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        reg_rs2 = self.ensure_var_in_reg(inst.rs2, new_insts)
        new_insts.append(Sub(reg_rd, reg_rs1, reg_rs2))
        return new_insts

    def alloc_mul(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        reg_rs2 = self.ensure_var_in_reg(inst.rs2, new_insts)
        new_insts.append(Mul(reg_rd, reg_rs1, reg_rs2))
        return new_insts

    def alloc_div(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        reg_rs2 = self.ensure_var_in_reg(inst.rs2, new_insts)
        new_insts.append(Div(reg_rd, reg_rs1, reg_rs2))
        return new_insts

    def alloc_slt(self, inst):
        new_insts = []
        self.ensure_rd_reg(new_insts)
        reg_rd = self.alloc_next_reg(inst.rd)
        reg_rs1 = self.ensure_var_in_reg(inst.rs1, new_insts)
        reg_rs2 = self.ensure_var_in_reg(inst.rs2, new_insts)
        new_insts.append(Slt(reg_rd, reg_rs1, reg_rs2))
        return new_insts

    def alloc_sw(self, inst):
        pass

    def alloc_lw(self, inst):
        pass

    def optimize(self):
        """
        This function perform register allocation. It maps variables into
        memory, and changes instructions, so that they use one of the following
        registers:
        * x0: always the value zero. Can't change.
        * sp: the stack pointer. Starts with the memory size.
        * ra: the return address.
        * a0: function argument 0 (or return address)
        * a1: function argument 1
        * a2: function argument 2
        * a3: function argument 3

        Notice that next to each register we have suggested a usage. You can,
        of course, write on them and use them in other ways. But, at least x0
        and sp you should not overwrite. The first register you can't overwrite,
        actually. And sp is initialized with the number of memory addresses.
        It's good to use it to control the function stack.

        Examples:
        >>> insts = [Addi("a", "x0", 3)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        3

        >>> insts = [Addi("a", "x0", 1), Slti("b", "a", 2)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3), Slti("b", "a", 2), Xori("c", "b", 5)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        5

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_mem(p.get_val("sp"))
        7

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> insts += [Lw("sp", 0, "b"), Addi("c", "b", 6)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        13

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Add("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 28),Addi("b", "x0", 4),Div("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Mul("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        12

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Xor("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        0

        If you want, you can allocate Jal/Jalr/Beq instructions, but that's not
        necessary for this exercise.

        >>> insts = [Jal("a", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 30), Jalr("b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 3), Addi("b", "a", 0), Beq("a", "b", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_pc()
        30
        """

        new_insts = []
        for inst in self.prog.get_insts():
            action = self.alloc_action[inst.get_opcode()]
            last_insts = action(inst)
            new_insts += last_insts
        self.prog.set_insts(new_insts)
