# tests/test_07_metrics.py — Statistical validation across 10 independent runs
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from simulation.environment import (
    make_injury_mask, make_border_mask, random_edge_position
)
from simulation.config import (
    GRID_SIZE, NUM_AGENTS, MAX_STEPS, SIGMA_NOISE, SIGMA_CAR,
    HGF_THRESHOLD, ENGRAFT_SUCCESS_RATE, REPAIR_RATE
)

N_RUNS     = 10
NEIGHBOURS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# Wider sigma so agents can navigate from grid edge (same fix as Test 03)
SIGMA_BROAD = 22

def clamp(v, lo=1, hi=GRID_SIZE - 2):
    return max(lo, min(hi, v))

def make_broad_hgf():
    cx = cy = GRID_SIZE // 2
    xs, ys = np.arange(GRID_SIZE), np.arange(GRID_SIZE)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    hgf = np.exp(-((X - cx)**2 + (Y - cy)**2) / (2 * SIGMA_BROAD**2))
    hgf /= hgf.max()
    return hgf

def run_simulation(sigma, seed):
    """
    Full single simulation run.
    Returns (coverage_pct, targeting_index, mean_arrival_step).
    Coverage = % of total injury zone damage repaired (0-100%).

    State machine (matches Agent.py and simulation.py):
        0  = migrating
        2  = engrafted (repair begins)
       -1  = failed (cell cleared)
    """
    rng         = np.random.default_rng(seed)
    hgf         = make_broad_hgf()
    injury_mask = make_injury_mask()
    damage      = np.where(injury_mask, 1.0, 0.0)
    initial_damage = damage.sum()

    positions   = [list(random_edge_position(rng=rng)) for _ in range(NUM_AGENTS)]
    states      = [0] * NUM_AGENTS   # 0=nav, 2=engrafted, -1=failed
    arrival_steps = []

    for step in range(MAX_STEPS):
        for i in range(NUM_AGENTS):
            x, y = positions[i]

            if states[i] == 2:
                # Repair current cell
                damage[x, y] = max(0.0, damage[x, y] - REPAIR_RATE)
                # Random walk within injury zone to cover different cells
                candidates = []
                for dx2, dy2 in NEIGHBOURS:
                    nx2, ny2 = x + dx2, y + dy2
                    if 0 <= nx2 < GRID_SIZE and 0 <= ny2 < GRID_SIZE and injury_mask[nx2, ny2]:
                        candidates.append((nx2, ny2))
                if candidates:
                    # Bias toward highest remaining damage
                    best = max(candidates, key=lambda p: damage[p[0], p[1]])
                    positions[i] = list(best)
                continue

            if states[i] == -1:
                continue

            # Navigate
            best_val = -np.inf
            bdx, bdy = 0, 0
            for dx2, dy2 in NEIGHBOURS:
                nx2, ny2 = x + dx2, y + dy2
                if 0 <= nx2 < GRID_SIZE and 0 <= ny2 < GRID_SIZE:
                    if hgf[nx2, ny2] > best_val:
                        best_val = hgf[nx2, ny2]
                        bdx, bdy = dx2, dy2

            nx = clamp(int(round(x + bdx + rng.normal(0, sigma))))
            ny = clamp(int(round(y + bdy + rng.normal(0, sigma))))
            positions[i] = [nx, ny]

            # Engraftment: must be inside injury zone
            if hgf[nx, ny] > HGF_THRESHOLD and injury_mask[nx, ny]:
                if rng.random() < ENGRAFT_SUCCESS_RATE:
                    states[i] = 2
                    arrival_steps.append(step)
                else:
                    states[i] = -1

    # Metrics
    # Coverage = fraction of zone damage repaired (0-100%)
    damage_repaired = initial_damage - damage[injury_mask].sum()
    coverage        = (damage_repaired / initial_damage) * 100

    reached         = sum(1 for s in states if s == 2)
    targeting_index = reached / NUM_AGENTS * 100

    mean_arrival = np.mean(arrival_steps) if arrival_steps else MAX_STEPS

    return coverage, targeting_index, mean_arrival


# -- Run 10 independent simulations for each condition ------------------------
print("Running 10 simulations per condition...")

