#!/usr/bin/env python3
"""
run_demo.py -- Live demonstration script for Review 2.

Runs the full pipeline (Parser -> IR -> Candidate Generator ->
SMT Encoder -> Equivalence Checker -> Cost Model) on every benchmark
block in benchmarks/blocks.txt and prints a results table.

Usage:
    python3 run_demo.py
"""
import time
from src.parser import parse_block
from src.superoptimizer import superoptimize
from src.cost_model import weighted_cost

OPCODE_SET = ["ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "NOT", "CONST", "MUL", "ROL", "ROR"]


def load_benchmarks(path: str):
    with open(path) as f:
        text = f.read()
    sections = text.split("@@@")
    blocks = []
    for section in sections:
        lines = [ln for ln in section.splitlines()]
        comment_lines = [ln.strip("# ").strip() for ln in lines if ln.strip().startswith("#")]
        code_lines = [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]
        if not code_lines:
            continue
        name = comment_lines[-1] if comment_lines else "unnamed block"
        blocks.append((name, "\n".join(code_lines)))
    return blocks


def main():
    benchmarks = load_benchmarks("benchmarks/blocks.txt")

    print(f"{'Benchmark':38} {'Orig':>5} {'Best':>5} {'Improved?':>10} {'Checked':>8} {'Time(s)':>8}")
    print("-" * 80)

    total_start = time.time()
    improved_count = 0

    for name, text in benchmarks:
        block = parse_block(text)
        result = superoptimize(block, OPCODE_SET, cost_fn=weighted_cost)
        improved_count += 1 if result.improved else 0
        print(f"{name[:38]:38} {result.original_cost:5d} {result.best_cost:5d} "
              f"{str(result.improved):>10} {result.stats.candidates_checked:8d} "
              f"{result.stats.time_seconds:8.3f}")
        print(f"    original : {str(result.original).replace(chr(10), ' ; ')}")
        print(f"    best     : {str(result.best).replace(chr(10), ' ; ')}")
        print()

    total_elapsed = time.time() - total_start
    print("-" * 80)
    print(f"Benchmarks run: {len(benchmarks)}   Improved: {improved_count}   "
          f"Total time: {total_elapsed:.3f}s")


if __name__ == "__main__":
    main()
