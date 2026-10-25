"""Tests for src/candidate_gen.py -- Member 3's module."""
from src.candidate_gen import generate_candidates, generate_candidates_up_to, harvest_constants
from src.parser import parse_block


def test_generate_length1_candidates_nonempty():
    cands = list(generate_candidates(["x"], length=1, opcode_set=["ADD", "SHL", "CONST"]))
    assert len(cands) > 0
    assert all(c.instruction_count() == 1 for c in cands)


def test_generate_length1_includes_known_target():
    """SHL x, 1 must appear among the length-1 candidates for input x."""
    cands = list(generate_candidates(["x"], length=1, opcode_set=["SHL"]))
    strs = [str(c) for c in cands]
    assert any("SHL x, 1" in s for s in strs)


def test_generate_skips_input_independent_candidates():
    """A binary op on two constants (e.g. ADD 1, 2) can never depend on
    the input, so it must be pruned from the search space."""
    cands = list(generate_candidates(["x"], length=1, opcode_set=["ADD"], const_pool=[1, 2]))
    for c in cands:
        ins = c.instructions[0]
        assert not all(isinstance(a, int) for a in ins.args)


def test_generate_respects_max_candidates_cap():
    cands = list(generate_candidates(["x"], length=2, opcode_set=["ADD", "SUB", "AND", "OR", "XOR"],
                                      const_pool=[0, 1, 2, 3, 4], max_candidates=50))
    assert len(cands) <= 50


def test_generate_up_to_covers_all_lengths():
    pairs = list(generate_candidates_up_to(["x"], max_length=2, opcode_set=["ADD"], const_pool=[0, 1]))
    lengths_seen = {length for length, _ in pairs}
    assert lengths_seen == {1, 2}


def test_harvest_constants_extracts_literals_and_powers():
    block = parse_block("y = MUL x, 8")
    harvested = harvest_constants(block)
    assert 8 in harvested
    assert 3 in harvested  # log2(8) == 3


def test_harvest_constants_extracts_rotation_complements():
    block = parse_block("t0 = SHL x, 1\nt1 = SHR x, 31\ny = OR t0, t1")
    harvested = harvest_constants(block)
    assert 1 in harvested
    assert 31 in harvested

