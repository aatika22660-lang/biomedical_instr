# CAR-MuSC: Chimeric Homing Receptor Simulation for Precision Muscle Regeneration

> **Biomedical Instrumentation — Interactive Simulation Project**  
> *A 2D agent-based model comparing unmodified MuSC therapy against CAR-engineered MuSC therapy for skeletal muscle regeneration*

---

## Overview

This project simulates a proposed biomedical therapy inspired by CAR-T cell engineering. Muscle-Derived Stem Cells (MuSCs) are engineered with a **Chimeric Homing Receptor (CHR)** that binds to damage-specific antigens on injured muscle fibres, upgrading their natural HGF-driven navigation from a random walk into a precision-guided system.

The simulation models the complete therapeutic pipeline:

```
HGF Signal → Cell Navigation → CAR Receptor Binding → Fibre Engraftment → Repair Metrics
```

This maps directly onto the closed-loop instrumentation architecture:
**Sensing → Processing → Actuation → Feedback**

---

## Background & Motivation

Skeletal muscle has a natural capacity for self-repair via **satellite cells** (MuSCs), guided by **Hepatocyte Growth Factor (HGF)** released at injury sites. However, in severe conditions such as:

- **Volumetric Muscle Loss (VML)** from trauma
- **Duchenne Muscular Dystrophy (DMD)**

...the endogenous repair system is overwhelmed. Transplanted MuSCs are poor navigators — the vast majority fail to reach the damaged zone, die within days, or engraft too far from the injury. Early clinical trials required up to **100 injections per cm²** of muscle surface, causing secondary tissue damage.

This project applies the CAR-T paradigm to muscle stem cells. CAR-T therapy achieves up to **88% transduction efficiency** and **2.5× higher tissue infiltration** vs non-transduced cells. CAR-MuSC therapy has not yet been trialled — this simulation is a **predictive model** of its expected benefit.

---

## Platform & Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Interface | Streamlit |
| Computation | NumPy |
| Visualisation | Matplotlib |

---

## Simulation Design

### Environment

- **Grid:** 100 × 100 units (~4 × 4 cm tibialis anterior cross-section)
- **Injury core:** Asymmetric ellipse (semi-axes 12 × 9 grid units; ~20–25% of grid area)
- **HGF gradient:** Gaussian distribution centred on injury, σ = 8 grid units
- **Border zone:** 5-unit wide ring around injury core — the engraftment target zone
- **Healthy tissue:** Remainder of grid (HGF < 0.1)

### Two Agent Conditions

The simulation runs two parallel populations for direct comparison:

| Parameter | Unmodified MuSC | CAR-MuSC |
|-----------|-----------------|----------|
| Movement noise (σ) | 0.4 grid units/step | 0.2 grid units/step |
| Navigation | HGF gradient + high drift | HGF gradient + receptor-guided |
| Engraftment trigger | HGF > 0.5 | HGF > 0.5 |
| Engraftment success rate | 80% | 80% |

> The difference between conditions is **purely navigation precision** — isolating the contribution of the CAR receptor to the therapeutic outcome.

### Agent State Machine

```
State 0  →  Migrating   (climbing HGF gradient toward injury)
State 1  →  Triggered   (HGF threshold reached, engraftment initiated)
State 2  →  Engrafted   (fused with damaged fibre, repair begins)
State -1 →  Failed      (engraftment unsuccessful, cell cleared)
```

### Repair Dynamics

- Each engrafted agent reduces local damage by **0.015 per time step**
- Damage is clamped at zero
- Coverage expected to plateau at **~60–70%** after ~150–200 steps

### Quorum Sensing

A repulsive force activates when two agents come within **3 grid units** of each other, preventing unrealistic clustering and modelling the in vivo risk of ischaemic necrosis from excessive local cell density.

---

## Biological Parameters

All parameters are anchored to literature-sourced values. Extrapolated parameters are clearly flagged.

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Grid size | N | 100 × 100 | ~4×4 cm muscle cross-section |
| Injury semi-axis (x) | r_x | 12 grid units | ~20–25% tibialis anterior area |
| Injury semi-axis (y) | r_y | 9 grid units | Asymmetric — realistic shape |
| Border zone width | w_b | 5 grid units | ~5 mm perilesional viable tissue |
| HGF gradient sigma | σ_HGF | 8 grid units | Gradient spans border zone |
| HGF trigger threshold | C_thresh | 0.5 (normalised) | Peak chemotactic range 1–10 ng/mL |
| CAR noise reduction | κ_CAR | 0.5× | *Extrapolated* from CAR-T infiltration data |
| Baseline movement noise | σ_noise | 0.4 grid units/step | Brownian diffusion — unmodified MuSC |
| CAR-enhanced noise | σ_CAR | 0.2 grid units/step | 50% reduction from CAR receptor boost |
| Engraftment success rate | P_engraft | 0.80 | *Adapted* from CAR transduction efficiency |
| Number of agents | N_agents | 50 | Normalised stem cell population |
| Quorum sensing radius | d_q | 3 grid units | Prevents injection-site clustering |
| Quorum sensing strength | q_str | 0.5 | Moderate repulsive force |
| Repair rate | r_repair | 0.015 per agent/step | *Estimated* from myoblast transplant timelines |
| Max simulation steps | T_max | 300 | Sufficient for convergence |
| Expected fibre coverage | θ_final | ~60–70% | Partial recovery — biologically realistic |

> **⚠ Extrapolated parameters:** `κ_CAR`, `P_engraft`, and `r_repair` are modelling assumptions based on analogous systems (CAR-T). No published CAR-MuSC homing data exists. This is the novel scientific question the simulation explores.

---

## User Interface Features

