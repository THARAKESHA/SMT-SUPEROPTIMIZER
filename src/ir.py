"""
ir.py -- Intermediate Representation for the SMT-Based Superoptimizer.

Owner: Member 2 (Core Module 1 / Front-End Owner)

Defines the data structures used to represent a small, straight-line
basic block: a sequence of three-address-code style instructions
operating on named registers and small integer constants.

Design notes
------------
- Every instruction has the form:  dst = OP arg1 [, arg2]
- Registers are simple string names (e.g. "x", "t0", "y").
- Operands (`args`) are either register names (str) or integer
  constants (int).
- A BasicBlock is single-entry, single-exit, straight-line code:
  no branches, no loops. This matches the project's stated scope
  (Review 1, Section 3: Objectives, Scope and Limitations).
"""

from dataclasses import dataclass, field
from typing import List, Union, Dict

Operand = Union[str, int]

# Opcodes supported by this prototype, with their arity (number of
# operands) and a short human-readable description. This table is the
# single source of truth used by the parser, candidate generator and
# SMT encoder -- adding a new opcode means adding one row here plus
# one case in smt_encoder.encode_instruction.
OPCODES: Dict[str, dict] = {
    "ADD":   {"arity": 2, "desc": "bitvector addition"},
    "SUB":   {"arity": 2, "desc": "bitvector subtraction"},
    "AND":   {"arity": 2, "desc": "bitwise AND"},
    "OR":    {"arity": 2, "desc": "bitwise OR"},
    "XOR":   {"arity": 2, "desc": "bitwise XOR"},
    "SHL":   {"arity": 2, "desc": "logical shift left"},
    "SHR":   {"arity": 2, "desc": "logical shift right"},
    "NOT":   {"arity": 1, "desc": "bitwise NOT"},
    "NEG":   {"arity": 1, "desc": "two's-complement negation"},
    "MUL":   {"arity": 2, "desc": "bitvector multiplication"},
    "CONST": {"arity": 1, "desc": "load an immediate constant"},
}


@dataclass(frozen=True)
class Instruction:
    dst: str
    op: str
    args: List[Operand] = field(default_factory=list)

    def __post_init__(self):
        if self.op not in OPCODES:
            raise ValueError(f"Unknown opcode: {self.op}")
        expected = OPCODES[self.op]["arity"]
        if len(self.args) != expected:
            raise ValueError(
                f"Opcode {self.op} expects {expected} operand(s), "
                f"got {len(self.args)}: {self.args}"
            )

    def __str__(self):
        args_str = ", ".join(str(a) for a in self.args)
        return f"{self.dst} = {self.op} {args_str}"


@dataclass(frozen=True)
class BasicBlock:
    instructions: List[Instruction]
    inputs: List[str]     # names of free input variables
    output: str           # name of the register holding the block's result

    def __str__(self):
        lines = [str(ins) for ins in self.instructions]
        return "\n".join(lines)

    def instruction_count(self) -> int:
        return len(self.instructions)

    def opcodes_used(self) -> List[str]:
        return [ins.op for ins in self.instructions]
