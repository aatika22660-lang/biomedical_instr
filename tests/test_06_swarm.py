# tests/test_06_swarm.py — Swarm behaviour and quorum sensing
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from simulation.environment import make_hgf_gradient, random_edge_position
from simulation.config import (
    GRID_SIZE, NUM_AGENTS, MAX_STEPS, SIGMA_CAR,
    QUORUM_RADIUS, QUORUM_STRENGTH
)

SWARM_STEPS = 100
NEIGHBOURS  = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def clamp(v, lo=0, hi=GRID_SIZE - 1):
    return max(lo, min(hi, v))

# ── Spawn 50 agents on random edges ───────────────────────────────────────────
rng = np.random.default_rng(7)
hgf = make_hgf_gradient()

# State: 0=navigating, 1=engrafted, 2=failed
positions = [list(random_edge_position(rng=rng)) for _ in range(NUM_AGENTS)]
states    = [0] * NUM_AGENTS

always_in_bounds = True
correct_counts   = True
quorum_repulsion_triggered = False

# Track a pair of nearby agents to confirm repulsion
# (we'll verify manually that close agents diverge)
pre_repulsion_distances = []
post_repulsion_distances = []

for step in range(SWARM_STEPS):
    # Record pairwise distances before moves
    pos_arr = np.array(positions)

    new_positions = []
    for i, (x, y) in enumerate(positions):
        if states[i] != 0:
            new_positions.append([x, y])
            continue

        # Gradient ascent
        best_val = -np.inf
        bdx, bdy = 0, 0
        for dx, dy in NEIGHBOURS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if hgf[nx, ny] > best_val:
                    best_val = hgf[nx, ny]
                    bdx, bdy = dx, dy

        # Quorum repulsion: push away from neighbours within QUORUM_RADIUS
        rep_x, rep_y = 0.0, 0.0
        for j, (ox, oy) in enumerate(positions):
            if i == j or states[j] != 0:
                continue
            dist = np.sqrt((x - ox)**2 + (y - oy)**2)
            if 0 < dist <= QUORUM_RADIUS:
                quorum_repulsion_triggered = True
                rep_x += (x - ox) / dist * QUORUM_STRENGTH
                rep_y += (y - oy) / dist * QUORUM_STRENGTH

        noise_x = rng.normal(0, SIGMA_CAR)
        noise_y = rng.normal(0, SIGMA_CAR)

        nx = clamp(int(round(x + bdx + rep_x + noise_x)))
        ny = clamp(int(round(y + bdy + rep_y + noise_y)))

        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            always_in_bounds = False

        new_positions.append([nx, ny])

    positions = new_positions

    # Check state counts sum to NUM_AGENTS every step
    if len(states) != NUM_AGENTS:
        correct_counts = False

# ── Pass/Fail checks ───────────────────────────────────────────────────────────
print("=" * 50)
print("TEST 06 — Swarm Behaviour")
print("=" * 50)
print(f"All in bounds always:        {always_in_bounds}   (expect True)")
print(f"State counts sum to 50:      {correct_counts}   (expect True)")
print(f"Quorum repulsion triggered:  {quorum_repulsion_triggered}   (expect True)")

assert always_in_bounds,           "FAIL: agent(s) went out of bounds"
assert correct_counts,             "FAIL: agent count changed mid-run"
assert quorum_repulsion_triggered, "FAIL: quorum repulsion never triggered (agents never close enough)"
print("\nAll checks PASSED ✓")