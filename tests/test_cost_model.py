"""Tests for src/cost_model.py -- Member 4's module."""
from src.parser import parse_block
from src.cost_model import simple_cost, weighted_cost


def test_simple_cost_counts_instructions():
    block = parse_block("t0 = ADD x, x\ny = ADD t0, t0")
    assert simple_cost(block) == 2


def test_weighted_cost_penalizes_multiply():
    add_block = parse_block("y = ADD x, x")
    mul_block = parse_block("y = MUL x, 2")
    assert weighted_cost(mul_block) > weighted_cost(add_block)


def test_weighted_cost_matches_simple_for_cheap_ops():
    block = parse_block("y = SHL x, 1")
    assert weighted_cost(block) == simple_cost(block) == 1
