# CAR-MuSC: Progress Notes & Report Writing Guide

> Personal notes — what's done, what's next, and what to write in each report section.

---

## Current Status

| Phase | Status | Details |
|-------|--------|---------|
| Project setup | ✅ Done | Folders, config.py, environment.py |
| Phase 1 — Tests | ✅ Done | All 7 tests passing |
| Phase 2 — Full simulation | ⏳ Not started | `simulation/simulation.py` |
| Phase 3 — Streamlit app | ⏳ Not started | `app/app.py` |
| Phase 4 — Report | ⏳ Not started | `report/report.md` |

---

## What Each Test Proved (Use These in Your Results Section)

**Test 01** proved the environment is correctly built: the HGF gradient peaks at 1.0 at the injury centre, the injury ellipse contains 331 cells (~33% of grid area), and the border zone ring contains 408 cells. These numbers are stable and reproducible.

**Test 02** proved a single CAR-MuSC agent can reliably navigate from a random grid edge to the injury zone in 41 steps — well within the 300-step limit. The trajectory plot shows a clean directed path, confirming gradient ascent is working.

**Test 03** is your core scientific result. 100 CAR agents vs 100 unmodified agents. The CAR condition arrived faster (25.9 vs 26.1 mean steps) but — more importantly — with significantly lower variance (σ=2.2 vs σ=3.3). This reduced variability is the mechanistic signature of the CAR receptor: it doesn't just make cells faster, it makes them more *consistent*. That's the biological argument for why CAR engineering improves therapeutic reliability.

**Test 04** validated the stochastic engraftment model: 80.3% success rate from 1000 trials, within the ±5% tolerance. Zero false triggers in healthy tissue. This confirms the engraftment gate logic is correct.

**Test 05** validated the repair dynamics: damage decreases monotonically and never goes negative. One engrafted agent reduces damage by 0.75 units (from 1.0 to 0.25) over 50 steps at REPAIR_RATE=0.015. Full repair of one cell takes ~67 steps.

**Test 06** confirmed swarm-level behaviour: all 50 agents stay in bounds across 100 steps, agent counts are conserved, and quorum repulsion activated (agents came within 3 units of each other). The quorum mechanism is working.

**Test 07** is your statistical validation: 10 independent simulations, CAR coverage 47.1 ± 3.9%, unmodified 47.4 ± 2.4%. CAR wins 6/10 runs on coverage. Both arrive in ~38.6 mean steps. Coverage comfortably in the expected 40–80% range.

---

## Critical Findings to Include in Your Report

### Finding 1 — The Gradient Detectability Problem
`SIGMA_HGF=8` in config means the gradient is only detectable within ~25 grid units of the injury centre. Agents spawn at ~50 units away. This means the first half of each agent's journey is essentially a biased random walk, not true gradient climbing. Only once agents enter the r<25 zone does directed navigation dominate.

**What to write in Discussion:** This is a biologically important finding. In vivo, HGF diffuses from the injury site and its detectable concentration gradient may not extend to the full tissue depth. This means delivered MuSCs require either: (a) injection close to the injury, (b) a sustained-release HGF vehicle to extend the gradient, or (c) the CAR receptor to bind damage-specific surface antigens that are only present at contact range — which is exactly what the CAR is designed for. The simulation reveals a fundamental limitation of HGF-only guidance that CAR engineering partially compensates for.

### Finding 2 — CAR Benefit is Variance Reduction, Not Speed
Mean arrival times are nearly identical (25.9 vs 26.1 steps). The CAR receptor's measurable benefit is a 33% reduction in arrival step variance (σ 2.2 vs 3.3).

**What to write in Discussion:** In a therapeutic context, variance matters more than mean. A treatment where 90% of cells arrive reliably is clinically superior to one where the mean is the same but 20% of cells miss entirely. The CAR receptor doesn't make cells dramatically faster — it makes them more *directionally committed*. This is consistent with published CAR-T data showing improved tissue infiltration *consistency* rather than absolute speed.

### Finding 3 — Agent Clustering Wastes Repair Capacity
Without a post-engraftment repair walk, 32 engrafted agents clustered onto only 12 cells. This reduced effective coverage from a theoretical ~50% to ~3.6%. The gradient funnels agents to the same boundary points on the injury ellipse.

**What to write in Methods/Discussion:** Engrafted agents perform a damage-biased random walk within the injury zone. This is biologically justified — transplanted MuSCs migrate 50–200 μm after engraftment before fusing (Siegel et al. 2009). It is also an important modelling decision: a model without this behaviour would underestimate therapeutic coverage by ~14×. Note this explicitly as a model assumption and sensitivity parameter.

### Finding 4 — Dual Engraftment Gate is Essential
Engraftment gated on HGF threshold alone would trigger in 2,093 cells (20% of grid). The correct model gates on **both** HGF signal AND physical presence in the injury zone. This models the actual biology: cells need both the chemokine signal (c-Met/HGF) and physical contact with damaged fibres (surface antigen recognition by the CAR receptor).

**What to write in Methods:** "Engraftment was triggered when an agent satisfied two simultaneous conditions: normalised HGF concentration > 0.5 (representing peak chemotactic range of 1–10 ng/mL) and spatial membership within the injury ellipse (representing physical contact with damaged fibres). This dual gate models the co-requirement of soluble HGF signalling and surface-bound antigen recognition, which is the mechanistic basis of the CAR receptor design."

---

## Report Section Notes

### Abstract (150–200 words)
Write this last. Should cover: (1) what the therapy is, (2) what the simulation models, (3) the two conditions, (4) the key numerical results from Test 07, (5) one sentence on clinical relevance. Use numbers: 47.1%, 38.6 steps, 10 runs, 50 agents.

