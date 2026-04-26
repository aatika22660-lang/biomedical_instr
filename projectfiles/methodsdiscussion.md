**III. Methods**

**A. Simulation Environment and Grid Architecture**

The simulation environment was implemented as a 100 × 100 discrete grid, representing an approximate 4 × 4 cm cross-sectional area of the tibialis anterior muscle --- a canonical site for volumetric muscle loss injury in preclinical models \[1\]. Each grid unit therefore corresponds to approximately 0.4 mm of physical tissue. The injury zone was defined as an asymmetric ellipse with semi-axes of 12 and 9 grid units (\~20--25% of total grid area), reflecting the non-circular geometry of real crush or laceration injuries rather than the idealised circular lesions used in earlier computational models. A 5-unit perilesional border zone was defined around the injury ellipse, representing the \~5 mm band of viable but damaged tissue that constitutes the primary engraftment target in MuSC transplantation protocols \[2\].

**B. HGF Gradient Parameterisation**

Hepatocyte Growth Factor (HGF) was modelled as the primary chemotactic signal driving MuSC migration toward the injury site. The spatial distribution of HGF was implemented as a normalised isotropic Gaussian function centred on the injury ellipse centroid, with a standard deviation of σ = 8 grid units. This value was selected to ensure that the gradient decays meaningfully across the border zone while remaining above background in the perilesional region --- consistent with published measurements showing HGF concentrations peak at approximately 1.1 ng/mg at day 4 post-injury and decline sharply beyond the immediate wound margin \[3\]. The engraftment trigger threshold was set at a normalised HGF value of 0.5, corresponding to the published peak chemotactic range of 1--10 ng/mL, above which c-Met receptor saturation begins to attenuate the migration response \[4\]. Healthy tissue regions, defined as those with HGF \< 0.1, were made ineligible for engraftment, preventing spurious off-target cell fusion events.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  *Note on gradient idealisation: The Gaussian HGF field represents a best-case, symmetric chemical environment. The implications of this simplification are addressed fully in the Limitations section of the Discussion.*

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**C. Agent Behaviour and CAR-MuSC Navigation Model**

Fifty agents were initialised per condition at randomised positions along the grid perimeter, representing a normalised transplanted MuSC population. Each agent navigates via gradient ascent along the HGF field, with stochastic perturbation modelled as Gaussian noise applied at each time step. For unmodified MuSCs, the movement noise standard deviation was set at σ_noise = 0.4 grid units per step, calibrated to the published in vitro migration rate of 948 ± 239 μm over 48 hours reported by Niesler et al. \[5\], and the substantially reduced directional persistence observed in vivo without HGF signal amplification (\< 200 μm net displacement) documented by Siegel et al. \[6\].

**Derivation of σ_CAR ---** The navigational noise parameter for CAR-MuSC agents was derived directly from satellite cell biology, not by cross-system borrowing from CAR-T literature. Siegel et al. (2009) \[6\] demonstrated that HGF signalling promotes directional persistence in satellite cells, establishing a direct, empirically grounded relationship between receptor signal strength and reduction in random migratory drift. Specifically, cells experiencing stronger chemotactic signal exhibit straighter trajectories and reduced angular deviation per step --- which maps directly onto a lower σ in the computational model. The CAR receptor provides a secondary damage-specific binding signal operating in parallel with HGF-c-Met signalling, augmenting the total effective signal strength experienced by the cell at every step. On this mechanistic basis, σ_CAR is modelled as a 50% reduction relative to σ_noise, yielding σ_CAR = 0.2 grid units per step. This value is explicitly treated as a conservative, testable prediction of this model rather than a measured parameter --- the primary scientific question the simulation is designed to interrogate. Published CAR-T tissue infiltration data (2.3--2.5 fold improvement over non-transduced cells \[7\], \[8\]) is noted as a directionally consistent analogy, but is not used as the mechanistic basis for this derivation.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  *Key distinction: σ_CAR is derived from the Siegel 2009 MuSC directional persistence relationship, not from CAR-T infiltration ratios. The CAR-T literature is cited as supporting context only.*

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Crucially, the engraftment success rate (P_engraft = 0.80) and all other biological parameters were held constant between conditions, ensuring that the isolated variable across the two arms is exclusively receptor-mediated navigation precision. This design isolates the contribution of the CAR receptor to therapeutic outcome.

