
from config.ui_config import (
    COLOR_BLACK,
    FONT_SIZE_DEFAULT,
)
from core.models import ComparisonMetrics, PathResult
from state.app_state import get_app_state
import pygame


class F3ComparisonPage:

    def __init__(self) -> None:
        self.menu_items = [
            "Space: Run comparison",
            "C: Clear results",
            "E: Export comparison",
        ]

    def draw(self, app) -> None:
        self.draw_menu(app)
        self.draw_comparison_results(app)
        self.draw_chart(app)

    def draw_menu(self, app) -> None:
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = app.content_left_rect.y + 10
        status_text = f"Status: {getattr(app, 'f3_status', 'Ready')}"
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

    def draw_comparison_results(self, app) -> None:
        state = get_app_state()
        if not state.f3_comparison_results:
            return

        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        results_y = app.content_left_rect.y + 10 + 45 + len(self.menu_items) * 30 + 20

        comparison = state.f3_comparison_results
        results_lines = ["=== Comparison Results ==="]

        # Header
        results_lines.append("Algorithm | Time (s) | Path Len | Status")
        results_lines.append("-" * 50)

        # Algorithm results
        for algo_name in comparison.get_algorithms():
            result = comparison.get_result(algo_name)
            if result:
                time_str = f"{result.execution_time:.4f}"
                path_len = len(result.path) if result.path else 0
                status = "✓" if result.success else "✗"
                line = f"{algo_name:10} | {time_str:8} | {path_len:8} | {status}"
                results_lines.append(line)

        # Draw results
        for i, line in enumerate(results_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(app.content_left_rect.x + 10, results_y + i * 25)
            )
            app.screen.blit(text_surface, text_rect)

    def draw_chart(self, app) -> None:
        state = get_app_state()
        if not state.f3_comparison_results:
            font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
            placeholder = font.render("Run comparison (Space)", True, COLOR_BLACK)
            placeholder_rect = placeholder.get_rect(
                center=(app.content_right_rect.centerx, app.content_right_rect.centery)
            )
            app.screen.blit(placeholder, placeholder_rect)
            return

        # Draw chart surface if available
        chart_surface = getattr(app, "f3_chart_surface", None)
        if not chart_surface:
            return

        # Scale chart to fit panel
        max_w = app.content_right_rect.width - 24
        max_h = app.content_right_rect.height - 24
        src_w = chart_surface.get_width()
        src_h = chart_surface.get_height()
        scale = min(max_w / src_w, max_h / src_h)
        dst_w = max(1, int(src_w * scale))
        dst_h = max(1, int(src_h * scale))

        scaled_chart = pygame.transform.smoothscale(chart_surface, (dst_w, dst_h))
        chart_x = app.content_right_rect.x + (app.content_right_rect.width - dst_w) // 2
        chart_y = (
            app.content_right_rect.y + (app.content_right_rect.height - dst_h) // 2
        )
        app.screen.blit(scaled_chart, (chart_x, chart_y))
