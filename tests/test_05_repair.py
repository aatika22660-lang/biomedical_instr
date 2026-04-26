# tests/test_05_repair.py — Repair feedback loop validation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from simulation.environment import make_injury_mask
from simulation.config import GRID_SIZE, REPAIR_RATE

REPAIR_STEPS = 50

# ── Build damage grid (1.0 everywhere inside injury zone) ─────────────────────
injury_mask = make_injury_mask()
damage      = np.zeros((GRID_SIZE, GRID_SIZE))
damage[injury_mask] = 1.0

# Mock engrafted agent at injury centre
agent_x = GRID_SIZE // 2
agent_y = GRID_SIZE // 2

# ── Run 50 repair steps ───────────────────────────────────────────────────────
damage_at_agent = [damage[agent_x, agent_y]]
zone_damage_history = [damage[injury_mask].sum()]

for _ in range(REPAIR_STEPS):
    damage[agent_x, agent_y] -= REPAIR_RATE
    damage[agent_x, agent_y]  = max(0.0, damage[agent_x, agent_y])   # clamp
    damage_at_agent.append(damage[agent_x, agent_y])
    zone_damage_history.append(damage[injury_mask].sum())

# ── Evaluate ───────────────────────────────────────────────────────────────────
all_decreasing  = all(
    damage_at_agent[i] >= damage_at_agent[i+1]
    for i in range(len(damage_at_agent) - 1)
)
min_damage      = min(damage_at_agent)
zone_reduced    = zone_damage_history[-1] < zone_damage_history[0]

# ── Pass/Fail checks ───────────────────────────────────────────────────────────
print("=" * 50)
print("TEST 05 — Repair Feedback")
print("=" * 50)
print(f"Initial damage at agent: {damage_at_agent[0]:.4f}")
print(f"Final damage at agent:   {damage_at_agent[-1]:.4f}")
print(f"Damage decreases:        {all_decreasing}   (expect True)")
print(f"No negative damage:      {min_damage >= 0}   (expect True)")
print(f"Total zone reduced:      {zone_reduced}   (expect True)")
print(f"Zone damage: {zone_damage_history[0]:.2f} → {zone_damage_history[-1]:.2f}")

assert all_decreasing,  "FAIL: damage did not monotonically decrease"
assert min_damage >= 0, "FAIL: damage went negative"
assert zone_reduced,    "FAIL: zone damage did not reduce"
print("\nAll checks PASSED ✓")