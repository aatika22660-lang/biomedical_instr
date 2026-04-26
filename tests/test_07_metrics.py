# tests/test_07_metrics.py
# Statistical validation across 10 independent runs.
#
# This test calls the real Simulation class directly — it does not
# reimplement simulation logic. It is a system-level integration test,
# not a unit test.
#
# Pass criteria:
#   - CAR wins >= 7/10 runs on final fibre coverage
#   - Effect size (CAR mean - unmod mean) > 3.0 percentage points
#   - CAR mean arrival step <= unmod mean arrival step
#   - Coverage in biologically plausible range [40, 80]%

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from simulation.simulation import Simulation
from simulation.config import MAX_STEPS

N_RUNS = 10

# ── Run 10 independent simulations per condition ──────────────────────────────
# Each run uses a unique seed for reproducibility and independence.
# Both conditions run inside the same Simulation object per run,
# ensuring they share the same environment and spawn seed — fair comparison.

print("Running 10 simulations per condition...")

car_coverages   = []
unmod_coverages = []
car_arrivals    = []
unmod_arrivals  = []
car_wins        = []

for run in range(N_RUNS):
    print(f"  Run {run + 1}/{N_RUNS}...", end=" ", flush=True)

    sim = Simulation(seed=run * 10)
    sim.run(MAX_STEPS)
    m = sim.get_metrics()

    c_cov  = m['car_final_coverage']
    u_cov  = m['unmod_final_coverage']
    c_arr  = m['car_mean_arrival']
    u_arr  = m['unmod_mean_arrival']

    car_coverages.append(c_cov)
    unmod_coverages.append(u_cov)
    car_arrivals.append(c_arr)
    unmod_arrivals.append(u_arr)
    car_wins.append(c_cov > u_cov)

    print(f"CAR cov={c_cov:.1f}%  Unmod cov={u_cov:.1f}%")

# ── Calculate statistics ──────────────────────────────────────────────────────
car_mean,   car_std   = np.mean(car_coverages),   np.std(car_coverages)
unmod_mean, unmod_std = np.mean(unmod_coverages), np.std(unmod_coverages)
car_wins_count        = sum(car_wins)
effect_size           = car_mean - unmod_mean

car_arrival_mean  = np.mean(car_arrivals)
unmod_arrival_mean = np.mean(unmod_arrivals)

# ── Pass/Fail criteria ────────────────────────────────────────────────────────
car_wins_majority  = car_wins_count >= 7          # CAR wins at least 7/10 runs
effect_meaningful  = effect_size > 3.0            # >3 percentage point advantage
car_arrives_faster = car_arrival_mean <= unmod_arrival_mean
coverage_in_range  = 40 <= car_mean <= 80

print("=" * 60)
print("TEST 07 — Metrics Validation (10 Runs)")
print("=" * 60)
print(f"CAR coverage mean ± std:   {car_mean:.1f} ± {car_std:.1f}%")
print(f"Unmod coverage mean ± std: {unmod_mean:.1f} ± {unmod_std:.1f}%")
print(f"Effect size (CAR - Unmod): {effect_size:+.1f} pp  (expect > 3.0)")
print(f"CAR wins ({car_wins_count}/10 runs):      {car_wins_majority}  (expect >= 7/10)")
print(f"CAR mean arrival step:     {car_arrival_mean:.1f}  vs unmod {unmod_arrival_mean:.1f}")
print(f"CAR arrives faster/equal:  {car_arrives_faster}  (expect True)")
print(f"Coverage in range [40,80]: {coverage_in_range}  (expect True)")

assert car_wins_majority, (
    f"FAIL: CAR won only {car_wins_count}/10 runs — need >= 7. "
    f"Effect size: {effect_size:+.1f} pp"
)
assert effect_meaningful, (
    f"FAIL: Effect size {effect_size:+.1f} pp below 3.0 threshold — "
    f"CAR advantage not clinically meaningful"
)
assert car_arrives_faster, (
    f"FAIL: CAR arrival {car_arrival_mean:.1f} steps vs unmod {unmod_arrival_mean:.1f}"
)
assert coverage_in_range, (
    f"FAIL: CAR mean coverage {car_mean:.1f}% outside [40, 80]"
)

print("\nAll checks PASSED ✓")

# ── Bar chart with error bars ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# Panel 1 — Coverage comparison
labels = ['Unmodified MuSC\n(σ=0.4)', 'CAR-MuSC\n(σ=0.2)']
means  = [unmod_mean, car_mean]
stds   = [unmod_std,  car_std]
colors = ['#e07070', '#70a8e0']

bars = axes[0].bar(labels, means, yerr=stds, color=colors, edgecolor='black',
                   capsize=8, width=0.5, error_kw={'linewidth': 2})
for bar, m, s in zip(bars, means, stds):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2, m + s + 1,
        f'{m:.1f} ± {s:.1f}%', ha='center', va='bottom',
        fontsize=10, fontweight='bold'
    )
axes[0].set_ylabel('Mean injury zone coverage (%)', fontsize=11)
axes[0].set_title('Final Fibre Coverage\n(mean ± std, 10 runs)', fontsize=12)
axes[0].set_ylim(0, 100)
axes[0].axhline(40, color='grey', linestyle='--', linewidth=0.8)
axes[0].axhline(80, color='grey', linestyle='--', linewidth=0.8)

# Annotate effect size
axes[0].annotate(
    f'Effect size: {effect_size:+.1f} pp',
    xy=(0.5, 0.92), xycoords='axes fraction',
    ha='center', fontsize=10,
    color='#1a5276' if effect_size > 3 else '#922b21',
    fontweight='bold'
)

# Panel 2 — Per-run results scatter
x_vals = list(range(1, N_RUNS + 1))
axes[1].plot(x_vals, car_coverages,   'o-', color='#70a8e0',
             label='CAR-MuSC', linewidth=2, markersize=7)
axes[1].plot(x_vals, unmod_coverages, 's-', color='#e07070',
             label='Unmodified', linewidth=2, markersize=7)
axes[1].axhline(car_mean,   color='#70a8e0', linestyle='--',
                linewidth=1, alpha=0.6)
axes[1].axhline(unmod_mean, color='#e07070', linestyle='--',
                linewidth=1, alpha=0.6)
axes[1].set_xlabel('Run number', fontsize=11)
axes[1].set_ylabel('Final coverage (%)', fontsize=11)
axes[1].set_title('Coverage per run\n(dashed = mean)', fontsize=12)
axes[1].set_ylim(0, 100)
axes[1].legend(fontsize=9)
axes[1].set_xticks(x_vals)

plt.suptitle(
    'Test 07 — Statistical Validation (10 Independent Runs)\n'
    'CAR-MuSC vs Unmodified MuSC — Perilesional Spawning',
    fontsize=12, fontweight='bold'
)
plt.tight_layout()

out = os.path.join(os.path.dirname(__file__), 'test_07_output.png')
plt.savefig(out, dpi=120)
plt.close()
print(f"Plot saved → {out}")
