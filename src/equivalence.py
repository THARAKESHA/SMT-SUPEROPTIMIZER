"""
equivalence.py -- Formal equivalence checking between two basic blocks.

Owner: Member 3 (Core Algorithm / Processing Owner)

This is the module that gives the project its correctness guarantee.
Two blocks P1 and P2 are semantically equivalent iff, for every
possible assignment of the shared input variables, they produce the
same output value. Rather than testing this on sample inputs, we ask
Z3 to prove it directly:

    assert  NOT( P1(x) == P2(x) )
    check satisfiability

  - UNSAT  => no input exists on which they disagree => PROVEN EQUIVALENT
  - SAT    => the solver's model IS a counterexample  => NOT EQUIVALENT

This is the same technique used by Denali (2002) and, in a more
elaborate form, by Souper -- see Review 1, Section 4c (Related
Approaches in Depth).
"""

from dataclasses import dataclass
from typing import Optional, Dict
from z3 import Solver, Not, sat, unsat

from .ir import BasicBlock
from .smt_encoder import make_input_vars, encode_block, BIT_WIDTH


@dataclass
class EquivResult:
    is_equivalent: bool
    counterexample: Optional[Dict[str, int]]
    solver_result: str  # "unsat" (proven equal) or "sat" (proven different)


def check_equivalent(original: BasicBlock, candidate: BasicBlock,
                      width: int = BIT_WIDTH) -> EquivResult:
    """Formally verify whether `candidate` is semantically equivalent to
    `original` for ALL possible inputs, using a single Z3 query."""

    if not set(candidate.inputs).issubset(set(original.inputs)):
        # A candidate is only comparable if every free variable it reads
        # is one of the original's inputs. (The reverse is fine: a
        # candidate that happens not to use some input at all -- e.g.
        # "y = CONST 0" -- is a legitimate rewrite, not a mismatch.)
        return EquivResult(is_equivalent=False, counterexample=None,
                            solver_result="input-mismatch")

    # Build the shared symbolic environment over the ORIGINAL's input
    # set (a superset of the candidate's), so both blocks are encoded
    # against the same variables even if the candidate ignores some of them.
    input_vars = make_input_vars(original.inputs, width)

    orig_expr = encode_block(original, input_vars, width)
    cand_expr = encode_block(candidate, input_vars, width)

    solver = Solver()
    solver.add(Not(orig_expr == cand_expr))
    result = solver.check()

    if result == unsat:
        return EquivResult(is_equivalent=True, counterexample=None,
                            solver_result="unsat")

    if result == sat:
        model = solver.model()
        counterexample = {
            name: model.eval(var, model_completion=True).as_long()
            for name, var in input_vars.items()
        }
        return EquivResult(is_equivalent=False, counterexample=counterexample,
                            solver_result="sat")

    # 'unknown' -- solver could not decide within resource limits.
    return EquivResult(is_equivalent=False, counterexample=None,
                        solver_result="unknown")
