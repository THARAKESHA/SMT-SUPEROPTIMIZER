"""
superoptimizer.py -- End-to-end integration of the full pipeline.

Owner: Member 1 (Integration Coordinator) with Member 4 (testing/wiring)

Wires together every module built by the team into the pipeline
described in Review 1, Section 6 (Proposed Methodology) and
Section 7 (Architecture and Data Flow):

    Input Parser -> IR -> Candidate Generator -> SMT Encoder
                  -> Equivalence Checker (Z3) -> Cost Model -> Output

Given an already-parsed BasicBlock, `superoptimize()` searches for the
lowest-cost instruction sequence that is *formally proven* equivalent
to it, searching candidate lengths from 1 up to the original block's
own length (an optimization can never need to be longer than what it
is replacing, for this project's scope).
"""

import time
from dataclasses import dataclass
from typing import List, Optional

from .ir import BasicBlock
from .candidate_gen import generate_candidates_up_to, harvest_constants
from .equivalence import check_equivalent
from .cost_model import simple_cost


@dataclass
class SearchStats:
    candidates_checked: int
    time_seconds: float
    lengths_searched: List[int]


@dataclass
class SuperoptResult:
    original: BasicBlock
    best: BasicBlock
    improved: bool
    original_cost: int
    best_cost: int
    stats: SearchStats


def superoptimize(block: BasicBlock, opcode_set: List[str],
                   max_length: Optional[int] = None,
                   const_pool: Optional[List[int]] = None,
                   cost_fn=simple_cost) -> SuperoptResult:
    """Search for a proven-equivalent, lower-cost replacement for `block`.

    Returns a SuperoptResult describing the best block found (which may
    simply be the original, if no cheaper proven-equivalent candidate
    exists within the search bound -- this is a legitimate, honest
    outcome, not a failure of the tool)."""
    start = time.time()
    max_length = max_length if max_length is not None else block.instruction_count()
    const_pool = harvest_constants(block) if const_pool is None else const_pool

    best = block
    best_cost = cost_fn(block)
    checked = 0
    lengths_searched = list(range(1, max_length + 1))

    for length, candidate in generate_candidates_up_to(
        block.inputs, max_length, opcode_set, const_pool
    ):
        checked += 1
        cand_cost = cost_fn(candidate)
        if cand_cost >= best_cost:
            # No point formally verifying a candidate that couldn't
            # possibly improve on the current best -- cheap pruning
            # before the expensive Z3 call.
            continue

        result = check_equivalent(block, candidate)
        if result.is_equivalent:
            best = candidate
            best_cost = cand_cost

    elapsed = time.time() - start
    return SuperoptResult(
        original=block,
        best=best,
        improved=(best is not block),
        original_cost=cost_fn(block),
        best_cost=best_cost,
        stats=SearchStats(candidates_checked=checked, time_seconds=elapsed,
                           lengths_searched=lengths_searched),
    )
