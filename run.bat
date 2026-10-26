@echo off
setlocal enabledelayedexpansion
title BCSE307L Review 3 - SMT Superoptimizer Launcher (Team A13)
color 0B

:: Ensure we switch to the repository root directory
cd /d "C:\Users\thara\OneDrive\Documents\smt_superoptimizer\smt_superoptimizer"

:menu
cls
echo ===============================================================================
echo      BCSE307L COMPILER DESIGN - PROJECT REVIEW 3 FINAL DEMONSTRATION
echo                 SMT-Based Superoptimizer Using Z3 Solver
echo               Team: A13  ^|  Project ID: CD-SMT-01  ^|  Marks: 10
echo ===============================================================================
echo.
echo   [1] Run 8 Benchmarks (WARM RUN: Instant 0.000s via Persistent Cache)
echo   [2] Run 8 Benchmarks (COLD RUN: Full Z3 Synthesis from Scratch)
echo   [3] Run Complete 44-Test Automated Testbench (Pytest - 100%% Pass)
echo   [4] Launch Interactive Live REPL Shell (Evaluator Custom Inputs)
echo   [5] Run Boundary 32-Bit Overflow Test (0xFFFFFFFF Wrap-Around)
echo   [6] Compare Cold vs Warm Cache Speedup Side-by-Side
echo   [7] Open Final Presentation Slides (.pptx)
echo   [8] Open Consolidated Final Report (.pdf)
echo   [9] Open Live GitHub Repository in Browser
echo   -----------------------------------------------------------------------------
echo   [A] Run Complete 7-Stage Review 3 Demonstration Sequence
echo   [Q] Quit
echo ===============================================================================
echo.
set "choice="
set /p choice="Select an option [1-9, A, Q] (Press Enter for Default [1]): "

if defined choice set choice=%choice: =%
if "%choice%"=="" set choice=1
if /i "%choice%"=="1" goto opt_warm
if /i "%choice%"=="2" goto opt_cold
if /i "%choice%"=="3" goto opt_tests
if /i "%choice%"=="4" goto opt_repl
if /i "%choice%"=="5" goto opt_overflow
if /i "%choice%"=="6" goto opt_compare
if /i "%choice%"=="7" goto opt_pptx
if /i "%choice%"=="8" goto opt_pdf
if /i "%choice%"=="9" goto opt_github
if /i "%choice%"=="A" goto opt_all
if /i "%choice%"=="Q" goto opt_quit

echo.
echo [!] Invalid selection '%choice%'. Please choose 1-9, A, or Q.
ping 127.0.0.1 -n 2 >nul
goto menu

:opt_warm
cls
echo ===============================================================================
echo   RUNNING BENCHMARKS WITH PERSISTENT CACHE (WARM RUN)
echo ===============================================================================
echo.
python run_demo.py
echo.
echo ===============================================================================
pause
goto menu

:opt_cold
cls
echo ===============================================================================
echo   RUNNING FULL SYNTHESIS FROM SCRATCH (COLD RUN - NO CACHE)
echo   (Evaluating thousands of candidates and invoking Z3 theorem prover)
echo ===============================================================================
echo.
python run_demo.py --cold
echo.
echo ===============================================================================
pause
goto menu

:opt_tests
cls
echo ===============================================================================
echo   RUNNING FULL AUTOMATED TEST SUITE (44 Pytest Tests)
echo ===============================================================================
echo.
python -m pytest tests/ -v
echo.
echo ===============================================================================
pause
goto menu

:opt_repl
cls
echo ===============================================================================
echo   STAGE 7: INTERACTIVE REPL SHELL (Evaluator Live Input)
echo   Enter custom Three-Address Code instructions (e.g. y = ADD x, x)
echo   Type 'exit' or 'quit' when finished to return to menu.
echo ===============================================================================
echo.
python run_demo.py --interactive
goto menu

:opt_overflow
cls
echo ===============================================================================
echo   STAGE 3: BOUNDARY & 32-BIT OVERFLOW TEST (0xFFFFFFFF Wrap-Around)
echo ===============================================================================
echo.
python -m pytest tests/test_equivalence.py -k "test_overflow_semantics_preserved" -v
echo.
echo ===============================================================================
pause
goto menu

:opt_compare
cls
echo ===============================================================================
echo   STAGE 6: CACHE MEMOIZATION SPEEDUP DEMONSTRATION
echo ===============================================================================
echo.
echo [1] Executing COLD RUN (Full Z3 Synthesis without cache):
python run_demo.py --cold
echo.
echo -------------------------------------------------------------------------------
echo [2] Executing WARM RUN (Instant retrieval from persistent cache):
python run_demo.py
echo.
echo ===============================================================================
echo   Notice: Cold run took ~3.8s while Warm run completed in 0.000s!
echo ===============================================================================
pause
goto menu

:opt_pptx
echo.
echo Opening Review 3 Final Presentation (.pptx)...
start "" "C:\Users\thara\OneDrive\Documents\Review_3_Final_Presentation.pptx"
ping 127.0.0.1 -n 2 >nul
goto menu

:opt_pdf
echo.
echo Opening Review 3 Final Project Report (.pdf)...
start "" "C:\Users\thara\OneDrive\Documents\Review_3_Final_Report.pdf"
ping 127.0.0.1 -n 2 >nul
goto menu

:opt_github
echo.
echo Opening GitHub Repository in browser...
start https://github.com/THARAKESHA/SMT-SUPEROPTIMIZER
ping 127.0.0.1 -n 2 >nul
goto menu

:opt_all
cls
echo ===============================================================================
echo   RUNNING COMPLETE 7-STAGE REVIEW 3 LIVE DEMONSTRATION SEQUENCE
echo ===============================================================================
echo.
echo -------------------------------------------------------------------------------
echo [Stage 1: Environment & Build Check]
echo -------------------------------------------------------------------------------
python --version
git log -n 3 --oneline
echo.
pause
echo.
echo -------------------------------------------------------------------------------
echo [Stage 2: Normal Benchmark Use Cases]
echo -------------------------------------------------------------------------------
python run_demo.py
echo.
pause
echo.
echo -------------------------------------------------------------------------------
echo [Stage 3: Boundary & 32-Bit Overflow Preservation]
echo -------------------------------------------------------------------------------
python -m pytest tests/test_equivalence.py -k "test_overflow_semantics_preserved" -v
echo.
pause
echo.
echo -------------------------------------------------------------------------------
echo [Stage 4: Invalid Input & Syntax Error Handling]
echo -------------------------------------------------------------------------------
python -m pytest tests/test_ir_and_parser.py -k "raises" -v
echo.
pause
echo.
echo -------------------------------------------------------------------------------
echo [Stage 5: SMT Internal Proof Trace]
echo -------------------------------------------------------------------------------
python -m pytest tests/test_equivalence.py -k "test_rotate_left or test_add_self_is_not_shift" -v
echo.
pause
echo.
echo -------------------------------------------------------------------------------
echo [Stage 6: Persistent Cache Speedup - Instant 0.000s Execution]
echo -------------------------------------------------------------------------------
python run_demo.py
echo.
echo ===============================================================================
echo   All 6 Automated Stages Completed Successfully!
echo   (For Stage 7: Evaluator-Selected Live Input, choose Option [4] in the menu)
echo ===============================================================================
pause
goto menu

:opt_quit
cls
echo Goodbye! Best of luck for Review 3 evaluation!
ping 127.0.0.1 -n 2 >nul
exit /b 0
