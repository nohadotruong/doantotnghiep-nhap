from abc import ABC, abstractmethod
import math
import random

class InertiaWeight(ABC):

    def __init__(self, w_min: float=0.4, w_max: float=0.9) -> None:
        self.w_min = w_min
        self.w_max = w_max

    @abstractmethod
    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        pass

class LDIW(InertiaWeight):

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        if t_max == 0:
            return self.w_min
        return self.w_max - (self.w_max - self.w_min) * (k / t_max)

class NDIW(InertiaWeight):

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        if t_max == 0:
            return math.exp(-math.exp(1.0))
        inner = (t_max - k) / t_max
        return math.exp(-math.exp(inner))

class AIW(InertiaWeight):

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        pk_gbest = kwargs.get('pk_gbest', 1.0)
        pk1_gbest = kwargs.get('pk1_gbest', pk_gbest)
        if pk1_gbest != 0:
            fitness_ratio = pk_gbest / pk1_gbest
        else:
            fitness_ratio = 1.0
        return (self.w_max + self.w_min) * fitness_ratio - self.w_max * (k / max(1, t_max))

class SIW(InertiaWeight):

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        if t_max == 0:
            return self.w_min
        rb = random.uniform(-0.1, 0.1)
        perturbation = math.exp(rb)
        return self.w_max - (self.w_max - self.w_min) * (k / t_max) * perturbation

class SOBL:

    def __init__(self, mu: float=0.5, sigma: float=0.15) -> None:
        self.mu = mu
        self.sigma = sigma

    def opposite_scalar(self, x: float, lb: float, ub: float) -> float:
        r = self._sample_r()
        x_tilde = lb + ub - x * r
        return max(lb, min(ub, x_tilde))

    def opposite_vector(self, x_vec, bounds):
        return [self.opposite_scalar(float(x_vec[i]), float(bounds[i][0]), float(bounds[i][1])) for i in range(len(x_vec))]

    def _sample_r(self) -> float:
        r = random.gauss(self.mu, self.sigma)
        return max(1e-06, min(1.0 - 1e-06, r))
