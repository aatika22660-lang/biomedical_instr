# simulation/environment.py — Shared grid, gradient, and mask functions
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from simulation.config import (
    GRID_SIZE, INFARCT_RX, INFARCT_RY, BORDER_WIDTH, SIGMA_HGF
)


def make_injury_mask(grid_size=GRID_SIZE, rx=INFARCT_RX, ry=INFARCT_RY):
    """Boolean mask: True inside the elliptical injury zone."""
    cx, cy = grid_size // 2, grid_size // 2
    xs, ys = np.arange(grid_size), np.arange(grid_size)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    injury_mask = ((X - cx)**2 / rx**2 + (Y - cy)**2 / ry**2) <= 1.0
    return injury_mask


def make_border_mask(injury_mask, border_width=BORDER_WIDTH,
                     rx=INFARCT_RX, ry=INFARCT_RY):
    """
    Boolean mask: ring of cells just outside the injury ellipse.

    Parameters
    ----------
    injury_mask  : np.ndarray bool — the inner ellipse mask
    border_width : int             — ring width in grid units
    rx, ry       : int             — semi-axes of the injury ellipse.
                                     Must match those used to build injury_mask.
                                     FIX: previously hardcoded INFARCT_RX/RY
                                     directly, which broke if a custom-sized
                                     injury mask was passed in.
    """
    grid_size = injury_mask.shape[0]
    cx, cy    = grid_size // 2, grid_size // 2
    rx_outer  = rx + border_width   # FIX: uses passed rx/ry, not hardcoded constants
    ry_outer  = ry + border_width
    xs, ys    = np.arange(grid_size), np.arange(grid_size)
    X, Y      = np.meshgrid(xs, ys, indexing='ij')
    outer       = ((X - cx)**2 / rx_outer**2 + (Y - cy)**2 / ry_outer**2) <= 1.0
    border_mask = outer & ~injury_mask
    return border_mask


def make_hgf_gradient(grid_size=GRID_SIZE, sigma=SIGMA_HGF):
    """Gaussian HGF gradient centred on the injury zone, normalised to [0,1]."""
    cx, cy = grid_size // 2, grid_size // 2
    xs, ys = np.arange(grid_size), np.arange(grid_size)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    dist_sq = (X - cx)**2 + (Y - cy)**2
    hgf = np.exp(-dist_sq / (2 * sigma**2))
    hgf /= hgf.max()          # normalise to [0, 1]
    return hgf


def random_edge_position(grid_size=GRID_SIZE, rng=None):
    """
    Return a random (x, y) position on the grid border.

    Note: not used by the main Simulation class, which uses
    random_perilesional_position() for biologically realistic spawning.
    Retained here for Tests 02, 03, and 06 which test edge-to-centre
    navigation as an isolated navigational benchmark.

    Parameters
    ----------
    grid_size : int                  — side length of the square grid
    rng       : np.random.Generator  — caller-supplied RNG for reproducibility.
                                       FIX: raises ValueError if None, preventing
                                       silent unreproducible behaviour from an
                                       untracked default_rng() being created.
    """
    if rng is None:
        raise ValueError(
            "random_edge_position() requires an explicit rng. "
            "Pass a np.random.default_rng(seed) instance. "
            "Creating a default RNG silently produces unreproducible results."
        )
    edge  = rng.integers(0, 4)
    coord = rng.integers(0, grid_size)
    if edge == 0:  return (0, coord)
    if edge == 1:  return (grid_size - 1, coord)
    if edge == 2:  return (coord, 0)
    return (coord, grid_size - 1)


def random_perilesional_position(grid_size=GRID_SIZE, spawn_radius=30, rng=None):
    """
    Return a random (x, y) position within the perilesional injection zone.

    Biological justification: clinical MuSC delivery targets the perilesional
    region — tissue immediately surrounding the injury — not distant injection
    sites. Spawning agents at radius ~30 grid units (~12 mm from injury centre)
    ensures they are within the detectable HGF gradient from step 1, making
    navigational noise the primary determinant of targeting success.

    Parameters
    ----------
    grid_size    : int                 — side length of the square grid
    spawn_radius : int                 — approximate distance from grid centre
                                         to spawn ring (grid units)
    rng          : np.random.Generator — caller-supplied RNG for reproducibility.
                                         Raises ValueError if None.

    Returns
    -------
    (x, y) : tuple of int — grid position on perilesional ring
    """
    if rng is None:
        raise ValueError(
            "random_perilesional_position() requires an explicit rng. "
            "Pass a np.random.default_rng(seed) instance."
        )

    cx, cy = grid_size // 2, grid_size // 2

    # Random angle around the injury centre
    angle = rng.uniform(0, 2 * np.pi)

    # Jitter the radius slightly so agents don't form a perfect ring
    # ± 5 grid units variation around spawn_radius
    r = spawn_radius + rng.integers(-5, 6)
    r = max(10, min(r, grid_size // 2 - 2))  # clamp — never too close or outside grid

    x = int(round(cx + r * np.cos(angle)))
    y = int(round(cy + r * np.sin(angle)))

    # Final clamp to grid bounds
    x = max(0, min(grid_size - 1, x))
    y = max(0, min(grid_size - 1, y))

    return (x, y)