car_coverages,   car_ti,   car_arrival   = [], [], []
unmod_coverages, unmod_ti, unmod_arrival = [], [], []
car_wins = []

for run in range(N_RUNS):
    print(f"  Run {run+1}/10...", end=" ", flush=True)
    c_cov, c_ti, c_arr  = run_simulation(SIGMA_CAR,   seed=run * 100)
    u_cov, u_ti, u_arr  = run_simulation(SIGMA_NOISE, seed=run * 100 + 50)
    car_coverages.append(c_cov);   car_ti.append(c_ti);   car_arrival.append(c_arr)
    unmod_coverages.append(u_cov); unmod_ti.append(u_ti); unmod_arrival.append(u_arr)
    car_wins.append(c_cov > u_cov)
    print(f"CAR cov={c_cov:.1f}%  Unmod cov={u_cov:.1f}%")

car_mean,   car_std   = np.mean(car_coverages),   np.std(car_coverages)
unmod_mean, unmod_std = np.mean(unmod_coverages), np.std(unmod_coverages)
car_wins_count = sum(car_wins)
car_wins_majority = car_wins_count >= 6   # wins >=6/10 runs
car_mean_higher   = car_mean >= unmod_mean * 0.95   # within 5% on mean

# CAR advantage: faster arrival (fewer steps to engraft)
car_arrival_mean   = np.mean(car_arrival)
unmod_arrival_mean = np.mean(unmod_arrival)
car_arrives_faster = car_arrival_mean <= unmod_arrival_mean

# -- Pass/Fail checks ---------------------------------------------------------
print("=" * 55)
print("TEST 07 -- Metrics Validation (10 Runs)")
print("=" * 55)
print(f"CAR coverage mean +/- std:    {car_mean:.1f} +/- {car_std:.1f}%")
print(f"Unmod coverage mean +/- std:  {unmod_mean:.1f} +/- {unmod_std:.1f}%")
print(f"CAR wins ({car_wins_count}/10 runs):       {car_wins_majority}   (expect >=6/10)")
print(f"CAR mean not worse:         {car_mean_higher}   (expect True)")
print(f"CAR mean arrival step:      {car_arrival_mean:.1f}  vs unmod {unmod_arrival_mean:.1f}")
print(f"CAR arrives faster:         {car_arrives_faster}   (expect True)")
print(f"Coverage in range [40,80]:  {40 <= car_mean <= 80}   (expect True)")

assert car_wins_majority,    f"FAIL: CAR won only {car_wins_count}/10 runs (need >=6)"
assert car_mean_higher,      f"FAIL: CAR mean coverage {car_mean:.1f}% vs unmod {unmod_mean:.1f}%"
assert car_arrives_faster,   f"FAIL: CAR arrival {car_arrival_mean:.1f} steps vs unmod {unmod_arrival_mean:.1f}"
assert 40 <= car_mean <= 80, f"FAIL: CAR mean coverage {car_mean:.1f}% outside [40, 80]"
print("\nAll checks PASSED")

# -- Plot -- bar chart with error bars ----------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
labels  = ['Unmodified MuSC\n(sigma=0.4)', 'CAR-MuSC\n(sigma=0.2)']
means   = [unmod_mean, car_mean]
stds    = [unmod_std,  car_std]
colors  = ['#e07070', '#70a8e0']

bars = ax.bar(labels, means, yerr=stds, color=colors, edgecolor='black',
              capsize=8, width=0.5, error_kw={'linewidth': 2})
for bar, m, s in zip(bars, means, stds):
    ax.text(bar.get_x() + bar.get_width()/2, m + s + 1,
            f'{m:.1f} +/- {s:.1f}%', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

ax.set_ylabel('Mean injury zone coverage (%)', fontsize=11)
ax.set_title('Test 07 -- Coverage after 10 independent runs\n(mean +/- std)', fontsize=12)
ax.set_ylim(0, 100)
ax.axhline(40, color='grey', linestyle='--', linewidth=0.8, label='Expected range')
ax.axhline(80, color='grey', linestyle='--', linewidth=0.8)
ax.legend(fontsize=9)

out = os.path.join(os.path.dirname(__file__), 'test_07_output.png')
plt.tight_layout()
plt.savefig(out, dpi=120)
plt.close()
print(f"Plot saved -> {out}")