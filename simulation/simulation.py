"""
simulation.py
CAR-MuSC Simulation — Simulation Orchestrator

Simulation class:
    __init__      — builds environment, spawns both populations
    step()        — advances all agents, updates damage, records metrics
    run()         — loops n_steps calling step()
    get_metrics() — returns targeting index, mean arrival, final coverage

Module-level function:
    sensitivity_analysis() — sweeps σ_CAR across [0.15, 0.20, 0.25, 0.30]
                             and returns coverage results for each value,
                             confirming the CAR advantage is robust to the
                             primary modelling assumption.

Two parallel populations are always run together so they share the same
random seed baseline, making condition comparisons fair.
"""

import numpy as np
from simulation.config import (
    GRID_SIZE, NUM_AGENTS, MAX_STEPS,
    SIGMA_NOISE, SIGMA_CAR, SIGMA_BROAD, REPAIR_RATE, ENGRAFT_SUCCESS_RATE
)
from simulation.environment import (
    make_hgf_gradient, make_injury_mask, make_border_mask,
    random_edge_position
)
from simulation.agent import Agent


class Simulation:
    """
    Full CAR-MuSC vs Unmodified MuSC comparison simulation.

    Parameters
    ----------
    n_agents     : int   — agents per condition (default NUM_AGENTS = 50)
    sigma_unmod  : float — unmodified noise σ (default SIGMA_NOISE = 0.4)
    sigma_car    : float — CAR-MuSC noise σ (default SIGMA_CAR = 0.2)
    engraft_rate : float — engraftment success probability (default ENGRAFT_SUCCESS_RATE)
    repair_rate  : float — damage reduction per agent per step
    seed         : int   — base RNG seed for reproducibility
    """

    def __init__(
        self,
        n_agents     = NUM_AGENTS,
        sigma_unmod  = SIGMA_NOISE,
        sigma_car    = SIGMA_CAR,
        engraft_rate = ENGRAFT_SUCCESS_RATE,  # FIX 3: was None, now wired through
        repair_rate  = REPAIR_RATE,
        seed         = 0,
    ):
        self.n_agents     = n_agents
        self.repair_rate  = repair_rate
        self.current_step = 0
        self.seed         = seed

        # ── Environment ───────────────────────────────────────────────────────
        self.hgf_grid = make_hgf_gradient(sigma=SIGMA_BROAD)
        self.injury_mask = make_injury_mask()
        self.border_mask = make_border_mask(self.injury_mask)

        # Two independent damage grids — one per condition
        self.damage_unmod    = np.where(self.injury_mask, 1.0, 0.0)
        self.damage_car      = np.where(self.injury_mask, 1.0, 0.0)
        self._initial_damage = float(self.damage_unmod.sum())

        # ── Spawn positions — use a dedicated seed-based RNG for positions only
        # so agent RNGs (below) are fully independent of spawn locations
        spawn_rng = np.random.default_rng(seed)
        unmod_positions = [random_edge_position(rng=spawn_rng) for _ in range(n_agents)]  # FIX 1: keyword arg
        car_positions   = [random_edge_position(rng=spawn_rng) for _ in range(n_agents)]  # FIX 1: keyword arg

        # ── Spawn agents — each agent gets its own independently seeded RNG ──
        # FIX 2: per-agent RNGs instead of one shared self.rng
        # Unmod agents: seeds seed+0 … seed+49
        # CAR agents:   seeds seed+100 … seed+149  (offset prevents collision)
        self.unmod_agents = [
            Agent(
                x=x, y=y,
                sigma=sigma_unmod,
                rng=np.random.default_rng(seed + i),
                injury_mask=self.injury_mask,
                engraft_rate=engraft_rate,   # FIX 3: wired through to Agent
            )
            for i, (x, y) in enumerate(unmod_positions)
        ]
        self.car_agents = [
            Agent(
                x=x, y=y,
                sigma=sigma_car,
                rng=np.random.default_rng(seed + 100 + i),
                injury_mask=self.injury_mask,
                engraft_rate=engraft_rate,   # FIX 3: wired through to Agent
            )
            for i, (x, y) in enumerate(car_positions)
        ]

        # ── Metrics history ───────────────────────────────────────────────────
        self.history = []

    # ── Single time step ──────────────────────────────────────────────────────

    def step(self):
        """
        Advance the simulation by one time step.

        Order per step:
            1. All unmodified agents move / engraft
            2. All CAR agents move / engraft
            3. All engrafted agents repair their local damage
            4. Record per-step metrics snapshot
        """
        s = self.current_step

        # Move
        for agent in self.unmod_agents:
            agent.step(self.hgf_grid, self.unmod_agents, s)
        for agent in self.car_agents:
            agent.step(self.hgf_grid, self.car_agents, s)

        # Repair
        for agent in self.unmod_agents:
            agent.repair(self.damage_unmod)
        for agent in self.car_agents:
            agent.repair(self.damage_car)

        # Snapshot
        self.history.append(self._snapshot())
        self.current_step += 1

    def _snapshot(self):
        """Return a lightweight metrics dict for the current step."""

        # FIX 4 & 5: removed 'triggered' key — state 1 is never used.
        # Dict now cleanly maps the three real states: 0, 2, -1.
        def counts(agents):
            c = {0: 0, 2: 0, -1: 0}
            for a in agents:
                if a.state in c:
                    c[a.state] += 1
            return c

        uc = counts(self.unmod_agents)
        cc = counts(self.car_agents)

        unmod_damage_remaining = float(self.damage_unmod[self.injury_mask].sum())
        car_damage_remaining   = float(self.damage_car[self.injury_mask].sum())

        return {
            'step'                   : self.current_step,
            'unmod_migrating'        : uc[0],
            'unmod_engrafted'        : uc[2],
            'unmod_failed'           : uc[-1],
            'car_migrating'          : cc[0],
            'car_engrafted'          : cc[2],
            'car_failed'             : cc[-1],
            'unmod_damage_remaining' : unmod_damage_remaining,
            'car_damage_remaining'   : car_damage_remaining,
            'unmod_coverage_pct'     : self._coverage(unmod_damage_remaining),
            'car_coverage_pct'       : self._coverage(car_damage_remaining),
        }

    def _coverage(self, damage_remaining):
        """Percentage of injury zone damage that has been repaired."""
        if self._initial_damage == 0:
            return 0.0
        repaired = self._initial_damage - damage_remaining
        return max(0.0, repaired / self._initial_damage * 100.0)

    # ── Full run ──────────────────────────────────────────────────────────────

    def run(self, n_steps=MAX_STEPS):
        """
        Execute n_steps time steps.

        Parameters
        ----------
        n_steps : int — number of steps to run (default MAX_STEPS = 300)
        """
        for _ in range(n_steps):
            self.step()

    # ── Metrics ───────────────────────────────────────────────────────────────

    def get_metrics(self):
        """
        Return summary metrics for both conditions after the run.

        Returns
        -------
        dict with keys:
            unmod_targeting_index — % of unmodified agents that engrafted
            car_targeting_index   — % of CAR agents that engrafted
            unmod_mean_arrival    — mean step at which unmodified agents engrafted
            car_mean_arrival      — mean step at which CAR agents engrafted
            unmod_final_coverage  — % injury zone repaired (unmodified)
            car_final_coverage    — % injury zone repaired (CAR)
        """
        def targeting_index(agents):
            engrafted = [a for a in agents if a.state == 2]
            return len(engrafted) / len(agents) * 100.0 if agents else 0.0

        def mean_arrival(agents):
            # arrival_step is only set on successful engraftment (fixed in agent.py)
            arrivals = [a.arrival_step for a in agents if a.arrival_step is not None]
            return float(np.mean(arrivals)) if arrivals else float(MAX_STEPS)

        unmod_damage_remaining = float(self.damage_unmod[self.injury_mask].sum())
        car_damage_remaining   = float(self.damage_car[self.injury_mask].sum())

        return {
            'unmod_targeting_index' : targeting_index(self.unmod_agents),
            'car_targeting_index'   : targeting_index(self.car_agents),
            'unmod_mean_arrival'    : mean_arrival(self.unmod_agents),
            'car_mean_arrival'      : mean_arrival(self.car_agents),
            'unmod_final_coverage'  : self._coverage(unmod_damage_remaining),
            'car_final_coverage'    : self._coverage(car_damage_remaining),
        }


# ── Sensitivity Analysis ──────────────────────────────────────────────────────
# Moved to simulation/sensitivity.py per roadmap Step 12.
# Import from there:
#   from simulation.sensitivity import sensitivity_analysis, plot_sensitivity