# Gate Sizing for Minimum Area under a Timing Constraint

Course project for EE6332 (Modelling and Optimization in VLSI), IIT Madras.
Author: Aman Saini

Given a combinational circuit and a timing specification, choose the size of every gate so that
total area (sum of gate sizes) is as small as possible while the circuit still meets timing.
The problem is solved as a continuous geometric program, and the continuous solution is then
converted into discrete, integer gate sizes.

## Approach

**Delay model.** Logical-effort delay model: each gate has a parasitic delay and a logical effort,
and its delay depends on the load it drives relative to its own size. Gate sizes are bounded to
[1, 64] (normalized to a unit inverter), with limits on input capacitance and a fixed output load.

**Phase 1: continuous sizing.** Gate sizes and node arrival times are the variables of a geometric
program, solved with [GPkit](https://github.com/convexengineering/gpkit) and the MOSEK solver.
Two problems are solved per circuit:
- `T_wall`: the minimum achievable delay.
- Minimum area at `T_spec = k * T_wall` for relaxation factors k from 1.05 to 1.5.

**Phase 2: discretization.** Continuous sizes are not realizable, so they are converted to integers:
- Simple floor / ceil / round heuristics were tried first. They fail the timing spec on most circuits.
- A breadth-first branch-and-bound search keeps the k best partial assignments at each depth,
  followed by a local refinement step (each gate tries sizes within +/-2 of its current size). This
  meets timing on every benchmark, but at a high area cost on some circuits.
- An area-recovery pass then shrinks gates that have positive slack, in several passes, while
  keeping the circuit within the timing spec.

**Comparison.** A mixed-integer geometric program in CVXPY (log-size variables with a penalty term)
gives comparable area on the smallest circuits but did not finish in reasonable time on the larger ones.

**Standard-cell sizes.** Gate sizes that occur in the area-optimal solutions are aggregated across
circuits to suggest which sizes a small standard-cell library should contain for each gate type.

## Results

ISCAS-85 benchmarks, `T_spec = 1.3 * T_wall`. Every discrete solution meets the timing spec.

| Circuit | Gates | Continuous area | Discrete area | Area increase | Runtime (s) |
|---------|------:|----------------:|--------------:|--------------:|------------:|
| c17     |     6 |          136.11 |           138 |         1.38% |       0.004 |
| c432    |   229 |          460.31 |           482 |         4.71% |        1.66 |
| c880    |   555 |          891.27 |           914 |         2.55% |        8.19 |
| c1908   | 1,144 |        1,531.48 |         1,572 |         2.64% |       54.49 |
| c2670   | 1,958 |        2,708.75 |         2,709 |         0.01% |      176.81 |
| c3540   | 2,548 |        2,734.58 |         2,753 |         0.67% |      223.32 |
| c5315   | 3,569 |        4,265.34 |         4,343 |         1.82% |      830.22 |
| c6288   | 2,672 |        2,825.94 |         2,858 |         1.13% |      242.94 |
| c7552   | 5,103 |        5,995.34 |         6,067 |         1.19% |    1,034.65 |

The discrete solutions stay within 5% of the continuous optimum. The full write-up, including the
critical-path analysis and the standard-cell size table, is in `ee24s007_project_report.pdf`.

## Repository layout

| Path | Contents |
|------|----------|
| `EE6332_endsem.ipynb` | Main notebook: GP formulation, discretization, area recovery |
| `parser.py`, `utilities.py` | Parse structural Verilog netlists into DAGs (networkx) and report critical paths and fan-out |
| `config.json` | Input, output and report directories |
| `iscas85_ckts/` | ISCAS-85 benchmark netlists |
| `sizing_results/` | Continuous solutions (`T_wall` and minimum-area runs per relaxation factor) |
| `discrete_solutions/` | Discrete gate sizes and run logs per circuit |
| `analyses/` | Critical-path and fan-out reports |

## Running it

1. Parse the netlists into DAG files: `python parser.py <path-to-netlist>`
   (needs `networkx`, `tabulate`, `matplotlib`; set the paths in `config.json`).
2. Open `EE6332_endsem.ipynb` (written for Google Colab) and set the paths at the top.
3. The notebook installs GPkit and MOSEK. MOSEK needs its own licence file (academic licences are
   free); it is not included in this repository.

## Limitations

- The logical-effort model is a first-order approximation, not a signoff static timing analysis
  with a real cell library.
- Discretization is heuristic, with no optimality guarantee, and the Python implementation takes
  about 17 minutes on the largest circuit (c7552).
- Results are for the ISCAS-85 combinational benchmarks only.
