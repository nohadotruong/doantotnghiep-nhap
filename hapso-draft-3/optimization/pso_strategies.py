import math
import random


class InertiaWeight:
    @staticmethod
    def aiw(
        k: int,
        t_max: int,
        pk_gbest: float,
        pk1_gbest: float,
        w_min: float = 0.4,
        w_max: float = 0.9,
    ) -> float:
        if pk1_gbest != 0:
            fitness_ratio = pk_gbest / pk1_gbest
        else:
            fitness_ratio = 1.0

        return (w_max + w_min) * fitness_ratio - w_max * (k / max(1, t_max))

    @staticmethod
    def ldiw(k: int, t_max: int, w_min: float = 0.4, w_max: float = 0.9) -> float:
        if t_max == 0:
            return w_min

        return w_max - (w_max - w_min) * (k / t_max)

    @staticmethod
    def ndiw(k: int, t_max: int) -> float:
        if t_max == 0:
            return math.exp(-math.exp(1.0))

        inner = (t_max - k) / t_max
        return math.exp(-math.exp(inner))

    @staticmethod
    def siw(k: int, t_max: int, w_min: float = 0.4, w_max: float = 0.9) -> float:
        if t_max == 0:
            return w_min

        rb = random.uniform(-0.1, 0.1)
        noise = math.exp(rb)

        return (w_max - (w_max - w_min) * (k / t_max)) * noise


class SOBL:
    def __init__(self, mu: float = 0.5, sigma: float = 0.15) -> None:
        self.mu = mu
        self.sigma = sigma

    def opposite_scalar(self, x: float, lb: float, ub: float) -> float:
        random_value = self._sample_r()
        x_tilde = lb + ub - x * random_value
        return max(lb, min(ub, x_tilde))

    def opposite_vector(self, x_vec: tuple, bounds: list) -> list:
        return [
            self.opposite_scalar(
                float(x_vec[i]), float(bounds[i][0]), float(bounds[i][1])
            )
            for i in range(len(x_vec))
        ]

    def _sample_r(self) -> float:
        gaussian_sample = random.gauss(self.mu, self.sigma)
        return max(1e-06, min(1.0 - 1e-06, gaussian_sample))