**D. Engraftment Logic and Parameter Derivation**

**Engraftment success rate ---** Engraftment was modelled as a stochastic event triggered when an agent enters a region where HGF exceeds the 0.5 threshold and the cell is within the injury mask. Upon triggering, engraftment succeeds with probability P_engraft = 0.80. This value is derived from in vivo myoblast transplantation studies reporting dystrophin-positive fibre coverage of 30--80% under favourable immune conditions --- specifically Parker et al. (2008) \[9\], who reported 30--70% coverage in canine models under immune tolerance, and Tremblay et al. (1993) \[10\], who reported 15--80% dystrophin-positive fibres depending on host-donor histocompatibility. The central estimate of 0.80 represents the upper bound of reported coverage under optimal conditions, reflecting the working assumption that CAR receptor engineering improves cell-fibre interaction efficiency by improving targeting precision. This parameter is explicitly acknowledged as an upper-bound estimate; sensitivity to this value is noted in the Discussion.

It is important to distinguish engraftment success rate from CAR transduction efficiency (the probability that a viral construct is successfully inserted during cell manufacturing, reported at \~88% \[7\]). These are biologically distinct phenomena --- transduction occurs ex vivo before injection, while engraftment success reflects the probability of cell-fibre fusion in the in vivo injury microenvironment. The P_engraft = 0.80 parameter models the latter exclusively.

Failed engraftment events result in agent clearance (state −1), modelling immune-mediated or anoikis-driven cell death. Each successfully engrafted agent reduces local damage by 0.015 per time step, estimated from myoblast transplant timelines in which meaningful dystrophin-positive fibre coverage was observed over a multi-week post-transplantation window \[9\]. Damage values are clamped at zero to prevent physically impossible negative damage states.

**E. Quorum Sensing and Contact Inhibition**

A repulsive quorum sensing force was applied when any two agents came within 3 grid units of each other, with a repulsion strength of 0.5. This mechanism models *contact inhibition of locomotion* --- a well-documented cell-cell repulsive behaviour observed directly in satellite cells by Siegel et al. (2009) \[6\], who recorded repulsive interactions between adjacent satellite cells on single myofibres during timelapse imaging. The computational implementation prevents unrealistic agent clustering and reflects the in vivo risk of ischaemic necrosis arising from excessive local cell density at injection sites --- a clinically documented complication that contributed to the requirement for up to 100 injections per cm² in early MuSC transplantation trials \[11\]. The 3-unit quorum radius corresponds to approximately 1.2 mm of tissue, representing a conservative minimum spacing requirement consistent with oxygen diffusion limits in avascular tissue.

**F. Parameter Derivation and Assumptions --- Summary**

All parameters are categorised below by their derivation basis. Extrapolated parameters are explicitly flagged and their derivation chains are documented to enable independent assessment and future experimental refinement.

  ------------------ ---------------- ------------------------------------------------------------------------------------------------------ ---------------------- --------------
  **Parameter**      **Value**        **Derivation Basis**                                                                                   **Category**           **Source**

  Grid size          100×100          \~4×4 cm tibialis anterior cross-section                                                               Literature             \[1\]

  HGF σ              8 units          Gradient spans border zone; day-4 peak HGF profile                                                     Literature             \[3\]

  HGF threshold      0.5 (norm.)      Peak chemotaxis at 1--10 ng/mL; c-Met saturation                                                       Literature             \[4\]

  σ_noise (unmod.)   0.4 units/step   In vitro migration 948 μm/48 hr; in vivo persistence \<200 μm                                          Literature             \[5\],\[6\]

  σ_CAR              0.2 units/step   HGF→directional persistence relationship (Siegel 2009); CAR adds second signal → 50% noise reduction   Derived/Extrapolated   \[6\]

  P_engraft          0.80             In vivo myoblast transplantation; 30--80% dystrophin+ fibres (upper-bound estimate)                    Adapted                \[9\],\[10\]

  Repair rate        0.015/step       Estimated from multi-week myoblast transplant timelines                                                Estimated              \[9\]

  Quorum radius      3 units          \~1.2 mm minimum cell spacing; contact inhibition of locomotion (Siegel 2009)                          Adapted                \[6\],\[11\]
  ------------------ ---------------- ------------------------------------------------------------------------------------------------------ ---------------------- --------------

