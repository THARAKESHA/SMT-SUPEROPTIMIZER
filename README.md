# SMT-Based Superoptimizer

**BCSE307 Compiler Design — Project ID CD-SMT-01**  
**Team Number: A13** | **Review 3 Final Release**  
Live GitHub Repository: [https://github.com/THARAKESHA/SMT-SUPEROPTIMIZER](https://github.com/THARAKESHA/SMT-SUPEROPTIMIZER)

A working compiler optimization engine that searches for provably optimal instruction sequences for straight-line basic blocks, using the **Z3 Theorem Prover** to formally verify bit-precise semantic equivalence over all $2^{32}$ inputs using Quantifier-Free Bit-Vector logic (`QF_BV`).

---

## What This Does

Given a small compiler basic block in Three-Address Code (TAC), such as:

```text
t0 = ADD x, x
t1 = ADD t0, t0
```

the superoptimizer searches bounded-length candidate instruction sequences ($L \le 2$), proves candidates equivalent to the original using Z3 refutation (`UNSAT`), and returns the cheapest **proven-equivalent** replacement:

```text
t0 = SHL x, 2
```

This reduces a 2-instruction block to 1 instruction, with an absolute mathematical guarantee that the rewrite is correct for **every possible 32-bit input ($4,294,967,296$ values)**, completely eliminating compiler miscompilations.

---

## Project Structure

```text
smt_superoptimizer/
├── src/
│   ├── ir.py              # IR data structures & 13 opcodes (Member 2: Saksham)
│   ├── parser.py          # TAC parser with def-use analysis (Member 2: Saksham)
│   ├── candidate_gen.py   # Candidate generation & symmetry breaking (Member 3: Ishan)
│   ├── smt_encoder.py     # IR -> Z3 QF_BV bitvector AST translator (Member 3: Ishan)
│   ├── equivalence.py     # UNSAT-based refutation prover (Member 3: Ishan)
│   ├── cost_model.py      # Simple and weighted cycle latency models (Member 4: Jeevanth)
│   ├── cache.py           # Persistent disk memoization cache (Member 1: Tharakesha)
│   └── superoptimizer.py  # Master pipeline integration & driver (Member 1: Tharakesha)
├── tests/
│   ├── test_ir_and_parser.py
│   ├── test_candidate_gen.py
│   ├── test_cost_model.py
│   ├── test_equivalence.py
│   ├── test_advanced_features.py
│   └── test_integration.py
├── benchmarks/
│   └── blocks.txt         # 8 compiler benchmark blocks
├── run_demo.py            # CLI benchmark runner & live interactive REPL
├── run.bat                # One-click Windows demonstration launcher
└── requirements.txt
```

---

## Quick Start & One-Click Execution

### Option A: One-Click Windows Launcher (`run.bat`)
Double-click `run.bat` in the repository root (or `RUN_REVIEW_3.bat` on your Desktop):
* **`[1]`**: Run 8 benchmarks using persistent cache (**Warm Run**: 0.000s instant hit).
* **`[2]`**: Run 8 benchmarks from scratch (**Cold Run**: full Z3 synthesis ~3.8s, checking up to 320,000 candidates).
* **`[3]`**: Run all 44 automated pytest tests (100% pass in ~0.95s).
* **`[4]`**: Launch interactive live REPL shell for custom evaluator inputs.
* **`[6]`**: Compare Cold vs Warm run side-by-side to showcase cache speedup.
* **`[A]`**: Execute the complete 7-stage demonstration sequence prescribed in Section 8 of Review 3 guidelines.

### Option B: Terminal Setup
```bash
pip install -r requirements.txt
```
*(Requires Python 3.10+ and `z3-solver`)*

---

## Running the Automated Test Suite (44 Tests Passing)

```bash
python -m pytest tests/ -v
```

All **44 automated tests** pass with 100% assertion success:
* **Unit tests:** Lexing, syntax validation, def-use analysis, SSA arity enforcement.
* **Mathematical property & boundary tests:** 32-bit integer overflow wrap-around (`0xFFFFFFFF + 1 = 0`), bitwise idempotence, zero cancellation.
* **Advanced feature tests:** Commutative symmetry breaking pruning, branchless `SEL` opcode, persistent memoization.
* **Regression tests:** `DEFECT-01` regression check ensuring constant-only replacements (`y = CONST 0`) are accepted.
* **Integration tests:** End-to-end multi-instruction benchmarks (double-add, strength reduction, 3-to-1 bit rotations).

---

## Running the Benchmarks & Demonstrations

### 1. Warm Run (Instant 0.000s Execution via Persistent Cache)
```bash
python run_demo.py
```
Outputs instant solutions from `superoptimizer_cache.json` with **8 cache hits and 0.000s solve time**.

### 2. Cold Run (Full Z3 Synthesis from Scratch)
```bash
python run_demo.py --cold
```
Bypasses the cache and actively explores candidate spaces (checking **up to 321,680 candidates** per block) with formal Z3 refutations in ~3.8 seconds.

### 3. Interactive Live REPL Shell
```bash
python run_demo.py --interactive
```
Allows testing custom Three-Address Code blocks entered live during presentation:
```text
Enter basic block:
  > t0 = ADD x, x
  > t1 = ADD t0, t0
  > run
```

---

## Key Technical Innovations

1. **Commutative Symmetry Breaking:**  
   Replaces naive $N \times N$ permutations with combinations with replacement $\binom{N+1}{2} = \frac{N(N+1)}{2}$ for commutative opcodes (`ADD`, `AND`, `OR`, `XOR`, `MUL`), eliminating **45% to 50%** of redundant solver queries.

2. **Dynamic Constant Harvesting (`harvest_constants`):**  
   Analyzes input blocks to extract integer literals, boundary constants (`0`, `1`, `31`, `32`, `0xFFFFFFFF`), and bit-shift complements ($32 - k$).

3. **Souper-Style Persistent Memoization Cache (`cache.py`):**  
   Stores verified equivalence proofs to disk (`superoptimizer_cache.json`), guaranteeing zero solver overhead on repeated compilation passes.

4. **13 Supported Opcodes with Hardware Idiom Recognition:**  
   `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SHL`, `SHR`, `ROL`, `ROR`, `NOT`, `NEG`, `MUL`, `SEL`, `CONST`.  
   Synthesizes 3-instruction shift/shift/OR cascades into a single hardware circular rotate (`ROL`/`ROR`), and optimizes 3-cycle multiplies into 1-cycle shifts (`MUL x, 8 -> SHL x, 3`).

---

## Defect Log

| Defect | Discovery Phase | Root Cause | Engineering Fix | Verified By |
|---|---|---|---|---|
| **DEFECT-01**: False rejection of constant-only candidate (e.g. `y = CONST 0` for `x - x`) | Review 2 test development | `equivalence.py` strictly checked `orig.inputs == cand.inputs`. A constant-only block has an empty input set ($\emptyset$), so it was rejected prematurely. | Relaxed to subset check `cand.inputs ⊆ orig.inputs`. A candidate may use fewer inputs than original, but never undefined inputs. | `test_regression_constant_only_candidate_not_falsely_rejected` |

---

## Team Members & Responsibilities (Team A13)

1. **THARAKESHA M (24BCE2538) — Project Lead / System Integrator**  
   *Pipeline architecture, persistent cache, interactive CLI, Review 3 slides & report compilation.*
2. **SAKSHAM PANWAR (24BDS0377) — Front-End & IR Owner**  
   *Intermediate representation (`ir.py`), TAC grammar, def-use analysis, parsing test suite.*
3. **ISHAN ARYA (24BCE2228) — SMT Logic Prover & Core Algorithms**  
   *SMT bit-vector encoder (`smt_encoder.py`), equivalence refutation checker, symmetry breaking, constant harvester.*
4. **JEEVANTH S A (24BCE0940) — Testing, Cost Models & Release**  
   *Simple and weighted cycle latency models (`cost_model.py`), 44-test testbench, benchmark suite, defect log.*
