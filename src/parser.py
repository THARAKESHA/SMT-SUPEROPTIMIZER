"""
parser.py -- Input Parser for the SMT-Based Superoptimizer.

Owner: Member 2 (Core Module 1 / Front-End Owner)

Converts a small, textual assembly-like description of a basic block
into the IR defined in ir.py.

Grammar (informal)
-------------------
    block      := line+
    line       := DST "=" OPCODE operand ("," operand)*
    DST        := identifier
    OPCODE     := one of ir.OPCODES
    operand    := identifier | integer

Example input:
    t0 = ADD x, x
    y  = ADD t0, t0

Rules applied while parsing:
    - A variable is treated as a free INPUT if it is read before it
      is ever assigned.
    - The OUTPUT of the block is the destination of the last
      instruction, unless explicitly overridden.
    - Blank lines and lines starting with '#' are ignored (comments).
"""

from typing import List
from .ir import Instruction, BasicBlock, OPCODES


class ParseError(Exception):
    pass


def _parse_operand(token: str):
    token = token.strip()
    try:
        return int(token)
    except ValueError:
        return token  # treat as a register/variable name


def parse_block(text: str, output_var: str = None) -> BasicBlock:
    instructions: List[Instruction] = []
    defined: set = set()
    inputs: List[str] = []

    for lineno, raw_line in enumerate(text.strip().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        if "=" not in line:
            raise ParseError(f"Line {lineno}: missing '=' in '{raw_line}'")

        dst_part, rhs = line.split("=", 1)
        dst = dst_part.strip()
        rhs = rhs.strip()

        rhs_tokens = rhs.split(None, 1)
        if not rhs_tokens:
            raise ParseError(f"Line {lineno}: missing opcode in '{raw_line}'")
        opcode = rhs_tokens[0].strip().upper()
        if opcode not in OPCODES:
            raise ParseError(f"Line {lineno}: unknown opcode '{opcode}'")

        arg_str = rhs_tokens[1] if len(rhs_tokens) > 1 else ""
        raw_args = [a for a in arg_str.split(",")] if arg_str else []
        args = [_parse_operand(a) for a in raw_args]

        # Track free inputs: any register operand not yet defined.
        for a in args:
            if isinstance(a, str) and a not in defined and a not in inputs:
                inputs.append(a)

        instructions.append(Instruction(dst=dst, op=opcode, args=args))
        defined.add(dst)

    if not instructions:
        raise ParseError("Empty basic block: no instructions parsed.")

    output = output_var if output_var is not None else instructions[-1].dst
    if output not in defined:
        raise ParseError(f"Output variable '{output}' is never assigned.")

    return BasicBlock(instructions=instructions, inputs=inputs, output=output)
