#!/usr/bin/env python3
"""
run_demo.py -- Live demonstration script for Review 2 & Review 3.

Runs the full pipeline (Parser -> IR -> Candidate Generator ->
SMT Encoder -> Equivalence Checker -> Cost Model) on every benchmark
block in benchmarks/blocks.txt and prints a results table.

Usage:
    python run_demo.py              # Uses persistent cache (instant 0.000s warm run)
    python run_demo.py --cold       # Disables cache (runs full synthesis from scratch ~2.8s)
    python run_demo.py --interactive# Launches interactive live REPL shell
"""
import sys
import time
from src.parser import parse_block
from src.superoptimizer import superoptimize
from src.cost_model import weighted_cost
from src.cache import OptimizationCache

OPCODE_SET = ["ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "NOT", "CONST", "MUL", "ROL", "ROR", "SEL"]


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


def interactive_shell():
    print("=" * 72)
    print("   SMT-Based Superoptimizer -- Interactive Live REPL")
    print("   Type instructions line-by-line (e.g. 't0 = ADD x, x').")
    print("   Press Enter on an empty line to optimize. Type 'quit' to exit.")
    print("=" * 72)
    cache = OptimizationCache()

    while True:
        try:
            print("\nEnter basic block:")
            lines = []
            while True:
                line = input("  > ").strip()
                if line.lower() in ("quit", "exit"):
                    print("Exiting interactive shell.")
                    return
                if line.lower() == "run" or (not line and lines):
                    break
                if not line:
                    continue
                lines.append(line)

            code = "\n".join(lines)
            block = parse_block(code)
            print(f"\n[+] Analyzing block: inputs={block.inputs}, output={block.output}")

            result = superoptimize(block, OPCODE_SET, cost_fn=weighted_cost, cache=cache)
            print("-" * 55)
            print(f"  Original Cost : {result.original_cost} cycles")
            print(f"  Optimal Cost  : {result.best_cost} cycles")
            print(f"  Improved?     : {result.improved}")
            print(f"  Checked       : {result.stats.candidates_checked} candidate(s)")
            print(f"  Solve Time    : {result.stats.time_seconds:.4f}s")
            print("-" * 55)
            print("Optimal Proven Replacement:")
            for ins in result.best.instructions:
                print(f"  {ins}")
            print("-" * 55)

        except KeyboardInterrupt:
            print("\nExiting.")
            return
        except Exception as e:
            print(f"[!] Error: {e}")


def main():
    no_cache = "--no-cache" in sys.argv or "--cold" in sys.argv
    benchmarks = load_benchmarks("benchmarks/blocks.txt")
    cache = None if no_cache else OptimizationCache()

    mode_label = "COLD RUN (Full Synthesis from Scratch - No Cache)" if no_cache else "WARM RUN (Persistent Cache Memoization)"
    print("=" * 80)
    print(f"  MODE: {mode_label}")
    print("=" * 80)
    print(f"{'Benchmark':38} {'Orig':>5} {'Best':>5} {'Improved?':>10} {'Checked':>8} {'Time(s)':>8}")
    print("-" * 80)

    total_start = time.time()
    improved_count = 0

    for name, text in benchmarks:
        block = parse_block(text)
        result = superoptimize(block, OPCODE_SET, cost_fn=weighted_cost, cache=cache)
        improved_count += 1 if result.improved else 0
        print(f"{name[:38]:38} {result.original_cost:5d} {result.best_cost:5d} "
              f"{str(result.improved):>10} {result.stats.candidates_checked:8d} "
              f"{result.stats.time_seconds:8.3f}")
        print(f"    original : {str(result.original).replace(chr(10), ' ; ')}")
        print(f"    best     : {str(result.best).replace(chr(10), ' ; ')}")
        print()

    total_elapsed = time.time() - total_start
    print("-" * 80)
    hits = cache.hits if cache else 0
    print(f"Benchmarks run: {len(benchmarks)}   Improved: {improved_count}   "
          f"Total time: {total_elapsed:.3f}s   Cache hits: {hits}")


if __name__ == "__main__":
    if "--interactive" in sys.argv or "-i" in sys.argv:
        interactive_shell()
    else:
        main()
