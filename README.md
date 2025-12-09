# Skyscrapers Puzzle Solver

This project implements multiple algorithms for solving the **Skyscrapers puzzle**, including A*, Weighted A*, CSP with AC-3, and Hill Climbing with Simulated Annealing. It provides both a programmatic API and a GUI for interactive play.

---

## Project Structure

```
main.py
A_star_Weighted_A_star/
    a_star_solver.py
    __pycache__/
CluesGenerator/
    clues_generator.py
    __pycache__/
Controller/
    data_checking.py
    puzzle_manager.py
    __pycache__/
CSP_AC3/
    csp_solver.py
    __pycache__/
Evaluations/
    evaluator.py
    __pycache__/
GUI/
    board.py
    __pycache__/
HillClimbingSA/
    hill_climbing_sa.py
    __pycache__/
SharedFunctions/
    shared_functions.py
    __pycache__/
```

---

## Description of Components

* **main.py** – Entry point to run solvers or the GUI.
* **A_star_Weighted_A_star/** – Implementation of A* and Weighted A* solvers.
* **CluesGenerator/** – Generates random puzzle grids and clue sets.
* **Controller/** – Handles puzzle validation, input/output checks, and puzzle management.
* **CSP_AC3/** – Implements CSP solver with AC-3 and backtracking strategies.
* **Evaluations/** – Contains the `Evaluator` class for comparing solver performance.
* **GUI/** – Implements a user interface for interactive puzzle solving.
* **HillClimbingSA/** – Hill Climbing solver with Simulated Annealing and tabu mechanisms.
* **SharedFunctions/** – Utility functions used across solvers, e.g., `visible_count`.

---

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_folder>
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

---

## Requirements

Based on the imports, the project requires:

* Python 3.10+
* `streamlit` – for GUI and user interface
* Standard libraries: `concurrent.futures`, `random`, `math`, `time`, `typing`, `collections`, `tracemalloc`, `itertools`, `copy`, `heapq`, `functools`, `statistics`, `multiprocessing`

*(All other imports are part of Python’s standard library.)*

---

## Usage

### Running Solvers

```bash
python main.py
```

* Runs evaluations for performance comparison.

### Running GUI

```bash
streamlit run main.py
```

* Opens an interactive GUI for entering puzzles and visualizing solutions.

---

## Solvers Implemented

1. **A* / Weighted A*** – Systematic search with heuristic guidance using a priority queue.
2. **CSP with AC-3** – Constraint satisfaction problem solver with arc consistency and backtracking.
3. **Hill Climbing with Simulated Annealing** – Stochastic local search with restarts, tabu list, and perturbations to escape local minima.

---

## Evaluations & Metrics

The `Evaluator` class supports:

* Comparing runtime and efficiency of different solvers
* Tracking nodes expanded/generated
* Measuring success rate over multiple random puzzles