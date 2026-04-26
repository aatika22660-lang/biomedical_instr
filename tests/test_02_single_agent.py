# tests/test_02_single_agent.py — Single CAR-MuSC agent navigation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from simulation.environment import (
    make_hgf_gradient, make_injury_mask, make_border_mask, random_edge_position
)
from simulation.config import GRID_SIZE, HGF_THRESHOLD, MAX_STEPS, SIGMA_CAR, SIGMA_BROAD
from simulation.agent import Agent

# ── Setup ──────────────────────────────────────────────────────────────────────
rng         = np.random.default_rng(42)
hgf         = make_hgf_gradient(sigma=SIGMA_BROAD)
injury_mask = make_injury_mask()
border_mask = make_border_mask(injury_mask)

# ── Spawn agent on a random edge ───────────────────────────────────────────────
x, y = random_edge_position(rng=rng)

agent = Agent(x=x, y=y, sigma=SIGMA_CAR, rng=rng, injury_mask=injury_mask)
trajectory = [(agent.x, agent.y)]

steps     = 0
in_bounds = True
final_hgf = hgf[agent.x, agent.y]

for step in range(MAX_STEPS):
    agent.step(hgf, [agent], step)

    if not (0 <= agent.x < GRID_SIZE and 0 <= agent.y < GRID_SIZE):
        in_bounds = False

    trajectory.append((agent.x, agent.y))
    steps += 1
    final_hgf = hgf[agent.x, agent.y]

    if final_hgf > HGF_THRESHOLD:
        break

# ── Pass/Fail checks ───────────────────────────────────────────────────────────
print("=" * 45)
print("TEST 02 — Single Agent Navigation")
print("=" * 45)
print(f"Final HGF value:  {final_hgf:.4f}  (expect > {HGF_THRESHOLD})")
print(f"Steps taken:      {steps}       (expect < {MAX_STEPS})")
print(f"Stayed in bounds: {in_bounds}   (expect True)")

assert final_hgf > HGF_THRESHOLD, f"FAIL: agent did not reach target (HGF={final_hgf:.4f})"
assert steps < MAX_STEPS,         f"FAIL: agent exceeded MAX_STEPS"
assert in_bounds,                  "FAIL: agent went out of bounds"
print("\nAll checks PASSED ✓")

# ── Plot ───────────────────────────────────────────────────────────────────────
tx, ty = zip(*trajectory)
fig, ax = plt.subplots(figsize=(6, 5))
ax.imshow(hgf.T, origin='lower', cmap='hot', interpolation='bilinear')
ax.contour(injury_mask.T.astype(float), levels=[0.5], colors='cyan',  linewidths=1.5, linestyles='--')
ax.contour(border_mask.T.astype(float), levels=[0.5], colors='lime',  linewidths=1.0, linestyles=':')
ax.plot(tx, ty, 'w-', linewidth=0.8, alpha=0.7, label='Trajectory')
ax.plot(tx[0], ty[0], 'go', markersize=8, label='Start')
ax.plot(tx[-1], ty[-1], 'b*', markersize=12, label='End')
ax.legend(loc='upper right', fontsize=8)
ax.set_title(f'Test 02 — Single Agent Navigation\nSteps: {steps}  |  Final HGF: {final_hgf:.3f}')
ax.set_xlabel('X'); ax.set_ylabel('Y')

out = os.path.join(os.path.dirname(__file__), 'test_02_output.png')
plt.tight_layout()
plt.savefig(out, dpi=120)
plt.close()
print(f"Plot saved → {out}")
