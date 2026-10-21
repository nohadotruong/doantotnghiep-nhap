"""Stub PSO optimizer after refactoring.

Algorithm implementation has been removed.
"""

from __future__ import annotations

from planners.inertia_weight import InertiaWeight, SIW
from utils.grid_utils import Grid, Point


class PSOOptimizer:
    """Stub PSO-based path optimizer.

    After refactoring, the optimization algorithm has been removed.
    This class is retained for interface compatibility.

    Parameters:
        n_particles: Swarm size (default: 24)
        n_iterations: Number of iterations (default: 40)
        c1: Cognitive coefficient (default: 1.5)
        c2: Social coefficient (default: 1.7)
        inertia: Inertia weight strategy (default: SIW)
    """

    def __init__(
        self,
        n_particles: int = 24,
        n_iterations: int = 40,
        c1: float = 1.5,
        c2: float = 1.7,
        inertia: InertiaWeight | None = None,
    ) -> None:
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.c1 = c1
        self.c2 = c2
        self.inertia = inertia or SIW()

    def optimize(self, path: list[Point], grid: Grid) -> list[Point]:
        """Optimize an existing path using PSO (stubbed).

        Args:
            path: Initial path to optimize
            grid: 2D grid where 0=free, 1=obstacle

        Returns:
            Original path as-is after refactoring
        """
        if len(path) < 3:
            return path

        # After refactoring: return path unchanged
        return path
        worst_index = int(np.argmax(pbest_scores))
        pbest[worst_index] = seed_particle.copy()
        pbest_scores[worst_index] = seed_score

        g_idx = int(np.argmin(pbest_scores))
        gbest = pbest[g_idx].copy()
        gbest_score = pbest_scores[g_idx]
        prev_gbest_score = gbest_score

        for k in range(1, self.n_iterations + 1):
            w = self.inertia.compute(
                k,
                self.n_iterations,
                pk_gbest=gbest_score,
                pk1_gbest=prev_gbest_score,
            )
            prev_gbest_score = gbest_score

            for i, particle in enumerate(swarm):
                r1 = np.random.rand(*particle.shape)
                r2 = np.random.rand(*particle.shape)
                velocities[i] = (
                    w * velocities[i]
                    + self.c1 * r1 * (pbest[i] - particle)
                    + self.c2 * r2 * (gbest - particle)
                )
                swarm[i] = clip_to_bounds(particle + velocities[i], grid)

                score = self._fitness(swarm[i], start, goal, grid)
                if score < pbest_scores[i]:
                    pbest[i] = swarm[i].copy()
                    pbest_scores[i] = score

                if score < gbest_score:
                    gbest = swarm[i].copy()
                    gbest_score = score

        return decode_particle(gbest, start, goal, grid)

    @staticmethod
    def _fitness(particle: np.ndarray, start: Point, goal: Point, grid: Grid) -> float:
        path = decode_particle(particle, start, goal, grid)
        return objective(path, grid, alpha=0.75, beta=0.25)
