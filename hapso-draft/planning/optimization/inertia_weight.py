"""
PSO inertia weight strategies.

Implements 4 inertia weight strategies for PSO algorithms.
For production use, refactor from other_project/utils/inertia_weight.py
"""

from abc import ABC, abstractmethod
import math
import random


class InertiaWeightStrategy(ABC):
    """Base class for inertia weight strategies."""

    @abstractmethod
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        """
        Compute inertia weight for iteration k of t_max total iterations.

        Args:
            k: Current iteration (0-indexed)
            t_max: Maximum iterations
            **kwargs: Strategy-specific parameters

        Returns:
            Inertia weight value (typically 0.0 to 1.0)
        """
        pass


class LinearDecreasingInertiaWeight(InertiaWeightStrategy):
    """Linear decreasing inertia weight (LDIW)."""

    def __init__(self, w_max: float = 0.9, w_min: float = 0.4):
        """Initialize with max and min inertia weights."""
        self.w_max = w_max
        self.w_min = w_min

    def compute(self, k: int, t_max: int, **kwargs) -> float:
        """w = w_max - (w_max - w_min) * (k / t_max)"""
        if t_max == 0:
            return self.w_min
        return self.w_max - (self.w_max - self.w_min) * (k / t_max)


class NonlinearDecreasingInertiaWeight(InertiaWeightStrategy):
    """Nonlinear decreasing inertia weight (NDIW)."""

    def __init__(self, w_max: float = 0.9, w_min: float = 0.4):
        """Initialize with max and min inertia weights."""
        self.w_max = w_max
        self.w_min = w_min

    def compute(self, k: int, t_max: int, **kwargs) -> float:
        """w = w_min + (w_max - w_min) * exp(-2*k/t_max)"""
        if t_max == 0:
            return self.w_min
        exponent = -2.0 * k / t_max
        return self.w_min + (self.w_max - self.w_min) * math.exp(exponent)


class AdaptiveInertiaWeight(InertiaWeightStrategy):
    """Adaptive inertia weight (AIW) based on fitness diversity."""

    def __init__(self, w_max: float = 0.9, w_min: float = 0.4):
        """Initialize with max and min inertia weights."""
        self.w_max = w_max
        self.w_min = w_min

    def compute(self, k: int, t_max: int, **kwargs) -> float:
        """w adapts based on fitness diversity (requires fitness_ratio in kwargs)"""
        fitness_ratio = kwargs.get("fitness_ratio", 0.5)  # Default to middle value

        if fitness_ratio > 0.0:
            return self.w_max
        else:
            return self.w_min


class StochasticInertiaWeight(InertiaWeightStrategy):
    """Stochastic inertia weight (SIW) with random perturbation."""

    def __init__(self, w_max: float = 0.9, w_min: float = 0.4):
        """Initialize with max and min inertia weights."""
        self.w_max = w_max
        self.w_min = w_min

    def compute(self, k: int, t_max: int, **kwargs) -> float:
        """w = (w_max - (w_max-w_min)*(k/t_max)) * exp(rb), rb ~ U(-0.1, 0.1)"""
        if t_max == 0:
            return self.w_min

        # Base weight from linear decreasing
        w_base = self.w_max - (self.w_max - self.w_min) * (k / t_max)

        # Random perturbation
        rb = random.uniform(-0.1, 0.1)
        perturbation = math.exp(rb)

        return w_base * perturbation


def get_strategy(strategy_name: str) -> InertiaWeightStrategy:
    """
    Get inertia weight strategy by name.

    Args:
        strategy_name: "LDIW", "NDIW", "AIW", or "SIW"

    Returns:
        InertiaWeightStrategy instance
    """
    strategies = {
        "LDIW": LinearDecreasingInertiaWeight,
        "NDIW": NonlinearDecreasingInertiaWeight,
        "AIW": AdaptiveInertiaWeight,
        "SIW": StochasticInertiaWeight,
    }

    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    return strategies[strategy_name]()


__all__ = [
    "InertiaWeightStrategy",
    "LinearDecreasingInertiaWeight",
    "NonlinearDecreasingInertiaWeight",
    "AdaptiveInertiaWeight",
    "StochasticInertiaWeight",
    "get_strategy",
]
