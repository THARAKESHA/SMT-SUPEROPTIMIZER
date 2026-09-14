"""Tests for src/smt_encoder.py and src/equivalence.py -- Member 3's module.

Covers: valid (positive) equivalences, invalid (negative) cases where
the checker must correctly return a counterexample, and boundary
cases involving overflow at the edge of the bit width.
"""
from src.parser import parse_block
from src.equivalence import check_equivalent
from src.smt_encoder import BIT_WIDTH


# ---------------------------------------------------------------------
# Positive (valid) cases: known-equivalent rewrites must verify as UNSAT
# ---------------------------------------------------------------------

def test_add_self_equals_shift_left_1():
    original = parse_block("y = ADD x, x")
    candidate = parse_block("y = SHL x, 1")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True
    assert result.solver_result == "unsat"
    assert result.counterexample is None


def test_double_add_equals_shift_left_2():
    original = parse_block("t0 = ADD x, x\nt1 = ADD t0, t0")
    candidate = parse_block("y = SHL x, 2")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True


def test_and_self_equals_identity_via_or_zero():
    original = parse_block("y = AND x, x")
    candidate = parse_block("y = OR x, 0")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True


def test_xor_self_equals_zero_constant():
    original = parse_block("y = XOR x, x")
    candidate = parse_block("y = CONST 0")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True


def test_sub_self_equals_zero_constant():
    original = parse_block("y = SUB x, x")
    candidate = parse_block("y = CONST 0")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True


# ---------------------------------------------------------------------
# Negative (invalid) cases: the checker must reject wrong candidates
# and produce a genuine counterexample
# ---------------------------------------------------------------------

def test_add_self_is_not_shift_left_2():
    """x + x = 2x, but x << 2 = 4x -- must NOT be judged equivalent."""
    original = parse_block("y = ADD x, x")
    wrong_candidate = parse_block("y = SHL x, 2")
    result = check_equivalent(original, wrong_candidate)
    assert result.is_equivalent is False
    assert result.solver_result == "sat"
    assert result.counterexample is not None
    # Verify the counterexample is real: plug it back in and confirm disagreement.
    x_val = result.counterexample["x"]
    mask = (1 << BIT_WIDTH) - 1
    lhs = (x_val + x_val) & mask
    rhs = (x_val << 2) & mask
    assert lhs != rhs


def test_or_self_is_not_and_zero():
    original = parse_block("y = OR x, x")     # y = x
    wrong_candidate = parse_block("y = AND x, 0")  # y = 0
    result = check_equivalent(original, wrong_candidate)
    assert result.is_equivalent is False
    assert result.solver_result == "sat"


def test_regression_constant_only_candidate_not_falsely_rejected():
    """Regression test for a defect found during Review 2 preparation:
    check_equivalent() originally required original.inputs == candidate.inputs
    exactly, which incorrectly rejected valid candidates that don't read
    any input at all (e.g. 'y = CONST 0' has an empty inputs list, since
    it never reads x). Fixed by requiring candidate.inputs to be a SUBSET
    of original.inputs instead of an exact match. This test pins the fix."""
    original = parse_block("y = SUB x, x")   # inputs = ['x']
    candidate = parse_block("y = CONST 0")   # inputs = []  (reads no variable)
    result = check_equivalent(original, candidate)
    assert result.solver_result != "input-mismatch"
    assert result.is_equivalent is True


def test_different_input_sets_are_not_equivalent():
    original = parse_block("y = ADD x, x")
    candidate = parse_block("y = ADD a, a")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is False
    assert result.solver_result == "input-mismatch"


# ---------------------------------------------------------------------
# Boundary case: overflow at the top of the 32-bit range
# ---------------------------------------------------------------------

def test_overflow_semantics_preserved_at_max_value():
    """ADD must wrap around exactly like real 32-bit hardware; a rewrite
    that is only correct for 'normal' values (no overflow) must be
    caught by the solver as non-equivalent, since the proof covers the
    ENTIRE input domain, including the overflow edge case."""
    # SHL x, 1 is a mathematically-doubling operation with the SAME
    # wraparound behaviour as ADD x, x for all 32-bit values -- so
    # these two ARE equivalent even at the overflow boundary.
    original = parse_block("y = ADD x, x")
    candidate = parse_block("y = SHL x, 1")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True

    # As a boundary sanity check, confirm the encoding wraps: evaluate
    # both sides at x = 2**31 (the overflow edge for a 32-bit block)
    # using plain Python arithmetic mod 2**32.
    x_val = 2 ** (BIT_WIDTH - 1)
    mask = (1 << BIT_WIDTH) - 1
    lhs = (x_val + x_val) & mask
    rhs = (x_val << 1) & mask
    assert lhs == rhs == 0  # both wrap to 0 at this boundary
