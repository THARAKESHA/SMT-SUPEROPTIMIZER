"""
cost_model.py -- Cost metrics for ranking proven-equivalent candidates.

Owner: Member 4 (Testing / Interface / Documentation Owner)

Z3 proving a candidate correct (see equivalence.py) tells us nothing
about whether it is better than the original -- multiple candidates
can all be proven equivalent. The cost model provides the ranking
used to pick the best one among them.

Two metrics are provided:
    simple_cost    -- instruction count (the default; easy to reason
                       about and to defend in viva).
    weighted_cost  -- a rough estimated-cycle-cost model, weighting
                       cheap bitwise/shift ops less than multiplication.
"""

from .ir import BasicBlock

# Rough relative cost per opcode, used only by weighted_cost().
# These are illustrative estimates, not a calibrated hardware model.
OPCODE_WEIGHT = {
    "ADD": 1, "SUB": 1, "AND": 1, "OR": 1, "XOR": 1,
    "SHL": 1, "SHR": 1, "NOT": 1, "NEG": 1, "CONST": 1,
    "MUL": 3,
}


def simple_cost(block: BasicBlock) -> int:
    """Cost = number of instructions in the block."""
    return block.instruction_count()


def weighted_cost(block: BasicBlock) -> int:
    """Cost = sum of per-opcode estimated-cycle weights."""
    return sum(OPCODE_WEIGHT.get(ins.op, 1) for ins in block.instructions)
