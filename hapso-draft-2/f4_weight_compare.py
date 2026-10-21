import random
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pso_improvement import AIW, LDIW, NDIW, SIW

matplotlib.use("Agg")


def plot_inertia_weights(w_min=0.4, w_max=0.9, Tmax=250, pkgbest=1.0, pk1gbest=1.0):
    random.seed(42)
    t_max = Tmax
    formulas = {
        "LDIW": LDIW(w_min=w_min, w_max=w_max),
        "NDIW": NDIW(w_min=w_min, w_max=w_max),
        "AIW": AIW(w_min=w_min, w_max=w_max),
        "SIW": SIW(w_min=w_min, w_max=w_max),
    }
    k_values = np.arange(1, t_max + 1)
    (fig, ax) = plt.subplots(figsize=(8, 5), dpi=100)
    fig.patch.set_facecolor((1.0, 1.0, 1.0))
    ax.set_facecolor((1.0, 1.0, 1.0))
    for label, model in formulas.items():
        vals = [
            model.compute(k, t_max, pk_gbest=1.0 / (k + 2), pk1_gbest=1.0 / (k + 1))
            for k in k_values
        ]
        ax.plot(k_values, vals, label=label, linewidth=2.2)
    ax.set_title("Inertia Weight Compare", fontsize=13)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("w")
    ax.grid(alpha=0.2)
    ax.legend()
    return plt
