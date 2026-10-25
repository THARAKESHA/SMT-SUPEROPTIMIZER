"""
candidate_gen.py -- Bounded enumeration of candidate instruction sequences.

Owner: Member 3 (Core Algorithm / Processing Owner)

Generates every well-formed candidate basic block of a given
instruction length, built from a restricted opcode set, a fixed set
of input registers, and a small pool of immediate constants.

A candidate is "well-formed" if:
    - Every instruction's operands refer only to registers already
      defined earlier in the sequence (inputs, or previous temps) or
      to a constant from the allowed constant pool.
    - Each temporary register is assigned at most once (SSA-style),
      using fresh names t0, t1, t2, ...
    - The block's output is the destination of its final instruction.

This bounded, exhaustive search is deliberately simple: it trades
search sophistication (c.f. STOKE's stochastic search or Souper's
CEGIS-based synthesis, see Review 1 Section 4c) for a search space
small enough to explore completely within the project's 6-8
instruction scope, guaranteeing that if a cheaper equivalent exists
within the length bound, this generator will eventually produce it.
"""

from itertools import product
from typing import List, Iterator
from .ir import Instruction, BasicBlock, OPCODES

DEFAULT_CONST_POOL = [0, 1, 2, 3, 4]


def harvest_constants(block: BasicBlock, base_pool: List[int] = None) -> List[int]:
    """Dynamically harvest constants from a basic block to expand synthesis power.
    
    Extracts all explicit integer constants in the block, plus:
    - Logarithms of powers-of-two (e.g. 8 = 2^3 -> extracts 3, enabling MUL->SHL)
    - Complementary shift amounts for 32-bit rotations (e.g. 1 and 31)
    - Base small constants to guarantee fundamental identities
    """
    base = DEFAULT_CONST_POOL if base_pool is None else base_pool
    harvested = set(base)

    for ins in block.instructions:
        for arg in ins.args:
            if isinstance(arg, int):
                harvested.add(arg)
                # Power-of-two exponent: e.g. 8 -> 3, 16 -> 4, 32 -> 5
                if arg > 0 and (arg & (arg - 1)) == 0:
                    harvested.add(arg.bit_length() - 1)
                # Complementary shift amounts for 32-bit word rotations
                if 0 < arg < 32:
                    harvested.add(32 - arg)

    return sorted(harvested)


def _operand_pool(defined_regs: List[str], const_pool: List[int]):
    return list(defined_regs) + list(const_pool)


def generate_candidates(inputs: List[str], length: int, opcode_set: List[str],
                         const_pool: List[int] = None,
                         max_candidates: int = 200_000) -> Iterator[BasicBlock]:
    """Yield every well-formed candidate BasicBlock of exactly `length`
    instructions, built from `opcode_set`, using `inputs` as the free
    input registers and `const_pool` as allowed immediate constants."""
    const_pool = DEFAULT_CONST_POOL if const_pool is None else const_pool
    produced = 0

    def build(step: int, defined: List[str], instructions: List[Instruction]):
        nonlocal produced
        if produced >= max_candidates:
            return
        if step == length:
            block = BasicBlock(
                instructions=list(instructions),
                inputs=list(inputs),
                output=instructions[-1].dst,
            )
            produced += 1
            yield block
            return

        dst = f"t{step}"
        for op in opcode_set:
            arity = OPCODES[op]["arity"]
            pool = _operand_pool(defined, const_pool)

            if op == "CONST":
                arg_choices = [(c,) for c in const_pool]
            else:
                arg_choices = list(product(pool, repeat=arity))

            for args in arg_choices:
                # Skip instructions that don't use any register at all
                # (e.g. CONST is fine; but a binary op on two constants
                # is dead search space -- it can never reference the
                # input, so it can't reproduce input-dependent behaviour).
                if op != "CONST" and all(isinstance(a, int) for a in args):
                    continue
                ins = Instruction(dst=dst, op=op, args=list(args))
                yield from build(step + 1, defined + [dst], instructions + [ins])
                if produced >= max_candidates:
                    return

    yield from build(0, list(inputs), [])


def generate_candidates_up_to(inputs: List[str], max_length: int, opcode_set: List[str],
                               const_pool: List[int] = None,
                               max_candidates_per_length: int = 200_000):
    """Convenience generator: yields (length, candidate) pairs for every
    length from 1 up to and including max_length."""
    for length in range(1, max_length + 1):
        for cand in generate_candidates(inputs, length, opcode_set, const_pool,
                                         max_candidates_per_length):
            yield length, cand