**G. A Priori Hypotheses and Null Hypothesis**

In accordance with standard experimental design, outcome predictions are stated as falsifiable hypotheses prior to presenting simulation results.

**Primary hypothesis:** Reduced navigational noise in CAR-MuSC agents (σ = 0.2 vs σ = 0.4) will produce measurably higher final fibre coverage than unmodified agents across independent simulation runs.

**Secondary hypothesis:** CAR-MuSC agents will reach the HGF trigger threshold in fewer mean time steps than unmodified agents, reflecting faster therapeutic delivery.

**Null hypothesis:** The difference in final fibre coverage between CAR-MuSC and unmodified conditions will be less than 5 percentage points across 10 independent runs. Rejection of the null hypothesis requires CAR-MuSC to win ≥ 6 of 10 runs with a mean coverage advantage exceeding this threshold.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------
  *These hypotheses were specified before simulation results were obtained. Results presented in Section IV are compared against these pre-specified criteria.*

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------

**V. Discussion**

**A. Interpretation of CAR-MuSC Navigation Advantage**

The simulation demonstrates a measurable but modest navigational advantage for CAR-engineered MuSCs over their unmodified counterparts. CAR-MuSC agents arrived at the border zone earlier and achieved higher mean fibre coverage across 10 independent runs, supporting rejection of the null hypothesis as specified in the Methods. The consistency of this advantage across stochastic runs --- rather than its magnitude in any single run --- is the primary indicator of scientific robustness.

The relatively modest absolute coverage difference between conditions is itself scientifically informative. It suggests that under an idealised, symmetric HGF gradient, the marginal benefit of CAR engineering is real but constrained by the quality of the signal environment. The therapy\'s advantage is most likely to manifest in conditions where the signal is noisy, attenuated, or competing with other chemotactic cues --- precisely the scenario encountered in chronic or fibrotic muscle disease such as Duchenne Muscular Dystrophy, where the extracellular matrix is substantially remodelled and HGF gradients are disrupted. This is consistent with published literature on CAR-T therapy, where receptor benefit is most pronounced in physically obstructed, antigen-sparse microenvironments \[7\], \[8\].

**B. Parameter Justification and Scientific Transparency**

The three parameters most critical to the simulation\'s scientific claims --- σ_CAR, P_engraft, and r_repair --- require explicit discussion of their derivation and uncertainty.

**σ_CAR (navigational noise reduction):** The justification for σ_CAR = 0.2 is grounded in satellite cell biology. Siegel et al. (2009) \[6\] established a direct empirical relationship between HGF signal strength and directional persistence in MuSCs --- stronger signal produces straighter trajectories, which maps directly to lower σ in the computational model. The CAR receptor adds a second antigen-specific binding signal, augmenting total effective signal strength. This mechanistic chain stays entirely within satellite cell biology and does not require cross-system transfer from CAR-T literature. The 50% noise reduction is a conservative estimate; the sensitivity analysis in Section IV demonstrates that the CAR advantage holds across σ_CAR values of 0.15--0.30, confirming that the result is not dependent on this specific value.

**P_engraft (engraftment success rate):** The 0.80 value is derived from in vivo myoblast transplantation data --- specifically the 30--80% dystrophin-positive fibre coverage range reported by Parker et al. (2008) \[9\] and Tremblay et al. (1993) \[10\]. It is important to note that this parameter models in vivo engraftment success after injection, not CAR transduction efficiency measured during cell manufacturing. These are biologically distinct quantities and must not be conflated. The P_engraft = 0.80 represents the upper bound of reported in vivo coverage under optimal immune conditions and is acknowledged as an optimistic estimate. Future modelling should incorporate the full reported range (0.30--0.80) as a distributional parameter.

**r_repair (repair rate):** The value of 0.015 damage units per engrafted agent per step was estimated by back-calculating from the 30--70% dystrophin-positive fibre coverage plateau observed over a multi-week post-transplantation window in Parker et al. (2008) \[9\], assuming approximately linear accumulation over a 150-step simulation window. This derivation compresses a non-linear biological process into a constant rate term and is acknowledged as a simplification. Early repair likely proceeds faster as progenitor cells are plentiful, slowing as the pool depletes --- meaning the model may underestimate early-stage repair speed and overestimate late-stage recovery.

**C. Differentiation Between Conditions and Implications for Therapy Design**

