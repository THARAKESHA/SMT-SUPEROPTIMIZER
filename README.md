# SMT-Based Superoptimizer

BCSE307 Compiler Design — Project ID CD-SMT-01

A working prototype that searches for provably optimal instruction
sequences for small basic blocks, using the Z3 SMT solver to formally
verify semantic equivalence (not just test it).

## What this does

Given a small basic block such as:

```
t0 = ADD x, x
t1 = ADD t0, t0
```

the tool searches bounded-length candidate instruction sequences,
proves candidates equivalent to the original using Z3, and returns
the cheapest **proven-equivalent** replacement it finds — in this
case:

```
t0 = SHL x, 2
```

reducing a 2-instruction block to 1 instruction, with a formal
guarantee that the rewrite is correct for **every** possible 32-bit
input, not just tested ones.

## Project structure

```
smt_superoptimizer/
├── src/
│   ├── ir.py              # IR data structures (Member 2)
│   ├── parser.py           # Text -> IR parser (Member 2)
│   ├── candidate_gen.py    # Bounded candidate enumeration (Member 3)
│   ├── smt_encoder.py      # IR -> Z3 bitvector expressions (Member 3)
│   ├── equivalence.py      # UNSAT-based equivalence checking (Member 3)
│   ├── cost_model.py       # simple_cost / weighted_cost (Member 4)
│   └── superoptimizer.py   # End-to-end pipeline (Member 1 / 4)
├── tests/
│   ├── test_ir_and_parser.py
│   ├── test_candidate_gen.py
│   ├── test_equivalence.py
│   ├── test_cost_model.py
│   └── test_integration.py
├── benchmarks/
│   └── blocks.txt           # Benchmark basic blocks used by run_demo.py
├── run_demo.py               # CLI: runs the full pipeline on the benchmarks
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ and the `z3-solver` package.

## Running the tests

```bash
python3 -m pytest tests/ -v
```

33 tests covering: valid (positive) equivalences, invalid (negative)
cases with real counterexamples, a boundary/overflow case, candidate
generation correctness, cost model behaviour, and full end-to-end
integration — including a regression test for a real defect found and
fixed during development (see "Known defect log" below).

## Running the live demo

```bash
python3 run_demo.py
```

Runs the full pipeline (Parser → IR → Candidate Generator → SMT
Encoder → Equivalence Checker → Cost Model) on every block in
`benchmarks/blocks.txt` and prints a results table: original cost,
best proven-equivalent cost found, whether it improved, how many
candidates were checked, and solve time.

## Known defect log

| Defect | Found | Cause | Fix | Regression test |
|---|---|---|---|---|
| `check_equivalent()` incorrectly rejected valid candidates that read no input variable at all (e.g. `y = CONST 0`) | During Review 2 test-suite development | Equivalence checker required `original.inputs == candidate.inputs` exactly; a constant-only candidate legitimately has an empty inputs list | Changed the check to require `candidate.inputs ⊆ original.inputs` (a candidate may use fewer inputs than the original, never more) | `test_regression_constant_only_candidate_not_falsely_rejected` in `tests/test_equivalence.py` |

## Current scope and limitations

- Basic blocks only (no branches or loops) — matches Review 1 scope.
- 32-bit fixed-width bitvector arithmetic.
- Opcode set: ADD, SUB, AND, OR, XOR, SHL, SHR, NOT, NEG, MUL, CONST.
- Candidate search is bounded by block length and a small constant
  pool (0–4) to keep each Z3 query small; this is an exhaustive
  search within that bound, not a heuristic one.
- Cost model provided in two forms: `simple_cost` (instruction count)
  and `weighted_cost` (rough estimated-cycle weighting that penalizes
  MUL relative to ADD/shift/bitwise ops).

## Pending for Review 3

- Extend candidate generator / cost model tuning for larger benchmark
  coverage (Hacker's Delight bit-trick set).
- Add performance benchmarking across increasing block lengths.
- Package results into the final comparison table and report.
