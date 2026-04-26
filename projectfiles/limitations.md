Here is the limitations section:

---

## Limitations

**1. Two-Dimensional Spatial Representation**

The simulation operates on a 100 × 100 two-dimensional grid representing a cross-sectional slice of the tibialis anterior muscle. Real skeletal muscle is a three-dimensional structure, and MuSC migration occurs across all three spatial axes — including longitudinal fibre tracking, transmembrane passage, and depth-dependent HGF gradients. Confining movement to a 2D plane artificially constrains agent trajectories, eliminates out-of-plane dispersion effects, and likely overestimates targeting efficiency by removing an entire axis along which cells could stray from the injury zone. A 3D agent-based model would be necessary to accurately capture volumetric cell distribution and the full geometric complexity of an in vivo injury site.

**2. Simplified HGF Gradient Model**

The HGF chemotactic signal is modelled as a static, isotropic Gaussian distribution centred on the injury ellipse. In biological tissue, HGF is released dynamically — its concentration rises over the first 72–96 hours post-injury, peaks around day 4, and then declines as repair progresses (Lee et al., 2019). Additionally, the gradient in vivo is shaped by extracellular matrix tortuosity, interstitial fluid flow, MMP-mediated remodelling, and competitive binding at c-Met receptors on resident satellite cells. None of these dynamics are captured here. A static gradient means agents always navigate in a consistent signal landscape, which almost certainly makes navigation easier than it would be in a real injury microenvironment, and may contribute to the unrealistically high targeting indices observed in Test 3 (100% for both conditions).

**3. Extrapolated CAR-MuSC Parameters**

The three most scientifically critical parameters in the model — the CAR noise reduction factor (κ_CAR = 0.5×), the engraftment success rate (P_engraft = 0.80), and the repair rate (r_repair = 0.015 per agent per step) — are extrapolated from CAR-T cell literature rather than derived from published CAR-MuSC experimental data. This is unavoidable given that CAR-MuSC therapy has not yet been trialled, but it introduces substantial parametric uncertainty. The 50% noise reduction assigned to the CAR receptor is a modelling assumption with no direct empirical basis in muscle stem cell biology. If the true homing advantage conferred by the CHR is smaller than assumed, the simulated benefit of CAR engineering would be proportionally diminished — consistent with the weak effect sizes observed in Test 7, where CAR and unmodified coverage means differed by less than 0.3 percentage points.

**4. Weak Differentiation Between Conditions**

A core finding from the test suite is that the performance gap between CAR-MuSC and unmodified MuSC is narrower than the biological literature would predict. In Test 7, CAR-MuSC achieved a mean fibre coverage of 47.1 ± 3.9% versus 47.4 ± 2.4% for unmodified cells — a difference that is not only small but directionally reversed from the hypothesis in several runs. CAR cells won only 6 of 10 simulations, barely exceeding the minimum pass threshold. This likely reflects the fact that the HGF gradient, as implemented, is sufficiently strong to guide even noisy unmodified agents reliably to the injury zone. The CAR receptor's navigational advantage is only meaningful when the signal environment is difficult enough to challenge unmodified cells — a condition not robustly present in the current parameter regime. Future iterations should consider steepening the gradient decay, increasing baseline movement noise, or introducing signal perturbations to create a more ecologically valid navigation challenge.

**5. Absence of Cell Death and Proliferation Dynamics**

The model does not incorporate MuSC apoptosis, necrosis, or proliferative expansion during the simulation window. In vivo, the majority of transplanted MuSCs die within the first 24–48 hours due to anoikis, immune-mediated clearance, and ischaemia at the injection site — a phenomenon well-documented as a primary bottleneck in clinical MuSC transplantation (Briggs & Morgan, 2013). Excluding early cell death means the simulated agent population remains constant throughout the run, overstating the number of viable cells available for engraftment at any given time step. Similarly, successful engraftment in vivo triggers satellite cell activation and proliferative expansion, which amplifies the repair signal in ways not modelled here. Both omissions bias the simulation toward more optimistic repair outcomes than would be observed experimentally.

**6. Quorum Sensing as a Proxy for Ischaemic Risk**

The repulsive quorum sensing force applied when agents come within 3 grid units of each other is a simplified proxy for the in vivo risk of ischaemic necrosis caused by excessive local cell density at the injection site. While the mechanism serves its functional purpose — preventing unrealistic clustering — it does not capture the underlying biology. True ischaemic necrosis is a threshold-dependent, time-sensitive process driven by oxygen diffusion limits, local vascularity, and the metabolic demand of densely packed cells. A biologically rigorous model would incorporate oxygen tension gradients, vascular proximity maps, and probabilistic necrosis rates as a function of local cell density, none of which are feasible within the current 2D discrete-time framework.

**7. Single-Injection Spatial Distribution**

All agents are initialised from randomised starting positions across the full grid, implicitly assuming a uniform spatial distribution of injected cells. Clinical MuSC transplantation, by contrast, involves discrete injection points — the 100 injections per cm² protocol referenced in the background section creates highly localised density peaks surrounded by uninjected tissue. This spatial heterogeneity fundamentally alters early migration dynamics, as cells near an injection cluster must first disperse before they can navigate directionally along the HGF gradient. Modelling a realistic injection geometry would require specifying injection point coordinates, local cell densities, and an initial dispersion phase prior to directed migration — a level of spatial detail beyond the current implementation.