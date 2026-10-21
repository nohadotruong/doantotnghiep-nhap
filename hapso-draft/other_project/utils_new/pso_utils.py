from environment.grid_map import GridMap
from typing import List, Optional, Tuple
import numpy as np


def encode_particle(path: List[Tuple[int, int]]) -> np.ndarray:
    particle = np.array(path, dtype=np.float32)
    return particle.flatten()


def decode_particle(
    particle: np.ndarray,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    num_waypoints: int,
) -> List[Tuple[int, int]]:
    particle = particle.reshape((num_waypoints, 2))
    path = [start]

    for i in range(len(particle)):
        x = int(round(particle[i, 0]))
        y = int(round(particle[i, 1]))
        path.append((x, y))

    path.append(goal)

    return path


def clip_to_bounds(
    particle: np.ndarray,
    grid: GridMap,
) -> np.ndarray:
    lb = np.array([0.0, 0.0], dtype=np.float32)
    ub = np.array([float(grid.width - 1), float(grid.height - 1)], dtype=np.float32)

    particle_reshaped = particle.reshape((-1, 2))
    particle_clipped = np.clip(particle_reshaped, lb, ub)
    return particle_clipped.flatten()


def initialize_swarm(
    n_particles: int,
    num_waypoints: int,
    grid: GridMap,
) -> List[np.ndarray]:
    swarm = []

    for _ in range(n_particles):
        particle = np.random.uniform(
            low=[0.0, 0.0],
            high=[float(grid.width - 1), float(grid.height - 1)],
            size=(num_waypoints, 2),
        ).astype(np.float32)

        particle = particle.flatten()
        particle = clip_to_bounds(particle, grid)
        swarm.append(particle)

    return swarm
