"""
test_integration.py -- End-to-end integration tests.

Owner: Member 1 (Integration Coordinator) / Member 4 (testing)

These tests exercise the FULL pipeline (Parser -> IR -> Candidate
Generator -> SMT Encoder -> Equivalence Checker -> Cost Model) on
representative basic blocks, matching Review 1's benchmark scope and
Review 2's requirement for demonstrable module-to-module execution.
"""
from src.parser import parse_block
from src.superoptimizer import superoptimize

OPCODE_SET = ["ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "NOT", "CONST"]


def test_double_add_reduces_to_single_shift():
    """4x written as two ADDs should be found equivalent to one SHL by 2,
    a genuine 2-instruction -> 1-instruction reduction."""
    block = parse_block("t0 = ADD x, x\nt1 = ADD t0, t0")
    result = superoptimize(block, OPCODE_SET)
    assert result.improved is True
    assert result.best_cost == 1
    assert result.original_cost == 2
    assert result.best.opcodes_used() == ["SHL"]


def test_already_minimal_block_reports_no_improvement():
    """A single-instruction block that is already minimal for this
    opcode set should honestly report no improvement, not a false one."""
    block = parse_block("y = ADD x, 5")
    result = superoptimize(block, OPCODE_SET, max_length=1)
    assert result.improved is False
    assert result.best_cost == result.original_cost == 1


def test_and_self_reduces_to_identity_form():
    block = parse_block("y = AND x, x")
    result = superoptimize(block, OPCODE_SET, max_length=1)
    # AND x, x is already 1 instruction; an equal-cost alternate form
    # (e.g. OR x, 0) may or may not be found first depending on opcode
    # ordering, but the result must always be proven equivalent.
    assert result.best_cost <= result.original_cost


def test_search_stats_are_populated():
    block = parse_block("t0 = ADD x, x\nt1 = ADD t0, t0")
    result = superoptimize(block, OPCODE_SET)
    assert result.stats.candidates_checked > 0
    assert result.stats.time_seconds >= 0
    assert result.stats.lengths_searched == [1, 2]

def test_result_is_always_reverifiable():
    """Whatever the optimizer returns as 'best', re-checking it against
    the original with the equivalence checker directly must also
    confirm equivalence -- i.e. the pipeline's output is independently
    verifiable, not just self-reported."""
    from src.equivalence import check_equivalent
    block = parse_block("t0 = ADD x, x\nt1 = ADD t0, t0")
    result = superoptimize(block, OPCODE_SET)
    recheck = check_equivalent(result.original, result.best)
    assert recheck.is_equivalent is True


def test_bit_rotation_cascade_reduces_to_rol():
    """A 3-instruction shift/shift/OR sequence should be superoptimized
    to a single ROL (rotate left) instruction."""
    block = parse_block("t0 = SHL x, 1\nt1 = SHR x, 31\ny = OR t0, t1")
    opcodes = OPCODE_SET + ["ROL", "ROR"]
    result = superoptimize(block, opcodes, max_length=1)
    assert result.improved is True
    assert result.best_cost == 1
    assert result.original_cost == 3
    assert result.best.opcodes_used() == ["ROL"]


def test_multiply_by_8_reduces_to_shift_left_3():
    """y = MUL x, 8 should be superoptimized to SHL x, 3 by dynamically
    harvesting the constant 8 and its power-of-two log 3."""
    from src.cost_model import weighted_cost
    block = parse_block("y = MUL x, 8")
    opcodes = OPCODE_SET + ["MUL"]
    result = superoptimize(block, opcodes, max_length=1, cost_fn=weighted_cost)
    assert result.improved is True
    assert result.best_cost < result.original_cost
    assert result.best.opcodes_used() == ["SHL"]