- **Side-by-side animated grids:** Unmodified MuSC vs CAR-MuSC running simultaneously
- **Parameter sliders:** Number of agents, CAR noise reduction factor, engraftment rate, repair rate
- **Live comparison graphs:** Repair curves for both conditions on the same axes
- **Real-time agent state counters:** Migrating / Triggered / Engrafted / Failed
- **End-of-run summary table:** Targeting index, mean arrival step, final coverage — both conditions
- **Multi-run mode:** 10 independent runs with mean ± std for statistical robustness

---

## Build Order & Testing

The project follows a **test-driven development** workflow. Each component must be validated in isolation before integration.

### Test Scripts

| Script | What It Tests | Pass Criteria |
|--------|---------------|---------------|
| `test_01_gradient.py` | Grid & HGF Gaussian generation | `max(C) == 1.0`, `min(C) < 0.05`, zone masks non-empty |
| `test_02_single_agent.py` | Single agent navigation & boundary enforcement | Agent reaches border zone within `max_steps` |
| `test_03_car_boost.py` | CAR vs unmodified comparison (core scientific test) | CAR arrives faster, higher targeting index |
| `test_04_engraftment.py` | Engraftment logic gate (1000 Monte Carlo trials) | Success rate = 80% ± 5%; no trigger in healthy tissue |
| `test_05_repair.py` | Damage reduction rate & floor clamping | Damage decreases; never goes below 0 |
| `test_06_swarm.py` | Quorum sensing & agent state accounting | All agents in-bounds; state counts sum to `num_agents` |
| `test_07_metrics.py` | Targeting index, coverage range, stochasticity | CAR-MuSC consistently outperforms on all metrics |

### Recommended Build Steps

```
Step 1  →  test_01_gradient.py       (confirm HGF grid is correct)
Step 2  →  test_02_single_agent.py   (confirm agent navigates correctly)
Step 3  →  test_03_car_boost.py      (confirm CAR outperforms unmodified)
Step 4  →  test_04_engraftment.py    (confirm 80/20 split over 1000 trials)
Step 5  →  test_05_repair.py         (confirm damage decreases correctly)
Step 6  →  test_06_swarm.py          (confirm swarm behaves correctly)
Step 7  →  test_07_metrics.py        (confirm metrics are plausible)
Step 8  →  Assemble full simulation from tested components
Step 9  →  Build Streamlit interface around working simulation
```

> Do not skip steps or build the full simulation before all tests pass.

---

## Expected Outcomes

| Metric | CAR-MuSC | Unmodified MuSC |
|--------|----------|-----------------|
| Final fibre coverage | ~63% ± 7% | ~45% ± 10% |
| Targeting index | > 65% of agents in injury zone | < 50% |
| Mean arrival step | Significantly earlier | Baseline |
| Stochasticity | Confirmed across 10 runs | Confirmed across 10 runs |

These results are biologically defensible. The CAR receptor **improves but does not perfect** the therapy — partial recovery reflects the realistic limitations of stem cell transplantation, consistent with published clinical and preclinical data.

---

## Key References

| # | Paper | What It Provides |
|---|-------|-----------------|
| 1 | Lee et al., *Front. Physiol.* 2019 | HGF baseline (120–160 pg/mg) and peak (1.1 ng/mg at day 4) |
| 2 | Bischoff, *Dev Dyn* 1997 | Bell-shaped dose-response; max chemotaxis at 1–10 ng/mL |
| 3 | Allen et al., *J Cell Physiol* 1995 | c-Met receptor on satellite cells; HGF activation mechanism |
| 4 | Niesler et al. 2011 (PMID 21691080) | In vitro migration: 948 μm ± 239 μm over 48 hrs |
| 5 | Siegel et al., *Stem Cells* 2009 | <200 μm in vivo without signal; HGF increases directional persistence |
| 6 | González et al., *Skelet. Muscle* 2017 | HGF drives directed migration via MMP/ERK |
| 7 | *Cancer Immunol. Immunother.* 2025 | 88% CAR transduction efficiency |
| 8 | BioRxiv Tunneling CARs 2025 | 53–73% unmodified T cell infiltration baseline |
| 9 | *Cell. Mol. Immunol.* 2024 | CAR infiltration advantage vs non-transduced cells |
| 10 | Parker et al., *Mol. Ther.* 2008 | 30–70% dystrophin-positive fibre coverage — plateau basis |
| 11 | Dohi et al., *Front. Cell Dev. Biol.* 2024 | Fusion rate improvement with scaffold support |
| 12 | Briggs & Morgan, *FEBS J* 2013 | Clinical bottleneck: poor migration & early cell death |

---

## Relevance to Biomedical Instrumentation

This project demonstrates all four components of a closed-loop biomedical sensing and actuation system:

| Instrumentation Layer | Biological Equivalent |
|-----------------------|-----------------------|
| **Sensing** | HGF gradient detected by c-Met; CAR receptor as second-order antigen sensor |
| **Processing** | Gradient-climbing algorithm + CAR noise-reduction model |
| **Actuation** | Engraftment and fibre fusion — the physical repair output |
| **Feedback** | Repair metrics (coverage, targeting index, repair curve slope) |

The Streamlit interface further reflects instrumentation principles: parameterised inputs, real-time measurement display, side-by-side condition comparison, and quantitative performance metrics.

---

## Scientific Novelty & Transparency

CAR-MuSC therapy has not been trialled in the form simulated here. This is a **predictive model of a proposed therapy** — a legitimate and valuable form of biomedical research. The simulation generates a testable prediction: that CAR receptor engineering will improve MuSC targeting index and fibre coverage by a quantifiable margin. This prediction could be validated by future in vitro or in vivo experiments.

---

*Biomedical Instrumentation — Simulation Project*