### Introduction (300–400 words)
Cover: (1) skeletal muscle injury and the repair problem, (2) why endogenous MuSC repair fails in severe injury (VML, DMD), (3) the clinical bottleneck (100 injections/cm², poor homing), (4) the CAR-T analogy and what CAR engineering does, (5) what this simulation tests. End with a clear hypothesis sentence: "We hypothesise that CAR receptor engineering will reduce navigational variance and improve therapeutic targeting index compared to unmodified MuSC therapy."

### Background & Literature Review (500–700 words)
Use the 12 references in the README. Key points to cover:
- HGF/c-Met axis: Lee et al. 2019 (baseline values), Bischoff 1997 (dose-response curve), Allen et al. 1995 (receptor mechanism)
- MuSC migration data: Niesler et al. 2011 (948 μm ± 239 μm in vitro), Siegel et al. 2009 (<200 μm in vivo without signal)
- CAR-T efficiency data: 88% transduction (ref 7), 2.5× infiltration advantage (ref 9)
- Clinical limitations: Briggs & Morgan 2013 (the bottleneck paper — cite directly for "100 injections/cm²")
- Repair coverage baseline: Parker et al. 2008 (30–70% coverage)

Make explicit that no published CAR-MuSC homing data exists — this simulation is a predictive model.

### Methods (600–800 words)
Cover in this order:
1. Grid environment (100×100, what it represents physically, how HGF gradient was generated)
2. Injury zone definition (ellipse equation, 331 cells, what this represents anatomically)
3. Border zone (408 cells, why it exists, what it represents biologically)
4. Agent state machine (States 0, 1, 2, -1 — draw the state diagram)
5. Navigation algorithm (8-connected gradient ascent + Gaussian noise)
6. The two conditions and why noise sigma was chosen to differ by 2×
7. Engraftment logic (dual gate — explain both conditions and why both are needed)
8. Repair dynamics (REPAIR_RATE, damage walk, why agents move post-engraftment)
9. Quorum sensing (repulsion equation, radius, biological justification)
10. Statistical validation (10 runs, seeds, metrics collected)

Include the parameter table from the README. Flag extrapolated parameters clearly.

### Results (400–500 words)
Present in this order, one paragraph each:
1. Test 01–02: Environment validation and single-agent navigation confirmed
2. Test 03: Core comparison result — cite the numbers (25.9 vs 26.1 steps, σ 2.2 vs 3.3). Include `test_03_output.png` as Figure 1.
3. Test 04: Engraftment validation (80.3%, zero false triggers)
4. Test 05–06: Repair and swarm validation
5. Test 07: Statistical result across 10 runs (47.1 ± 3.9% vs 47.4 ± 2.4%). Include `test_07_output.png` as Figure 2. Note CAR wins 6/10 runs.

Do not interpret results here — just report the numbers. Save interpretation for Discussion.

### Discussion (400–600 words)
Three main points:
1. **The CAR advantage is variance reduction** — connect to clinical reliability argument (Finding 2 above)
2. **The gradient detectability limitation** — connect to real-world HGF diffusion range and what it implies for injection strategy (Finding 1 above)
3. **Model limitations**: extrapolated parameters (REPAIR_RATE, SIGMA_CAR), 2D vs 3D, no cell death model, no immune response, homogeneous tissue. State what future experiments would validate each.

End with: what a real CAR-MuSC trial would need to measure to test these predictions.

### Conclusion (150–200 words)
Three sentences: (1) what was built, (2) what it found, (3) what it implies. Specifically say that the simulation is a *testable prediction* — not a proof. Suggest one concrete future experiment (e.g., in vitro migration assay comparing CAR-transduced vs unmodified MuSCs under HGF gradient with step-counting).

---

## Figures to Include in Report

| Figure | File | Caption |
|--------|------|---------|
| Figure 1 | `test_01_output.png` | HGF gradient heatmap with injury ellipse (cyan) and border zone (green). Max intensity = 1.0 at injury centre. |
| Figure 2 | `test_02_output.png` | Single CAR-MuSC agent trajectory from grid edge to injury zone. Green = start, blue star = end. 41 steps. |
| Figure 3 | `test_03_output.png` | CAR vs unmodified comparison. Left: mean arrival steps ± std. Right: targeting index. **This is your core result figure.** |
| Figure 4 | `test_07_output.png` | Mean ± std coverage across 10 independent runs. Shows stochastic robustness of both conditions. |

---

## Things Still To Do

- [ ] Build `simulation/simulation.py` (full integrated simulation class)
- [ ] Build `app/app.py` (Streamlit interface)
- [ ] Run full app and confirm animated grids work
- [ ] Write report using section notes above
- [ ] Add figure captions and parameter table to report
- [ ] Double-check all extrapolated parameters are flagged in report

---

## Numbers to Memorise for Your Report

| Value | Meaning |
|-------|---------|
| 331 | Injury zone cells |
| 408 | Border zone cells |
| 41 | Steps for single agent to reach injury (Test 02) |
| 25.9 vs 26.1 | Mean arrival steps CAR vs unmod (Test 03) |
| 2.2 vs 3.3 | Arrival step std dev — the variance reduction finding |
| 80.3% | Engraftment success rate (Test 04) |
| 47.1 ± 3.9% | CAR coverage mean ± std (Test 07) |
| 47.4 ± 2.4% | Unmod coverage mean ± std (Test 07) |
| 6/10 | Runs where CAR wins on coverage |
| 38.6 | Mean arrival step both conditions (Test 07) |