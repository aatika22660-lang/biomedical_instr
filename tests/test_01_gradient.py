# tests/test_01_gradient.py — Grid and HGF gradient validation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from simulation.environment import make_hgf_gradient, make_injury_mask, make_border_mask
from simulation.config import GRID_SIZE

# ── Build ──────────────────────────────────────────────────────────────────────
hgf          = make_hgf_gradient()
injury_mask  = make_injury_mask()
border_mask  = make_border_mask(injury_mask)

# ── Pass/Fail checks ───────────────────────────────────────────────────────────
print("=" * 45)
print("TEST 01 — Grid and Gradient")
print("=" * 45)
print(f"Max HGF:           {hgf.max():.4f}  (expect 1.0)")
print(f"Min HGF:           {hgf.min():.6f}  (expect < 0.05)")
print(f"Border zone cells: {border_mask.sum()}      (expect > 0)")
print(f"Injury zone cells: {injury_mask.sum()}      (expect > 0)")

assert hgf.max() == 1.0,              "FAIL: max HGF not 1.0"
assert hgf.min() < 0.05,             "FAIL: min HGF not < 0.05"
assert border_mask.sum() > 0,        "FAIL: no border zone cells"
assert injury_mask.sum() > 0,        "FAIL: no injury zone cells"
print("\nAll checks PASSED ✓")

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(hgf.T, origin='lower', cmap='hot', interpolation='bilinear')
plt.colorbar(im, ax=ax, label='HGF intensity')

# Overlay masks as contours
ax.contour(injury_mask.T.astype(float), levels=[0.5], colors='cyan',  linewidths=1.5, linestyles='--')
ax.contour(border_mask.T.astype(float), levels=[0.5], colors='lime',  linewidths=1.0, linestyles=':')

ax.set_title('Test 01 — HGF Gradient\nCyan = injury ellipse | Green = border zone')
ax.set_xlabel('X'); ax.set_ylabel('Y')

out = os.path.join(os.path.dirname(__file__), '..', 'report', 'figures', 'test_01_output.png')
plt.tight_layout()
plt.savefig(out, dpi=120)
plt.close()
print(f"Plot saved → {out}")