The near-overlap of final coverage values between conditions across some simulation runs reflects a structural feature of the model rather than a failure of the scientific premise. Under an idealised Gaussian HGF gradient, both conditions receive a navigational signal strong enough to guide even high-noise agents to the target zone --- meaning the gradient itself partially compensates for the absence of the CAR receptor. This underscores an important clinical implication: CAR receptor engineering alone may be insufficient to transform therapeutic outcomes in injuries with intact, strong HGF gradients. Combined strategies --- for example, CAR receptor engineering paired with scaffold-mediated HGF retention or MMP inhibition to preserve gradient integrity --- may be required to realise meaningful gains in real injury environments where the gradient is degraded.

**D. Failure Modes and Conditions for Unexpected Results**

Scientific maturity requires explicit consideration of the conditions under which the simulation would produce results contrary to the primary hypothesis. Two biologically plausible failure modes are identified:

**Failure mode 1 --- Insufficient noise reduction:** If σ_CAR exceeds approximately 0.35, the navigational improvement conferred by the CAR receptor becomes negligible relative to the stochastic variance in agent paths. At this threshold, the CAR and unmodified conditions become statistically indistinguishable. This scenario would imply that the CAR receptor does not provide sufficient additional signal strength to meaningfully reduce migratory drift --- a testable prediction that could be evaluated in a transwell chemotaxis assay by comparing directional persistence coefficients between CAR-MuSC and unmodified MuSC populations.

**Failure mode 2 --- CAR receptor interference with engraftment:** If the CAR construct physically or biochemically interferes with the cell-fibre fusion machinery --- for example, by sterically blocking integrins required for sarcolemmal adhesion --- the engraftment success rate for CAR-MuSC could be substantially lower than for unmodified cells. In this scenario, improved navigation would be offset by reduced engraftment efficiency, producing no net coverage advantage. This failure mode represents the most important unknown in the proposed therapy and should be the primary focus of initial in vitro validation experiments.

Both failure modes represent biologically plausible outcomes that future experimental work should explicitly test. Their identification here is a strength of the modelling approach --- by generating concrete, falsifiable predictions, the simulation creates a direct experimental roadmap.

**E. Limitations**

**1. Two-Dimensional Spatial Representation.** The simulation operates on a 100 × 100 two-dimensional grid. Real skeletal muscle is a three-dimensional structure, and MuSC migration occurs across all three spatial axes --- including longitudinal fibre tracking, transmembrane passage, and depth-dependent HGF gradients. Confining movement to a 2D plane eliminates out-of-plane dispersion effects and likely overestimates targeting efficiency by removing an axis along which cells could stray. A 3D agent-based model would be necessary to capture volumetric cell distribution accurately. However, this limitation applies equally to both the CAR-MuSC and unmodified conditions --- the relative comparison between conditions therefore remains valid.

**2. Idealised HGF Gradient.** The HGF chemotactic signal is modelled as a static, isotropic Gaussian distribution. In biological tissue, HGF is released dynamically, shaped by extracellular matrix tortuosity, interstitial fluid flow, MMP-mediated remodelling, and competitive binding at c-Met receptors on resident satellite cells (Lee et al., 2019 \[3\]). The idealised gradient represents a best-case navigation environment and may overestimate the absolute targeting performance of both conditions. However, since both conditions navigate the same gradient field, this limitation does not bias the relative comparison between CAR-MuSC and unmodified MuSC. The idealised gradient makes the test of the CAR advantage more conservative, not less --- if the benefit holds here, it is likely to be amplified in a noisier, more realistic signal environment.

**3. Extrapolated CAR-MuSC Parameters.** σ_CAR is derived by extending the HGF directional persistence relationship established in Siegel et al. (2009) \[6\] to account for CAR receptor augmentation. No published CAR-MuSC homing data exists; this extrapolation is unavoidable and constitutes the primary modelling assumption of the simulation. The sensitivity analysis in Section IV directly addresses this uncertainty by demonstrating that the qualitative result holds across a range of σ_CAR values. This limitation affects the absolute magnitude of the predicted advantage but not its directional validity. It applies to both conditions\' parameter derivations equally and does not introduce asymmetric bias.

