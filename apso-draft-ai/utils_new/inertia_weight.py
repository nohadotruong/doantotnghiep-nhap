from abc import ABC, abstractmethod
import math
import numpy as np


class InertiaWeight(ABC):
    def __init__(self, w_min: float = 0.4, w_max: float = 0.9) -> None:
        self.w_min = w_min
        self.w_max = w_max

    @abstractmethod
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        pass


class LDIW(InertiaWeight):
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        return self.w_max - (self.w_max - self.w_min) * (k / t_max)


class NDIW(InertiaWeight):
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        exponent = (t_max - k) / t_max
        return math.exp(-math.exp(exponent))


class AIW(InertiaWeight):
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        pk_gbest = kwargs.get("pk_gbest", 1.0)
        pk1_gbest = kwargs.get("pk1_gbest", 1.0)

        if pk1_gbest == 0:
            ratio = 1.0
        else:
            ratio = pk_gbest / pk1_gbest

        return (self.w_max + self.w_min) * ratio - self.w_max * (k / t_max)


class SIW(InertiaWeight):
    def compute(self, k: int, t_max: int, **kwargs) -> float:
        rb = np.random.uniform(-0.1, 0.1)
        return self.w_max - (self.w_max - self.w_min) * (k / t_max) * math.exp(rb)
