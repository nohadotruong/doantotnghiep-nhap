from __future__ import annotations

from io import BytesIO

import matplotlib
import numpy as np
import pygame

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app_io.experiment_runner import run_experiments
from ui.common import FONT_NORMAL, FONT_SMALL, PALETTE, Button, draw_title


class CompareResultScreen:
    def __init__(self, app: object) -> None:
        self.app = app
        self.chart_surface: pygame.Surface | None = None
        self.status = "Press R to run algorithm benchmark"
        self.buttons = [Button(pygame.Rect(24, 117, 294, 32), "Run Benchmark", "R")]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self._run_and_draw()

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE["bg"])
        content_top = 40
        left_panel_width = int(self.app.window_width * 0.3)
        right_panel_x = left_panel_width
        right_panel_width = self.app.window_width - left_panel_width
        content_bottom = self.app.window_height

        pygame.draw.rect(
            surface,
            PALETTE["panel"],
            pygame.Rect(0, content_top, left_panel_width, content_bottom - content_top),
        )

        # Draw borders: left (border-right), right (border-left)
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (left_panel_width, content_top),
            (left_panel_width, content_bottom),
            2,
        )
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (right_panel_x, content_top),
            (right_panel_x, content_bottom),
            2,
        )

        draw_title(surface, "Result Compare", "Benchmark A* / PSO / APSO / HAPSO")

        font = pygame.font.Font(None, FONT_NORMAL)
        for b in self.buttons:
            b.draw(surface, font)

        info_lines = [
            self.status,
            "Charts:",
            "1. Length",
            "2. Node count",
            "3. Total rotation",
            "4. Objective",
            "5. Aggregate score",
        ]
        for idx, line in enumerate(info_lines):
            line_surface = pygame.font.Font(None, FONT_SMALL).render(
                line, True, PALETTE["muted"]
            )
            surface.blit(line_surface, (21, 154 + idx * 24))

        if self.chart_surface:
            chart_width = self.chart_surface.get_width()
            chart_height = self.chart_surface.get_height()
            chart_x = right_panel_x + 5 + ((right_panel_width - 10) - chart_width) // 2
            chart_y = 60 + (content_bottom - 60 - chart_height) // 2
            surface.blit(self.chart_surface, (chart_x, chart_y))

    def _run_and_draw(self) -> None:
        if self.app.start is None or self.app.goal is None:
            self.status = "Please set start and goal in Map Editor"
            return

        results = run_experiments(self.app.grid, self.app.start, self.app.goal)
        labels = [r.name for r in results]
        lengths = np.array([r.length for r in results], dtype=float)
        nodes = np.array([r.nodes for r in results], dtype=float)
        rotations = np.array([r.smoothness for r in results], dtype=float)
        objectives = np.array([r.objective_value for r in results], dtype=float)

        def sanitize(values: np.ndarray) -> np.ndarray:
            finite = values[np.isfinite(values)]
            if finite.size == 0:
                return np.ones_like(values) * 1e6
            cap = float(np.max(finite) * 1.15 + 1.0)
            return np.where(np.isfinite(values), values, cap)

        lengths = sanitize(lengths)
        nodes = sanitize(nodes)
        rotations = sanitize(rotations)
        objectives = sanitize(objectives)

        def normalize(values: np.ndarray) -> np.ndarray:
            v_min = float(np.min(values))
            v_max = float(np.max(values))
            if abs(v_max - v_min) < 1e-9:
                return np.zeros_like(values)
            return (values - v_min) / (v_max - v_min)

        aggregate = 0.25 * (
            normalize(lengths)
            + normalize(nodes)
            + normalize(rotations)
            + normalize(objectives)
        )

        fig, axes = plt.subplots(3, 2, figsize=(7.5, 6.5), dpi=100)
        fig.patch.set_facecolor((1.0, 1.0, 1.0))
        chart_data = [
            ("Length", lengths),
            ("Nodes", nodes),
            ("Total rotation", rotations),
            ("Objective", objectives),
            ("Aggregate", aggregate),
        ]

        for ax, (title, values) in zip(axes.flatten(), chart_data):
            ax.set_facecolor((1.0, 1.0, 1.0))
            bars = ax.bar(
                labels, values, color=["#2E86AB", "#E07A5F", "#3D9970", "#6C5B7B"]
            )
            ax.set_title(title, fontsize=9)
            ax.tick_params(axis="x", labelrotation=0, labelsize=7)
            ax.tick_params(axis="y", labelsize=7)
            ax.grid(axis="y", alpha=0.2)
            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{value:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=6,
                )

        axes.flatten()[-1].axis("off")
        plt.tight_layout(pad=1.0)

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        self.chart_surface = pygame.image.load(buf).convert_alpha()
        self.status = "Benchmark complete"
