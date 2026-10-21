import importlib.util
import os
from pathlib import Path
import random

import matplotlib.pyplot as plt


def load_inertia_weight_functions():
    module_path = (
        Path(__file__).resolve().parent / "core" / "utils" / "inertia_weight.py"
    )
    spec = importlib.util.spec_from_file_location("inertia_weight", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module.aiw, module.ldiw, module.ndiw, module.siw


def compute_weights(t_max: int, w_min: float, w_max: float):
    aiw, ldiw, ndiw, siw = load_inertia_weight_functions()

    ks = list(range(0, t_max + 1))
    w_aiw = [aiw(k, t_max, w_min=w_min, w_max=w_max) for k in ks]
    w_ldiw = [ldiw(k, t_max, w_min=w_min, w_max=w_max) for k in ks]
    w_ndiw = [ndiw(k, t_max) for k in ks]

    random.seed(0)
    w_siw = [siw(k, t_max, w_min=w_min, w_max=w_max) for k in ks]

    return ks, w_aiw, w_ldiw, w_ndiw, w_siw


def plot_weights(ks, *weights, labels=None, out_path=None):
    plt.figure(figsize=(6, 6))
    for w, label in zip(weights, labels):
        plt.plot(ks, w, label=label)
    plt.xlabel("Vòng lặp (k)")
    plt.ylabel("Trọng số quán tính (w)")
    plt.legend()
    plt.grid(alpha=0.3)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=200)
    plt.show()


def main():
    t_max = 200
    w_min = 0.4
    w_max = 0.9
    ks, w_aiw, w_ldiw, w_ndiw, w_siw = compute_weights(t_max, w_min, w_max)
    out_path = os.path.join("data/results", "weights_compare.png")
    plot_weights(
        ks,
        w_aiw,
        w_ldiw,
        w_ndiw,
        w_siw,
        labels=["AIW", "LDIW", "NDIW", "SIW"],
        out_path=out_path,
    )


if __name__ == "__main__":
    main()