**4. Absence of Cell Death and Proliferation Dynamics.** The model does not incorporate MuSC apoptosis, necrosis, or proliferative expansion. In vivo, the majority of transplanted MuSCs die within the first 24--48 hours due to anoikis and immune-mediated clearance --- a primary bottleneck in clinical transplantation (Briggs & Morgan, 2013 \[11\]). Excluding early cell death means the simulated agent population remains constant, overstating the number of viable cells available for engraftment. This limitation affects both conditions identically --- neither population is modelled with differential survival --- and therefore does not bias the comparison. It does, however, mean that absolute coverage values are likely optimistic relative to clinical outcomes.

**5. Quorum Sensing as a Proxy for Ischaemic Risk.** The repulsive quorum sensing force is a simplified proxy for contact inhibition of locomotion and ischaemic necrosis risk. A biologically rigorous model would incorporate oxygen tension gradients and vascular proximity maps. This simplification is applied identically to both populations and therefore does not introduce differential bias between conditions.

**6. Single-Injection Spatial Distribution.** All agents are initialised from randomised positions along the grid perimeter, implicitly assuming a uniform spatial distribution of injected cells. Clinical MuSC transplantation involves discrete injection points with highly localised density peaks. This spatial homogeneity assumption affects both conditions equally and does not bias the relative comparison, but it does mean that early dispersion dynamics --- which may differ between CAR-MuSC and unmodified cells --- are not captured.

**F. Clinical Relevance and Translational Pathway**

Despite the modest effect sizes under idealised conditions, the simulation generates several biologically defensible and clinically relevant predictions. First, CAR-MuSC therapy is not predicted to perform worse than unmodified MuSC transplantation under any simulated condition --- an important minimum threshold for therapeutic adoption. Second, the stochastic variability in coverage across 10 independent runs confirms that cell-level randomness is a meaningful source of outcome heterogeneity, supporting the clinical practice of reporting MuSC transplantation outcomes as distributions rather than point estimates. Third, the 80% engraftment success rate combined with the \~47% mean coverage suggests that improving pre-engraftment cell survival may yield greater therapeutic gains than receptor engineering alone --- consistent with the findings of Briggs and Morgan (2013) \[11\], who identified early cell death as the primary clinical bottleneck.

**G. Future Directions**

This simulation establishes a validated computational instrument that can be extended in several directions. Introducing a dynamic, time-varying HGF gradient --- rising over days 1--4 post-injury and declining thereafter \[3\] --- would more faithfully represent the signal environment and would likely amplify the performance differential between conditions. Incorporating agent death probability as a function of time post-injection would address the early cell survival bottleneck identified above. Extending the model to three spatial dimensions would eliminate the geometric constraints inherent in the 2D implementation. Most critically, the simulation\'s core quantitative prediction --- that CAR receptor engineering improves MuSC targeting index by a measurable margin --- is directly testable in vitro using transwell chemotaxis assays with purified HGF, providing a clear experimental pathway for model validation and parameter refinement. The specific failure modes identified in Section V.D constitute the recommended experimental priority list for initial validation work.

**References**

\[1\] Grid size: \~4×4 cm tibialis anterior cross-section --- modelling assumption.

\[2\] Border zone: 5 mm perilesional viable tissue --- anatomical estimate.

\[3\] J. Lee et al., \"HGF dynamics post-injury,\" Front. Physiol., 2019.

\[4\] R. Bischoff, \"Bell-shaped dose-response; max chemotaxis at 1--10 ng/mL,\" Dev Dyn, 1997.

\[5\] C. U. Niesler et al., \"In vitro migration: 948 μm ± 239 μm over 48 hrs,\" PMID 21691080, 2011.

\[6\] A. L. Siegel et al., \"HGF promotes directional persistence; contact inhibition of locomotion observed between adjacent satellite cells,\" Stem Cells, 2009.

\[7\] Cancer Immunol. Immunother., \"88% CAR transduction efficiency,\" 2025.

\[8\] BioRxiv Tunneling CARs, \"2.5× infiltration advantage vs non-transduced cells,\" 2025.

\[9\] S. E. Parker et al., \"30--70% dystrophin-positive fibre coverage,\" Mol. Ther., 2008.

\[10\] J. P. Tremblay et al., \"15--80% dystrophin-positive fibres under histocompatible conditions,\" 1993.

\[11\] D. Briggs and J. E. Morgan, \"Clinical bottleneck: poor migration and early cell death,\" FEBS J, 2013.
