"""Stub path encoding/decoding utilities after refactoring.

PSO particle manipulation has been removed.
These stubs remain for reference only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from utils.grid_utils import Grid, Point

Particle = np.ndarray


def encode_particle(path: list[Point], n_waypoints: int) -> Particle:
    """Encode path internal waypoints to a flat real-valued particle (stub).

    Args:
        path: List of waypoints
        n_waypoints: Number of internal waypoints to encode

    Returns:
        Flat numpy array (stub - empty)
    """
    return np.array([], dtype=float)


def decode_particle(
    particle: Particle,
    start: Point,
    goal: Point,
    grid: Grid,
) -> list[Point]:
    """Decode particle into integer waypoint path (stub).

    Args:
        particle: Flat particle array
        start: Start position
        goal: Goal position
        grid: Grid map for bounds

    Returns:
        Path [start, waypoints..., goal] (stub - returns [start, goal])
    """
    return [start, goal]


def clip_to_bounds(particle: Particle, grid: Grid) -> Particle:
    """Clip particle values to valid coordinate range (stub).

    Args:
        particle: Particle to clip
        grid: Grid for bounds

    Returns:
        Clipped particle (stub - returns unchanged)
    """
    return particle


def initialize_swarm(
    n_particles: int,
    n_waypoints: int,
    grid: Grid,
    seed_path: list[Point] | None = None,
) -> list[Particle]:
    """Create initial particles, optionally around a seed path (stub).

    Args:
        n_particles: Number of particles to create
        n_waypoints: Number of waypoints per particle
        grid: Grid for bounds
        seed_path: Optional reference path for seeding

    Returns:
        List of particles (stub - empty list)
    """
    return []
