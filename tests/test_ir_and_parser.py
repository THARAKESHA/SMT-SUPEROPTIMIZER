"""Tests for src/ir.py and src/parser.py -- Member 2's module."""
import pytest
from src.ir import Instruction, BasicBlock
from src.parser import parse_block, ParseError


def test_instruction_valid_binary():
    ins = Instruction(dst="y", op="ADD", args=["x", "x"])
    assert str(ins) == "y = ADD x, x"


def test_instruction_wrong_arity_raises():
    with pytest.raises(ValueError):
        Instruction(dst="y", op="ADD", args=["x"])  # ADD needs 2 operands


def test_instruction_unknown_opcode_raises():
    with pytest.raises(ValueError):
        Instruction(dst="y", op="FROB", args=["x", "x"])


def test_parse_single_instruction_block():
    block = parse_block("y = ADD x, x")
    assert block.inputs == ["x"]
    assert block.output == "y"
    assert block.instruction_count() == 1


def test_parse_multi_instruction_block_infers_inputs_and_output():
    text = """
    t0 = ADD x, x
    y  = ADD t0, t0
    """
    block = parse_block(text)
    assert block.inputs == ["x"]          # x is the only free variable
    assert block.output == "y"            # last instruction's dst
    assert block.instruction_count() == 2


def test_parse_ignores_comments_and_blank_lines():
    text = """
    # this is a comment
    y = ADD x, x

    """
    block = parse_block(text)
    assert block.instruction_count() == 1


def test_parse_missing_equals_raises():
    with pytest.raises(ParseError):
        parse_block("y ADD x, x")


def test_parse_unknown_opcode_raises():
    with pytest.raises(ParseError):
        parse_block("y = FROB x, x")


def test_parse_empty_block_raises():
    with pytest.raises(ParseError):
        parse_block("")


def test_parse_undefined_output_raises():
    with pytest.raises(ParseError):
        parse_block("t0 = ADD x, x", output_var="y")  # y never assigned
