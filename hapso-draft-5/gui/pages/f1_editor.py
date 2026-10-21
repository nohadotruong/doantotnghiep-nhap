
from config.ui_config import (
    COLOR_BLACK,
    F1_MENU_ITEMS,
    FONT_SIZE_DEFAULT,
    GRID_SIZE,
)
import pygame


class F1EditorPage:

    def __init__(self) -> None:
        self.menu_items = F1_MENU_ITEMS

    def draw(self, app) -> None:
        self.draw_menu(app)
        self.draw_info_panel(app)

    def draw_menu(self, app) -> None:
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = app.content_left_rect.y + 10
        status_text = f"Status: {app.editor_status}"
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
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = app.content_left_rect.y + 10 + 45 + len(self.menu_items) * 30 + 20

        # Use app's current grid_map for display
        total_cells = GRID_SIZE * GRID_SIZE
        obstacle_count = app.grid_map.get_obstacle_count()
        start = app.grid_map.start
        goal = app.grid_map.goal

        info_lines = [
            f"Start: {start if start else 'None'}",
            f"Goal: {goal if goal else 'None'}",
            f"Obstacles: {obstacle_count}/{total_cells}",
        ]

        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(app.content_left_rect.x + 10, info_y + i * 30)
            )
            app.screen.blit(text_surface, text_rect)
