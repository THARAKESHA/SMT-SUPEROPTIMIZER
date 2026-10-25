"""
smt_encoder.py -- Translates IR basic blocks into Z3 bitvector expressions.

Owner: Member 3 (Core Algorithm / Processing Owner)

This module performs symbolic execution of a BasicBlock: instead of
running the block on concrete inputs, it runs it on symbolic Z3
BitVec variables, producing a single Z3 expression that represents
the value of the block's output register as a function of its
inputs. Two blocks are semantically equivalent iff their output
expressions agree for every possible input -- this is exactly what
equivalence.py checks using this module's output.

Bit width
---------
BIT_WIDTH = 32, matching standard 32-bit machine registers. Using a
bitvector theory (as opposed to plain mathematical integers) is what
makes the model faithful to real hardware: overflow wraps around
exactly as it would on a physical machine, which is the correct
semantics for a peephole optimizer to preserve.
"""

from z3 import BitVec, BitVecVal, BitVecRef
from .ir import BasicBlock, Instruction

BIT_WIDTH = 32


def make_input_vars(names, width: int = BIT_WIDTH) -> dict:
    """Create one fresh Z3 BitVec per input name."""
    return {name: BitVec(name, width) for name in names}


def _as_expr(operand, env: dict, width: int = BIT_WIDTH):
    """Resolve an operand (register name or int constant) to a Z3 expr."""
    if isinstance(operand, int):
        return BitVecVal(operand, width)
    if operand not in env:
        raise KeyError(f"Use of undefined register '{operand}' before assignment.")
    return env[operand]


def encode_instruction(ins: Instruction, env: dict, width: int = BIT_WIDTH):
    """Compute the Z3 expression produced by a single instruction, given
    the current environment mapping register name -> Z3 expression."""
    op = ins.op

    if op == "CONST":
        (a,) = ins.args
        result = BitVecVal(a, width)

    elif op in ("NOT", "NEG"):
        (a,) = ins.args
        a_expr = _as_expr(a, env, width)
        result = (~a_expr) if op == "NOT" else (-a_expr)

    else:
        a, b = ins.args
        a_expr = _as_expr(a, env, width)
        b_expr = _as_expr(b, env, width)
        if op == "ADD":
            result = a_expr + b_expr
        elif op == "SUB":
            result = a_expr - b_expr
        elif op == "AND":
            result = a_expr & b_expr
        elif op == "OR":
            result = a_expr | b_expr
        elif op == "XOR":
            result = a_expr ^ b_expr
        elif op == "SHL":
            result = a_expr << b_expr
        elif op == "SHR":
            result = z3_lshr(a_expr, b_expr)
        elif op == "MUL":
            result = a_expr * b_expr
        elif op == "ROL":
            result = z3_rotate_left(a_expr, b_expr)
        elif op == "ROR":
            result = z3_rotate_right(a_expr, b_expr)
        else:
            raise ValueError(f"No SMT encoding defined for opcode '{op}'")

    return result


def z3_lshr(a_expr, b_expr):
    """Logical (unsigned) shift-right -- explicit helper so the intent
    (unsigned shift, matching typical peephole-optimization semantics)
    is documented at the call site."""
    from z3 import LShR
    return LShR(a_expr, b_expr)


def z3_rotate_left(a_expr, b_expr):
    """Bitvector rotate left."""
    from z3 import RotateLeft
    return RotateLeft(a_expr, b_expr)


def z3_rotate_right(a_expr, b_expr):
    """Bitvector rotate right."""
    from z3 import RotateRight
    return RotateRight(a_expr, b_expr)


def encode_block(block: BasicBlock, input_vars: dict, width: int = BIT_WIDTH) -> BitVecRef:
    """Symbolically execute `block` given a mapping of input-register
    name -> Z3 BitVec, returning the Z3 expression for block.output."""
    env = dict(input_vars)
    for ins in block.instructions:
        env[ins.dst] = encode_instruction(ins, env, width)
    if block.output not in env:
        raise KeyError(f"Output register '{block.output}' was never assigned.")
    return env[block.output]
