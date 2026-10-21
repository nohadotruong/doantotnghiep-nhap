import math
import random
from typing import Tuple


def calculate_aiw(
    current_iteration: int,
    max_iterations: int,
    current_gbest: float,
    previous_gbest: float,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
) -> float:
    if previous_gbest == 0:
        fitness_ratio = 1.0
    else:
        fitness_ratio = current_gbest / previous_gbest

    base_omega = (omega_max + omega_min) * fitness_ratio - omega_max * (
        current_iteration / max_iterations
    )
    return max(omega_min, min(omega_max, base_omega))


def calculate_ndiw(
    current_iteration: int,
    max_iterations: int,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
) -> float:
    exponent = (max_iterations - current_iteration) / max_iterations
    omega = math.exp(-math.exp(exponent))
    scaled_omega = omega_min + (omega_max - omega_min) * omega
    return max(omega_min, min(omega_max, scaled_omega))


def calculate_ldiw(
    current_iteration: int,
    max_iterations: int,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
) -> float:
    omega = omega_max - (omega_max - omega_min) * (current_iteration / max_iterations)
    return max(omega_min, min(omega_max, omega))


def calculate_siw(
    current_iteration: int,
    max_iterations: int,
    omega_max: float = 0.9,
    omega_min: float = 0.4,
    rb_range: Tuple[float, float] = (-0.1, 0.1),
) -> float:
    rb = random.uniform(rb_range[0], rb_range[1])
    stochastic_factor = math.exp(rb)

    base_omega = omega_max - (omega_max - omega_min) * (
        current_iteration / max_iterations
    )
    omega = base_omega * stochastic_factor

    return max(omega_min, min(omega_max, omega))
