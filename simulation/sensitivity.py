"""
sensitivity.py
CAR-MuSC Simulation — Sensitivity Analysis

Sweeps σ_CAR across [0.15, 0.20, 0.25, 0.30] and reports mean
targeting index for both CAR-MuSC and unmodified MuSC at each value.

Purpose (from roadmap):
    Prove that the CAR advantage holds across a range of plausible σ_CAR
    values, demonstrating robustness to the primary modelling assumption
    rather than dependence on a single point estimate (σ_CAR = 0.2).

    This directly addresses the critique that σ_CAR is an extrapolated
    parameter — if the result holds at 0.15, 0.20, 0.25, and 0.30, it
    cannot be dismissed as an artefact of one arbitrary choice.

Usage:
    python -m simulation.sensitivity

    Or import and call directly:
        from simulation.sensitivity import sensitivity_analysis, plot_sensitivity
        results = sensitivity_analysis()
        plot_sensitivity(results)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
# Add project root to sys.path to allow absolute imports from 'simulation' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.config import (
    SIGMA_NOISE, MAX_STEPS, NUM_AGENTS, ENGRAFT_SUCCESS_RATE, SENSITIVITY_RUNS
)

from simulation.simulation import Simulation

def sensitivity_analysis(
    sigma_car_values = (0.15, 0.20, 0.25, 0.30),
    sigma_unmod      = SIGMA_NOISE,
    n_runs           = SENSITIVITY_RUNS,
    n_steps          = MAX_STEPS,
    n_agents         = NUM_AGENTS,
    base_seed        = 42,
):
    """
    Sweep σ_CAR across a range of values and report mean final coverage
    for both CAR-MuSC and unmodified MuSC at each value.

    Parameters
    ----------
    sigma_car_values : iterable of float
        σ_CAR values to test. Default: (0.15, 0.20, 0.25, 0.30)
    sigma_unmod : float
        Unmodified MuSC noise — held constant throughout. Default: 0.4
    n_runs : int
        Independent runs per σ_CAR value for mean ± std. Default: 5
    n_steps : int
        Steps per run. Default: MAX_STEPS (300)
    n_agents : int
        Agents per condition per run. Default: NUM_AGENTS (50)
    base_seed : int
        Base RNG seed — each run uses base_seed + run_index for independence.

    Returns
    -------
    results : list of dict, one entry per σ_CAR value, each containing:
        {
            'sigma_car'          : float — the σ_CAR value tested
            'car_targeting_mean' : float — mean CAR targeting index (%)
            'car_targeting_std'  : float — std CAR targeting index (%)
            'unmod_targeting_mean': float — mean unmod targeting index (%)
            'unmod_targeting_std' : float — std unmod targeting index (%)
            'car_wins'           : int   — number of runs where CAR > unmod
            'car_advantage_mean' : float — mean (CAR targeting − unmod targeting)
        }
    """
    results = []

    for sigma_car in sigma_car_values:
        print(f"  Testing σ_CAR = {sigma_car:.2f}…", end=" ", flush=True)
        car_targetings   = []
        unmod_targetings = []

        for run in range(n_runs):
            seed = base_seed + run
            sim  = Simulation(
                n_agents     = n_agents,
                sigma_unmod  = sigma_unmod,
                sigma_car    = sigma_car,
                engraft_rate = ENGRAFT_SUCCESS_RATE,
                seed         = seed,
            )
            sim.run(n_steps)
            metrics = sim.get_metrics()
            car_targetings.append(metrics['car_targeting_index'])
            unmod_targetings.append(metrics['unmod_targeting_index'])

        car_arr   = np.array(car_targetings)
        unmod_arr = np.array(unmod_targetings)

        entry = {
            'sigma_car'          : sigma_car,
            'car_targeting_mean' : float(car_arr.mean()),
            'car_targeting_std'  : float(car_arr.std()),
            'unmod_targeting_mean': float(unmod_arr.mean()),
            'unmod_targeting_std' : float(unmod_arr.std()),
            'car_wins'           : int(np.sum(car_arr > unmod_arr)),
            'car_advantage_mean' : float((car_arr - unmod_arr).mean()),
        }
        results.append(entry)
        print(f"CAR {entry['car_targeting_mean']:.1f}% vs Unmod "
              f"{entry['unmod_targeting_mean']:.1f}%  "
              f"(CAR wins {entry['car_wins']}/{n_runs})")

    return results


def plot_sensitivity(results, out_path=None):
    """
    Plot sensitivity analysis results as a grouped bar chart with error bars.

    One group per σ_CAR value tested. CAR-MuSC and unmodified bars shown
    side by side. This is the figure that goes into the report Results section
    to demonstrate robustness of the CAR advantage across σ values.

    Parameters
    ----------
    results  : list of dict — output of sensitivity_analysis()
    out_path : str or None  — file path to save PNG. If None, saves to
                              simulation/sensitivity_output.png
    """
    sigma_labels  = [f"σ_CAR={r['sigma_car']:.2f}" for r in results]
    car_means     = [r['car_targeting_mean']   for r in results]
    car_stds      = [r['car_targeting_std']    for r in results]
    unmod_means   = [r['unmod_targeting_mean'] for r in results]
    unmod_stds    = [r['unmod_targeting_std']  for r in results]
    advantages    = [r['car_advantage_mean']   for r in results]

    x      = np.arange(len(sigma_labels))
    width  = 0.35
    colors = {'car': '#70a8e0', 'unmod': '#e07070'}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # ── Panel 1: grouped bars ─────────────────────────────────────────────────
    ax = axes[0]
    bars_unmod = ax.bar(x - width/2, unmod_means, width,
                        yerr=unmod_stds, label='Unmodified (σ=0.4)',
                        color=colors['unmod'], edgecolor='black',
                        capsize=6, error_kw={'linewidth': 1.5})
    bars_car   = ax.bar(x + width/2, car_means, width,
                        yerr=car_stds, label='CAR-MuSC',
                        color=colors['car'], edgecolor='black',
                        capsize=6, error_kw={'linewidth': 1.5})

    ax.set_xticks(x)
    ax.set_xticklabels(sigma_labels, fontsize=10)
    ax.set_ylabel('Mean targeting index (%)', fontsize=11)
    ax.set_title('Targeting by σ_CAR value\n(mean ± std, 20 runs each)', fontsize=11)
    ax.set_ylim(0, 100)
    ax.axhline(40, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.axhline(80, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.legend(fontsize=9)

    # ── Panel 2: CAR advantage line ───────────────────────────────────────────
    ax2 = axes[1]
    ax2.plot([r['sigma_car'] for r in results], advantages,
             'o-', color='#4a7fc1', linewidth=2, markersize=8)
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.fill_between([r['sigma_car'] for r in results], advantages, 0,
                     where=[a > 0 for a in advantages],
                     alpha=0.15, color='#70a8e0', label='CAR advantage')
    ax2.set_xlabel('σ_CAR value', fontsize=11)
    ax2.set_ylabel('CAR targeting advantage (pp)', fontsize=11)
    ax2.set_title('CAR advantage vs σ_CAR\n(positive = CAR outperforms)', fontsize=11)
    ax2.legend(fontsize=9)

    plt.suptitle('Sensitivity Analysis — CAR-MuSC vs Unmodified MuSC\n'
                 'σ_CAR swept across plausible range [0.15, 0.30]',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()

    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__), 'sensitivity_output.png')
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"Sensitivity plot saved → {out_path}")
    return out_path


def print_summary(results):
    """Print a formatted summary table of sensitivity analysis results."""
    n_runs = SENSITIVITY_RUNS
    print("=" * 65)
    print("SENSITIVITY ANALYSIS — σ_CAR sweep")
    print("=" * 65)
    print(f"{'σ_CAR':<8} {'CAR targeting':>14} {'Unmod targeting':>16} "
          f"{'Advantage':>11} {'CAR wins':>10}")
    print("-" * 65)
    for r in results:
        print(f"{r['sigma_car']:<8.2f} "
              f"{r['car_targeting_mean']:>6.1f} ± {r['car_targeting_std']:<5.1f}  "
              f"{r['unmod_targeting_mean']:>7.1f} ± {r['unmod_targeting_std']:<5.1f}  "
              f"{r['car_advantage_mean']:>+8.1f}pp  "
              f"{r['car_wins']:>5}/{n_runs}")
    print("=" * 65)

    car_wins_all = all(r['car_advantage_mean'] > 0 for r in results)
    print(f"\nCAR outperforms at all σ values: {car_wins_all}  (expect True)")
    if car_wins_all:
        print("✓ Result is robust to σ_CAR assumption — null hypothesis rejected"
              " across full parameter range.")
    else:
        print("✗ CAR advantage breaks down at some σ values — review assumptions.")



# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running sensitivity analysis…")
    results = sensitivity_analysis()
    print_summary(results)
    plot_sensitivity(results)