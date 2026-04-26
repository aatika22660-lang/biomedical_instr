# config.py — CAR-MuSC Simulation: Instrument Specifications
#
# Parameters are organised by their role in the closed-loop instrumentation
# architecture: Sensing → Signal Processing → Actuation → Feedback
#
# Sensing: HGF gradient (sensor signal)
# Signal Processing: Agent navigation algorithm + CAR noise-reduction model
# Actuation: Engraftment and fibre fusion (repair output)
# Feedback: Coverage metrics, targeting index, repair curve

# ── Instrument Environment — Physical Scale ───────────────────────────────────
# 100×100 grid representing ~4×4 cm tibialis anterior cross-section.
# Each grid unit ≈ 0.4 mm of physical tissue.
GRID_SIZE = 100
INFARCT_RX = 12 # Injury ellipse semi-axis x (~20–25% grid area)
INFARCT_RY = 9 # Injury ellipse semi-axis y (asymmetric, realistic)
BORDER_WIDTH = 5 # Perilesional border zone width (~5 mm viable tissue)

# ── Sensor Signal — HGF Chemotactic Gradient ─────────────────────────────────
# The HGF gradient is the primary sensor signal driving agent navigation.
# Modelled as a normalised Gaussian field (peak = 1.0 at injury centre).
# σ = 8 ensures gradient is detectable across the border zone.
# Threshold = 0.5 corresponds to peak chemotactic range 1–10 ng/mL (Bischoff 1997).
SIGMA_HGF = 8 # Gaussian spread of HGF sensor signal (grid units)
HGF_THRESHOLD = 0.5 # Sensor activation threshold — triggers engraftment gate
SIGMA_BROAD = 22        # Broad HGF sigma for edge-to-centre navigation tests.
                        # SIGMA_HGF=8 decays to ~0 at r=25; agents spawn at r=50.
                        # SIGMA_BROAD=22 keeps the gradient navigable from grid edges.
                        # Used in Tests 03 and 07 and the sensitivity analysis.

SIGMA_SIMULATION = 15   # Intermediate gradient for full simulation runs.
                        # At spawn radius 38: HGF ≈ 0.20 — gradient direction
                        # is detectable but weak enough that navigational noise
                        # is the primary determinant of targeting success.
                        # Creates the regime where σ_CAR=0.2 vs σ_noise=0.4
                        # produces a meaningful, reproducible coverage difference.

# ── Signal Processing — Agent Navigation Model ───────────────────────────────
# Agents climb the HGF gradient via discrete gradient ascent with
# stochastic noise modelling Brownian diffusion (unmodified) or
# receptor-guided navigation (CAR-MuSC).
NUM_AGENTS = 100 # Normalised transplanted MuSC population
SIGMA_NOISE = 0.4 # Unmodified MuSC: baseline navigational noise (σ)
# Calibrated to in vitro migration 948 μm/48 hr (Niesler 2011)
# and in vivo persistence <200 μm (Siegel 2009)

# ── Signal Amplifier — CAR Receptor Navigation Boost ─────────────────────────
# The CAR receptor provides a second damage-specific binding signal,
# augmenting the HGF sensor signal and increasing directional persistence.
# Mechanistic basis: Siegel et al. (2009) established a direct relationship
# between HGF signal strength and directional persistence in satellite cells.

# The CAR receptor adds a parallel signal → noise reduced by 50%.
# σ_CAR is the primary testable prediction of this instrument.
SIGMA_CAR = 0.2 # CAR-MuSC: amplified navigation (50% noise reduction)

# ── Actuator Output — Engraftment and Fibre Repair ───────────────────────────
# Engraftment is the actuation event: agent fuses with damaged fibre,
# converting navigational success into measurable repair output.
# P_engraft derived from in vivo myoblast transplantation data
# (Parker et al. 2008; Tremblay et al. 1993: 30–80% dystrophin+ fibres).
ENGRAFT_SUCCESS_RATE = 0.80 # Probability of successful fibre fusion
REPAIR_RATE = 0.015 # Damage reduction per engrafted agent per step
MAX_STEPS = 200 # Instrument run duration (sufficient for convergence)

# ── Collision Avoidance — Contact Inhibition of Locomotion ───────────────────
# Repulsive quorum sensing models contact inhibition observed between
# adjacent satellite cells in timelapse imaging (Siegel et al. 2009).
# Prevents unrealistic clustering and models ischaemic necrosis risk
# from excessive local cell density at injection sites.
QUORUM_RADIUS = 3 # Activation distance (~1.2 mm minimum cell spacing)
QUORUM_STRENGTH = 0.5 # Repulsive force magnitude
# ── Injection Zone — Perilesional Spawn Radius ────────────────────────────────
# Clinical MuSC delivery targets the perilesional region — tissue immediately
# surrounding the injury — not distant injection sites far from the gradient.
# SPAWN_RADIUS = 30 grid units ≈ 12 mm from injury centre.
# This ensures agents are within the detectable HGF gradient from step 1,
# making navigational noise the primary determinant of targeting success.
SPAWN_RADIUS = 30
# ── Statistical Validation ────────────────────────────────────────────────────
SENSITIVITY_RUNS = 20   # Independent runs per σ_CAR value in sensitivity analysis
