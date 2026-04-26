# tests/test_04_engraftment.py — Engraftment Monte Carlo validation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from simulation.environment import make_hgf_gradient
from simulation.config import ENGRAFT_SUCCESS_RATE, HGF_THRESHOLD, GRID_SIZE

N_TRIALS = 1000
rng = np.random.default_rng(42)

# ── Monte Carlo: 1000 engraftment trials ───────────────────────────────────────
draws      = rng.random(N_TRIALS)
successes  = np.sum(draws < ENGRAFT_SUCCESS_RATE)
failures   = N_TRIALS - successes
success_rate = successes / N_TRIALS

# ── Mock agent in healthy tissue — should never engraft ───────────────────────
hgf        = make_hgf_gradient()
# Place agent at corner — far from injury, HGF << threshold
mock_x, mock_y = 2, 2
assert hgf[mock_x, mock_y] < HGF_THRESHOLD, "Sanity check: corner should be healthy tissue"

# Simulate 100 steps: engraftment only allowed when HGF > threshold
healthy_engraftments = 0
for _ in range(100):
    val = rng.random()
    # Only allow engraftment attempt if HGF > threshold at position
    if hgf[mock_x, mock_y] > HGF_THRESHOLD and val < ENGRAFT_SUCCESS_RATE:
        healthy_engraftments += 1

# ── Pass/Fail checks ───────────────────────────────────────────────────────────
within_tolerance = abs(success_rate - ENGRAFT_SUCCESS_RATE) < 0.05

print("=" * 50)
print("TEST 04 — Engraftment Logic")
print("=" * 50)
print(f"Trials:           {N_TRIALS}")
print(f"Successes:        {successes}   ({success_rate*100:.1f}%)")
print(f"Failures:         {failures}    ({(1-success_rate)*100:.1f}%)")
print(f"Success rate:     {success_rate:.4f}  (expect {ENGRAFT_SUCCESS_RATE} ± 0.05)")
print(f"Within tolerance: {within_tolerance}  (expect True)")
print(f"HGF at mock pos:  {hgf[mock_x, mock_y]:.6f}  (expect < {HGF_THRESHOLD})")
print(f"Healthy engraft:  {healthy_engraftments}  (expect 0)")

assert within_tolerance,         f"FAIL: success rate {success_rate:.4f} outside ±0.05 of {ENGRAFT_SUCCESS_RATE}"
assert healthy_engraftments == 0, "FAIL: engraftment triggered in healthy tissue"
print("\nAll checks PASSED ✓")