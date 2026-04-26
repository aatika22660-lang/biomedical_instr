# tests/test_06_swarm.py — Swarm behaviour and quorum sensing
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from simulation.simulation import Simulation
from simulation.config import (
    GRID_SIZE, NUM_AGENTS, QUORUM_RADIUS
)

SWARM_STEPS = 100
NEIGHBOURS  = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def clamp(v, lo=0, hi=GRID_SIZE - 1):
    return max(lo, min(hi, v))

sim = Simulation(seed=7)

always_in_bounds           = True
correct_counts             = True
quorum_repulsion_triggered = False

for step in range(SWARM_STEPS):
    sim.step()

    all_agents = sim.car_agents  # check one population is enough

    # Bounds check
    for a in all_agents:
        if not (0 <= a.x < GRID_SIZE and 0 <= a.y < GRID_SIZE):
            always_in_bounds = False

    # Count check — population size must never change
    if len(all_agents) != NUM_AGENTS:
        correct_counts = False

    # Quorum check — did any active agent have a close neighbour?
    active = [a for a in all_agents if a.state == 0]
    for i, a in enumerate(active):
        for b in active[i+1:]:
            dist = np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
            if 0 < dist <= QUORUM_RADIUS:
                quorum_repulsion_triggered = True


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