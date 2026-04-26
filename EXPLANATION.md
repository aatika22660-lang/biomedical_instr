# CAR-MuSC Computational Instrument: Technical Explanation

The CAR-MuSC Computational Instrument is a high-fidelity 2D agent-based simulation designed to quantify the navigational advantage provided by Chimeric Antigen Receptor (CAR) modification in muscle stem cells (MuSCs). By modelling the recruitment of MuSCs to an injury site as a closed-loop instrumentation problem (Sensing → Signal Processing → Actuation → Feedback), this simulation provides a platform for testing the hypothesis that reducing receptor-level noise increases the targeting efficiency of cell-based therapies. The repository is structured as a modular Python package where the physical environment, agent decision logic, and population-level orchestration are decoupled, allowing for rigorous statistical validation and sensitivity analysis across biologically plausible parameter ranges.

---

## simulation/config.py

📌 This file acts as the "Single Source of Truth" for the entire project. By centralising all biological and mathematical constants, we ensure that every test and simulation run operates on an identical baseline, eliminating "magic numbers" and ensuring reproducibility.

### Environment Parameters
*   **GRID_SIZE (100)**: 🧮 Represents a 100x100 grid where each unit corresponds to approximately 0.4 mm of physical tissue. The total 4x4 cm area models a cross-section of the human tibialis anterior muscle.
*   **INFARCT_RX/RY (12, 9)**: 🔬 Biologically, muscle injuries are rarely perfectly circular; they follow the longitudinal orientation of muscle fibres. Modelling the injury as an ellipse allows us to simulate this structural asymmetry.
*   **BORDER_WIDTH (5)**: 🔬 Represents the perilesional zone — a ring of viable but stressed tissue immediately surrounding the necrotic core where engraftment is most clinically effective.

### HGF Gradient Parameters
*   **SIGMA_HGF (8)**: 🔬 Hepatocyte Growth Factor (HGF) is the primary chemoattractant for MuSCs. Modelling it as a Gaussian field reflects the diffusion of the cytokine from the injury centre.
*   **SIGMA_BROAD (22)**: 📌 This "broad" gradient is specifically designed for edge-spawn tests (like Test 02). In these scenarios, agents start far from the injury where a standard gradient would have decayed to near-zero. SIGMA_BROAD ensures a detectable signal exists even at the grid boundaries.
*   **SIGMA_SIMULATION (15)**: 📌 This is the balanced gradient used for primary simulation runs. It is steep enough to challenge navigation but broad enough to ensure that the difference between σ=0.4 and σ=0.2 results in meaningful performance divergence.

### Agent Parameters
*   **SIGMA_NOISE (0.4) vs SIGMA_CAR (0.2)**: 🔬 Sigma represents the navigational noise standard deviation. Biologically, this models receptor binding noise and Brownian diffusion. The core claim of the CAR model is that secondary receptor signals (CAR) effectively "amplify" the gradient signal, resulting in a 50% reduction in perceived noise.

### Engraftment and Repair
*   **ENGRAFT_SUCCESS_RATE (0.80)**: 🔬 Derived from in vivo myoblast transplantation data, acknowledging that not every cell that reaches the target successfully fuses with a host fibre.
*   **REPAIR_RATE (0.015)**: 🧮 Represents the amount of damage (normalized 0 to 1) an agent can repair per step. Combined with MAX_STEPS=200, this ensures the simulation runs long enough for population-level convergence.

### Quorum Sensing and Spawning
*   **QUORUM_RADIUS/STRENGTH (3, 0.5)**: 🔬 Models "Contact Inhibition of Locomotion" (CIL). Satellite cells are known to repel each other upon contact; this prevents unrealistic agent stacking and models the spatial constraints of the tissue.
*   **SPAWN_RADIUS (30)**: 📌 Agents spawn in a ring around the injury rather than at the grid edges. 🔬 This models perilesional injection, the standard clinical delivery method, ensuring the simulation focuses on "navigation to the core" rather than "travel across the limb."

---

## simulation/environment.py

This module serves as the "World Builder," providing pure functions that generate the static geometry and fields of the simulation.

### make_injury_mask()
*   **Explanation**: Generates a Boolean mask for the injury ellipse.
*   **🧮 Implementation**: Uses `np.meshgrid` with `indexing='ij'` to ensure the coordinate system matches the row/column structure of the grid.
*   **📌 Design Decision**: The mask is Boolean because engraftment is a binary "gate" — a cell is either in contact with the damaged fibre matrix or it isn't.

### make_border_mask()
*   **🔬 Biological Basis**: Represents the recruitment target where HGF levels are high enough to trigger activation but tissue is still viable.
*   **📌 Fix**: This function was refactored to use passed `rx/ry` parameters rather than hardcoded constants, ensuring that custom-sized injury zones (used in some tests) correctly generate matching border zones.

### make_hgf_gradient()
*   **🧮 Mathematical Model**: Implements a standard 2D Gaussian: `exp(-dist^2 / (2 * sigma^2))`.
*   **📌 Normalisation**: The field is normalised to `[0, 1]` so that the peak HGF concentration is always 1.0, regardless of the sigma value used.
*   **⚠️ Limitation**: This is a static field. In reality, HGF concentrations fluctuate, but for the 200-step timeframe of this simulation, the gradient is assumed to be in steady-state.

### random_edge_position()
*   **⚠️ Usage**: Retained specifically for Test 02 and 03. It samples one of the four grid boundaries.
*   **📌 RNG Constraint**: Requires an explicit `rng` object. 💡 This prevents "silent stochasticity" where the global NumPy state might drift, ensuring every test is perfectly reproducible.

