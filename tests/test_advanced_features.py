"""Tests for advanced features: Caching, Commutative Symmetry Breaking, and SEL opcode."""
import os
from src.parser import parse_block
from src.equivalence import check_equivalent
from src.candidate_gen import generate_candidates
from src.superoptimizer import superoptimize
from src.cache import OptimizationCache


def test_commutative_symmetry_breaking_prunes_candidates():
    """For commutative op ADD, combinations_with_replacement generates fewer candidates
    than non-commutative op SUB on the same operand pool."""
    cands_add = list(generate_candidates(["x"], length=1, opcode_set=["ADD"], const_pool=[0, 1, 2]))
    cands_sub = list(generate_candidates(["x"], length=1, opcode_set=["SUB"], const_pool=[0, 1, 2]))
    # Symmetric pairs like (0, 1) and (1, 0) are collapsed for ADD, so ADD candidates < SUB candidates
    assert len(cands_add) < len(cands_sub)


def test_select_true_condition_equals_first_operand():
    """y = SEL 1, a, b should evaluate identically to y = a."""
    original = parse_block("y = SEL 1, a, b")
    candidate = parse_block("y = ADD a, 0")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True
    assert result.solver_result == "unsat"


def test_select_false_condition_equals_second_operand():
    """y = SEL 0, a, b should evaluate identically to y = b."""
    original = parse_block("y = SEL 0, a, b")
    candidate = parse_block("y = ADD b, 0")
    result = check_equivalent(original, candidate)
    assert result.is_equivalent is True
    assert result.solver_result == "unsat"


def test_optimization_cache_hit_returns_instant_result(tmp_path):
    """Cache should record a proven optimization and return an instant hit on subsequent queries."""
    cache_file = str(tmp_path / "test_cache.json")
    cache = OptimizationCache(cache_file=cache_file)
    block = parse_block("t0 = ADD x, x\nt1 = ADD t0, t0")

    # First run: cache miss, runs full synthesis
    res1 = superoptimize(block, ["ADD", "SHL"], cache=cache)
    assert res1.improved is True
    assert cache.misses == 1
    assert cache.hits == 0

    # Second run: cache hit, instantaneous return
    res2 = superoptimize(block, ["ADD", "SHL"], cache=cache)
    assert res2.improved is True
    assert res2.best_cost == res1.best_cost
    assert cache.hits == 1
    assert res2.stats.time_seconds == 0.0
