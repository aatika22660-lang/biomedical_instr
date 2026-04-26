"""
agent.py
CAR-MuSC Simulation — Agent Module

Agent state machine:
    0  ->  Migrating   (climbing HGF gradient toward injury)
    2  ->  Engrafted   (fused with fibre, repair begins)
   -1  ->  Failed      (engraftment unsuccessful, cell cleared)

The only difference between unmodified MuSC and CAR-MuSC agents is
the noise sigma passed at construction — isolating receptor-mediated
navigation as the independent variable.
"""

import os
import sys
# Add project root to sys.path to allow absolute imports from 'simulation' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from simulation.config import (
    GRID_SIZE, HGF_THRESHOLD, ENGRAFT_SUCCESS_RATE,
    REPAIR_RATE, QUORUM_RADIUS, QUORUM_STRENGTH
)

# 8-connected neighbour offsets
_NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1),
               ( 0, -1),          ( 0, 1),
               ( 1, -1), ( 1, 0), ( 1, 1)]


def _clamp(v, lo=0, hi=GRID_SIZE - 1):
    return max(lo, min(hi, v))


class Agent:
    """
    A single MuSC (modified or unmodified) navigating the HGF field.

    Parameters
    ----------
    x, y         : int   -- initial grid position
    sigma        : float -- movement noise standard deviation
    rng          : np.random.Generator -- shared RNG from the Simulation
    injury_mask  : np.ndarray bool -- needed to gate engraftment to injury zone
    engraft_rate : float -- probability of successful engraftment on trigger
                           (default: ENGRAFT_SUCCESS_RATE from config)
    """

    def __init__(self, x: int, y: int, sigma: float,
                 rng: np.random.Generator, injury_mask: np.ndarray,
                 engraft_rate: float = ENGRAFT_SUCCESS_RATE):
        self.x            = x
        self.y            = y
        self.sigma        = sigma
        self.rng          = rng
        self.injury_mask  = injury_mask
        self.engraft_rate = engraft_rate

        # State: 0=migrating, 2=engrafted, -1=failed
        self.state        = 0
        self.arrival_step = None   # step at which engraftment succeeded

    # -- Navigation -----------------------------------------------------------

    def step(self, hgf_grid: np.ndarray, all_agents: list, current_step: int):
        """
        Advance the agent one time step.

        Only active (state == 0) agents move. Engrafted / failed agents
        stay in place (repair is handled separately via repair()).

        Parameters
        ----------
        hgf_grid     : np.ndarray (GRID_SIZE, GRID_SIZE) -- HGF concentration
        all_agents   : list[Agent] -- full population for quorum sensing
        current_step : int         -- used to record arrival_step
        """
        if self.state != 0:
            return

        x, y = self.x, self.y

        # 1. Noisy, partial gradient sensing
        # Sample only 5 random neighbours to model imperfect sensing
        sampled_neighbours = self.rng.choice(_NEIGHBOURS, size=5, replace=False)

        best_val = -np.inf
        best_dx, best_dy = 0, 0

        for dx, dy in sampled_neighbours:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                # Add receptor-level noise to the HGF reading
                observed_hgf = hgf_grid[nx, ny] + self.rng.normal(0, self.sigma * 0.5)
                if observed_hgf > best_val:
                    best_val         = observed_hgf
                    best_dx, best_dy = dx, dy

        # 2. Quorum sensing -- repel from nearby active neighbours
        rep_x, rep_y = 0.0, 0.0
        for other in all_agents:
            if other is self or other.state != 0:
                continue
            dist = np.sqrt((x - other.x) ** 2 + (y - other.y) ** 2)
            if 0 < dist <= QUORUM_RADIUS:
                rep_x += (x - other.x) / dist * QUORUM_STRENGTH
                rep_y += (y - other.y) / dist * QUORUM_STRENGTH

        # 3. Apply movement (noise is now integrated into sensing)
        self.x = _clamp(int(round(x + best_dx + rep_x)))
        self.y = _clamp(int(round(y + best_dy + rep_y)))

        # 5. Check engraftment trigger -- must be in injury zone above threshold
        if (hgf_grid[self.x, self.y] > HGF_THRESHOLD
                and self.injury_mask[self.x, self.y]):
            self.arrival_step = current_step
            self.engraft()

    # -- Engraftment ----------------------------------------------------------

    def engraft(self):
        """
        Run engraftment logic using self.engraft_rate.

        Success (p = self.engraft_rate) -> state 2  (engrafted, repair begins)
        Failure (p = 1 - engraft_rate)  -> state -1 (cleared)
        """
        if self.rng.random() < self.engraft_rate:
            self.state = 2    # engrafted
        else:
            self.state = -1   # failed

    # -- Repair ---------------------------------------------------------------

    def repair(self, damage_grid: np.ndarray):
        """
        Reduce local damage if this agent is successfully engrafted.

        Each engrafted agent reduces damage at its current cell by
        REPAIR_RATE per step. Damage is clamped at zero.

        Parameters
        ----------
        damage_grid : np.ndarray (GRID_SIZE, GRID_SIZE)
            Mutable damage array updated in-place.
        """
        if self.state != 2:
            return

        damage_grid[self.x, self.y] = max(
            0.0,
            damage_grid[self.x, self.y] - REPAIR_RATE
        )

        # Bias toward the highest remaining damage cell in the neighbourhood
        # so engrafted agents spread repair rather than stacking on one cell.
        #
        # Intentional behaviour: if all neighbouring cells are fully repaired
        # (damage == 0.0), best_val stays -np.inf and best_x/best_y stay at
        # self.x, self.y — the agent stops moving. This is correct: an agent
        # in a fully-repaired zone has nothing left to do. repair() will still
        # be called each step but the damage clamp (max 0.0) means it has no
        # further effect. No guard clause is needed.
        best_val       = -np.inf
        best_x, best_y = self.x, self.y
        for dx, dy in _NEIGHBOURS:
            nx, ny = self.x + dx, self.y + dy
            if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE
                    and self.injury_mask[nx, ny]):
                if damage_grid[nx, ny] > best_val:
                    best_val       = damage_grid[nx, ny]
                    best_x, best_y = nx, ny

        self.x, self.y = best_x, best_y