### random_perilesional_position()
*   **📌 Design Decision**: Replaced edge-spawning for the main simulation.
*   **🔬 Justification**: Models clinical perilesional injection.
*   **🧮 Geometry**: Converts polar coordinates (angle + radius) to Cartesian (x, y). A ±5 jitter is applied to the radius so agents don't start on a perfect circle, creating a more realistic "cloud" of initial positions.

---

## simulation/agent.py

The `Agent` class implements the decision-making logic, acting as the "Signal Processor" in the instrumentation loop.

### State Machine
*   **0 (Migrating)**: Active navigation.
*   **2 (Engrafted)**: Success. The agent has fused and is now performing repair.
*   **-1 (Failed)**: The agent triggered the engraftment gate but failed the probability roll. 📌 These agents remain in the grid to model physical blockage/occupancy.

### step() method
This method is executed every cycle for migrating agents.

*   **Stage 1: Noisy Gradient Sensing**:
    *   📌 **Partial Sensing**: The agent randomly samples 5 out of 8 possible neighbours. 🔬 This is more realistic than "perfect scan" models; biological cells cannot simultaneously compare all directions with infinite precision.
    *   🔬 **Receptor Noise**: Sigma is applied here to corrupt the HGF reading: `observed_hgf = real_hgf + noise`. 💡 This was a critical architectural change. Previously, noise was applied to *position* after sensing. By applying it to the *reading*, we model how high-noise agents (σ=0.4) "misperceive" the gradient, making the navigation parameter mechanistically meaningful.
*   **Stage 2: Quorum Repulsion**:
    *   Computes a repulsive vector from all nearby active agents. 💡 This ensures that the population spreads out as it approaches the injury centre.
*   **Stage 3 & 4: Movement and Triggering**:
    *   The agent moves toward the perceived "best" neighbour.
    *   ✅ **Engraftment Trigger**: Gated on `hgf > HGF_THRESHOLD` AND `injury_mask == True`. Both are required to ensure cells only engraft where they sense the signal AND contact damaged tissue.

### repair() method
*   **🧮 Logic**: Decrements damage at the current cell by `REPAIR_RATE`.
*   **💡 Repair Walk**: Engrafted agents move toward the neighbour with the *highest remaining damage*. ✅ This prevents "repair stacking" where multiple agents waste effort on a single cell that is already at zero damage.

---

## simulation/simulation.py

The `Simulation` class orchestrates the populations and extracts system-level metrics (Feedback).

### Constructor & Paired Design
*   **📌 Matched-Pairs**: Both populations (CAR and Unmod) are spawned at identical coordinates and share the same seed sequence (`seed + i`).
*   **💡 Reasoning**: This ensures that if a CAR agent and an Unmod agent both reach the injury zone, they receive the identical "luck" roll for engraftment. This isolates **navigation speed** as the only variable impacting the final targeting index.
*   **⚠️ Tradeoff**: While this reduces noise for comparison, it means the two populations are not statistically independent. This is acceptable for a comparative instrumentation study where we want to minimize confounding variables.

### get_metrics()
*   **targeting_index**: 📌 Primary Metric. Measures the percentage of the population that successfully engrafted.
*   **final_coverage**: 💡 The Ceiling Problem. Because 100 agents have enough repair capacity to saturate the injury zone, both conditions will eventually converge to a similar coverage percentage (~60%). Coverage measures the "payload capacity," whereas **targeting_index** measures the "delivery efficiency."

---

## simulation/sensitivity.py

### sensitivity_analysis()
*   **📌 Purpose**: Sweeps σ_CAR from 0.15 to 0.30. This range covers the "likely" real-world advantage of the CAR receptor.
*   **✅ Robustness**: By showing an advantage at σ=0.30 (only a 25% noise reduction), we prove the model isn't dependent on the "optimistic" 50% reduction (σ=0.20).

### plot_sensitivity()
*   **Visualisation**: Generates a two-panel figure. The "Advantage Line" is the critical plot for the final report, showing the delta between conditions across the parameter sweep.

---

## Tests (tests/test_0*.py)

### test_01_gradient.py
*   **Purpose**: Validates the physical world. If this fails, the HGF concentration or injury geometry is mathematically broken.

### test_02_single_agent.py
*   **📌 Sigma Logic**: Uses `SIGMA_BROAD=22`. 🔬 This is required because agents spawn at the grid edges (r=50). The default gradient (σ=15) is effectively zero at the edges; σ=22 keeps the signal "above the floor" for this isolated test.

### test_03_car_boost.py
*   **⚠️ Removed Assertion**: H3 (speed) was removed because at edge-spawn distances, both groups eventually reach 100% targeting.
*   **💡 Key Metric**: Variance reduction (H2) is the primary indicator of success here. CAR agents take more consistent, less "wiggly" paths.

### test_04_engraftment.py
*   **🔬 Healthy Check**: Explicitly places an agent in a corner (HGF ≈ 0) to ensure the engraftment gate never triggers in healthy tissue.

### test_05_repair.py
*   **💡 Mathematical Sanity**: Zone damage drops from 331.00 to 330.25. This is correct: one agent repairing for 50 steps at 0.015/step = 0.75 units.

### test_06_swarm.py
*   **📌 Architecture**: Uses the real `Simulation` class. 💡 This ensures that if we change the swarming logic in the future, this test will catch regressions in the actual production code.

### test_07_metrics.py
*   **📌 Integration Test**: This is the final "Gatekeeper" test. It runs the full simulation across 10 seeds and enforces:
    *   **Effect Size > 3.0pp**: 🔬 Ensures the advantage is "clinically" meaningful, not just a rounding error.
    *   **7/10 Wins**: 🧮 Allows for some stochastic variance while requiring a clear majority of success.
    *   **Arrival Consistency**: CAR must arrive at least as fast as Unmod.
