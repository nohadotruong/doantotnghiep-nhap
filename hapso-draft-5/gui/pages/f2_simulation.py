
from config.ui_config import (
    COLOR_BLACK,
    FONT_SIZE_DEFAULT,
)
from core.models import PathResult
from state.app_state import get_app_state
import pygame


class F2SimulationPage:

    def __init__(self) -> None:
        self.menu_items = [
            "1: A* algorithm",
            "2: PSO algorithm",
            "3: APSO algorithm",
            "4: HAPSO algorithm",
            "Space: Run",
            "C: Clear results",
        ]

    def draw(self, app) -> None:
        self.draw_menu(app)
        self.draw_info_panel(app)
        self.draw_metrics(app)

    def draw_menu(self, app) -> None:
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = app.content_left_rect.y + 10
        status_text = (
            f"Status: {app.f2_status if hasattr(app, 'f2_status') else 'Ready'}"
        )
        status_surface = font.render(status_text, True, COLOR_BLACK)
        status_rect = status_surface.get_rect(
            topleft=(app.content_left_rect.x + 10, status_y)
        )
        app.screen.blit(status_surface, status_rect)

        y_offset = status_y + 45
        for item in self.menu_items:
            text_surface = font.render(item, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(app.content_left_rect.x + 10, y_offset)
            )
            app.screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_info_panel(self, app) -> None:
        state = get_app_state()
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = app.content_left_rect.y + 10 + 45 + len(self.menu_items) * 30 + 20

        algorithm = getattr(app, "f2_algorithm", "None") or "None"
        info_lines = [
            f"Algorithm: {algorithm}",
        ]

        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(app.content_left_rect.x + 10, info_y + i * 30)
            )
            app.screen.blit(text_surface, text_rect)

    def draw_metrics(self, app) -> None:
        state = get_app_state()
        if not state.f2_results:
            return

        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        metrics_y = app.content_left_rect.y + app.content_left_rect.height - 150

        metrics_lines = ["=== Last Results ==="]
        for algo_name, result in state.f2_results.items():
            if isinstance(result, PathResult):
                line = f"{algo_name}: {result.execution_time:.4f}s"
                if result.success and result.path:
                    line += f" ({len(result.path)} waypoints)"
                else:
                    line += " (failed)"
                metrics_lines.append(line)

        for i, line in enumerate(metrics_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(app.content_left_rect.x + 10, metrics_y + i * 25)
            )
            app.screen.blit(text_surface, text_rect)
