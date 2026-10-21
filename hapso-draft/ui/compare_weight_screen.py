from __future__ import annotations

from io import BytesIO

import matplotlib
import numpy as np
import pygame

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from planners.inertia_weight import AIW, LDIW, NDIW, SIW
from ui.common import FONT_NORMAL, FONT_SMALL, PALETTE, Button, TextInput, draw_title


class CompareWeightScreen:
    def __init__(self, app: object) -> None:
        self.app = app
        self.chart_surface: pygame.Surface | None = None
        self.status = "Press R to generate omega chart"
        self.buttons = [Button(pygame.Rect(24, 117, 294, 32), "Recompute Weights", "R")]
        self.inputs = [
            TextInput(pygame.Rect(24, 172, 294, 30), "Iterations", "80"),
            TextInput(pygame.Rect(24, 225, 294, 30), "w_min", "0.4"),
            TextInput(pygame.Rect(24, 278, 294, 30), "w_max", "0.9"),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        for field in self.inputs:
            field.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self._build_chart()

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE["bg"])
        content_top = 40

        # 3-7 ratio layout
        left_panel_width = int(self.app.window_width * 0.3)
        right_panel_x = left_panel_width
        right_panel_width = self.app.window_width - left_panel_width
        content_bottom = self.app.window_height

        # Draw left panel background
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

        # Draw title in left panel
        draw_title(surface, "Weight Compare", "Compare 4 inertia formulas")

        # Draw controls in left panel
        font = pygame.font.Font(None, FONT_NORMAL)
        for b in self.buttons:
            b.draw(surface, font)
        for field in self.inputs:
            field.draw(surface, pygame.font.Font(None, FONT_SMALL))

        # Draw status in left panel
        status = pygame.font.Font(None, FONT_SMALL).render(
            self.status, True, PALETTE["muted"]
        )
        surface.blit(status, (21, 313))

        # Draw chart in right panel (centered)
        if self.chart_surface:
            chart_width = self.chart_surface.get_width()
            chart_height = self.chart_surface.get_height()
            chart_x = right_panel_x + 5 + ((right_panel_width - 10) - chart_width) // 2
            chart_y = 60 + (content_bottom - 60 - chart_height) // 2
            surface.blit(self.chart_surface, (chart_x, chart_y))

    def _build_chart(self) -> None:
        t_max = max(5, self.inputs[0].get_int(80))
        w_min = self.inputs[1].get_float(0.4)
        w_max = self.inputs[2].get_float(0.9)

        formulas = {
            "LDIW": LDIW(w_min=w_min, w_max=w_max),
            "NDIW": NDIW(w_min=w_min, w_max=w_max),
            "AIW": AIW(w_min=w_min, w_max=w_max),
            "SIW": SIW(w_min=w_min, w_max=w_max),
        }
        k_values = np.arange(1, t_max + 1)

        fig, ax = plt.subplots(figsize=(5.3, 4.9), dpi=100)
        fig.patch.set_facecolor((1.0, 1.0, 1.0))
        ax.set_facecolor((1.0, 1.0, 1.0))

        for label, model in formulas.items():
            vals = [
                model.compute(k, t_max, pk_gbest=1.0 / (k + 2), pk1_gbest=1.0 / (k + 1))
                for k in k_values
            ]
            ax.plot(k_values, vals, label=label, linewidth=2.2)

        ax.set_title("Inertia Weight Schedules", fontsize=13)
        ax.set_xlabel("Iteration")
        ax.set_ylabel("w")
        ax.grid(alpha=0.2)
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        self.chart_surface = pygame.image.load(buf).convert_alpha()
        self.status = "Chart updated with custom parameters"
