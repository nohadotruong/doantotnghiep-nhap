
from config.ui_config import (
    COLOR_BLACK,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_SMALL,
    GRID_CELL_SIZE,
    GRID_SIZE,
    MENU_ITEMS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gui.pages.f1_editor import F1EditorPage
from gui.pages.f2_simulation import F2SimulationPage
from gui.pages.f3_comparison import F3ComparisonPage
from state.app_state import get_app_state

import os
import pygame


class Renderer:

    def __init__(self):
        self.f1_page = F1EditorPage()
        self.f2_page = F2SimulationPage()
        self.f3_page = F3ComparisonPage()

    def draw_content_area(self, app):
        pygame.draw.rect(app.screen, COLOR_WHITE, app.content_left_rect)
        pygame.draw.rect(app.screen, COLOR_BLACK, app.vertical_separator_rect)
        pygame.draw.rect(app.screen, COLOR_WHITE, app.content_right_rect)

        if app.current_page == pygame.K_F1:
            self.f1_page.draw(app)
            self.draw_grid(app)
        elif app.current_page == pygame.K_F2:
            self.f2_page.draw(app)
            self.draw_grid(app)
        elif app.current_page == pygame.K_F3:
            self.f3_page.draw(app)
            self.draw_grid(app)
        else:
            font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
            text_right = font.render("Page Content", True, COLOR_BLACK)
            text_rect_right = text_right.get_rect(
                topleft=(app.content_right_rect.x + 10, app.content_right_rect.y + 10)
            )
            app.screen.blit(text_right, text_rect_right)

    def draw_grid(self, app):
        font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        axis_label_width = 50
        grid_x = app.content_right_rect.x + axis_label_width
        grid_y = app.content_right_rect.y + 10
        grid_width = GRID_SIZE * GRID_CELL_SIZE
        grid_height = GRID_SIZE * GRID_CELL_SIZE
        grid_area = pygame.Rect(grid_x, grid_y, grid_width, grid_height)
        app.grid_area = grid_area
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = grid_area.x + x * GRID_CELL_SIZE
                cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
                cell_value = app.grid_map.grid[y][x]
                if cell_value == app.grid_map.OBSTACLE:
                    pygame.draw.rect(app.screen, COLOR_BLACK, cell_rect)
                elif cell_value == app.grid_map.START:
                    pygame.draw.rect(app.screen, (0, 255, 0), cell_rect)
                elif cell_value == app.grid_map.GOAL:
                    pygame.draw.rect(app.screen, (255, 0, 0), cell_rect)
                else:
                    pygame.draw.rect(app.screen, COLOR_WHITE, cell_rect)
        for i in range(GRID_SIZE + 1):
            x = grid_area.x + i * GRID_CELL_SIZE
            pygame.draw.line(
                app.screen, COLOR_LIGHT_GRAY, (x, grid_area.y), (x, grid_area.bottom), 1
            )
            y = grid_area.y + i * GRID_CELL_SIZE
            pygame.draw.line(
                app.screen, COLOR_LIGHT_GRAY, (grid_area.x, y), (grid_area.right, y), 1
            )
        if (
            app.current_page == pygame.K_F2
            and app.f2_result
            and app.f2_result.get("path")
        ):
            path = app.f2_result["path"]
            if len(path) > 1:
                for i in range(len(path) - 1):
                    x1, y1 = path[i]
                    x2, y2 = path[i + 1]
                    px1 = grid_area.x + x1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    py1 = (
                        grid_area.y
                        + (GRID_SIZE - 1 - y1) * GRID_CELL_SIZE
                        + GRID_CELL_SIZE // 2
                    )
                    px2 = grid_area.x + x2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    py2 = (
                        grid_area.y
                        + (GRID_SIZE - 1 - y2) * GRID_CELL_SIZE
                        + GRID_CELL_SIZE // 2
                    )
                    pygame.draw.line(
                        app.screen, (100, 149, 237), (px1, py1), (px2, py2), 2
                    )

        if app.current_page == pygame.K_F2 and app.f2_all_results:
            colors = [
                (100, 149, 237),  # A* - Cornflower Blue
                (0, 200, 100),  # A* improved - Green
                (255, 140, 0),  # PSO - Orange
                (220, 20, 60),  # PSO improved - Crimson Red
                (138, 43, 226),  # APSO - Blue Violet
                (255, 215, 0),  # HAPSO - Gold
            ]
            for idx, result in enumerate(app.f2_all_results):
                if result.get("path") and len(result["path"]) > 1:
                    path = result["path"]
                    color = colors[idx % len(colors)]
                    for i in range(len(path) - 1):
                        x1, y1 = path[i]
                        x2, y2 = path[i + 1]
                        px1 = grid_area.x + x1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                        py1 = (
                            grid_area.y
                            + (GRID_SIZE - 1 - y1) * GRID_CELL_SIZE
                            + GRID_CELL_SIZE // 2
                        )
                        px2 = grid_area.x + x2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                        py2 = (
                            grid_area.y
                            + (GRID_SIZE - 1 - y2) * GRID_CELL_SIZE
                            + GRID_CELL_SIZE // 2
                        )
                        pygame.draw.line(app.screen, color, (px1, py1), (px2, py2), 2)
        if app.current_page == pygame.K_F3:
            if app.f3_result_cells:
                for x, y in app.f3_result_cells:
                    cell_x = grid_area.x + x * GRID_CELL_SIZE
                    cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                    cell_rect = pygame.Rect(
                        cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE
                    )
                    pygame.draw.rect(app.screen, (200, 220, 255), cell_rect)
                    pygame.draw.rect(app.screen, (0, 100, 200), cell_rect, 2)
            if app.f3_line_start:
                sx, sy = app.f3_line_start
                start_x = grid_area.x + sx * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                start_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - sy) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                pygame.draw.circle(app.screen, (0, 255, 0), (start_x, start_y), 8)
                pygame.draw.circle(app.screen, (0, 200, 0), (start_x, start_y), 8, 2)
            if app.f3_line_end:
                ex, ey = app.f3_line_end
                end_x = grid_area.x + ex * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                end_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - ey) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                pygame.draw.circle(app.screen, (255, 0, 0), (end_x, end_y), 8)
                pygame.draw.circle(app.screen, (200, 0, 0), (end_x, end_y), 8, 2)
            if app.f3_line_start and app.f3_line_end:
                sx, sy = app.f3_line_start
                ex, ey = app.f3_line_end
                start_x = grid_area.x + sx * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                start_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - sy) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                end_x = grid_area.x + ex * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                end_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - ey) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                pygame.draw.line(
                    app.screen, (150, 150, 150), (start_x, start_y), (end_x, end_y), 1
                )
        # Draw preview line when mouse is pressed
        if app.mouse_pressed and app.mouse_start_pos and app.mouse_current_pos and app.current_page == pygame.K_F1:
            preview_points = app.get_preview_line_points(app.mouse_start_pos, app.mouse_current_pos)
            mode = app.editor_status
            if mode == "Obstacle":
                preview_color = (100, 100, 100)
            elif mode == "Ecrase":
                preview_color = (200, 200, 200)
            elif mode == "Start":
                preview_color = (0, 150, 0)
            elif mode == "Goal":
                preview_color = (150, 0, 0)
            else:
                preview_color = None
            
            if preview_color:
                for x, y in preview_points:
                    cell_x = grid_area.x + x * GRID_CELL_SIZE
                    cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                    cell_rect = pygame.Rect(cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
                    pygame.draw.rect(app.screen, preview_color, cell_rect, 2)
        for i in range(GRID_SIZE):
            x = grid_area.x + i * GRID_CELL_SIZE + GRID_CELL_SIZE / 2
            y = grid_area.bottom + 15
            label = font_small.render(str(i), True, COLOR_BLACK)
            label_rect = label.get_rect(center=(x, y))
            app.screen.blit(label, label_rect)
        for i in range(GRID_SIZE):
            y = grid_area.y + (GRID_SIZE - 1 - i) * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            x = grid_area.x - 35
            label = font_small.render(str(i), True, COLOR_BLACK)
            label_rect = label.get_rect(center=(x, y))
            app.screen.blit(label, label_rect)

    def draw_load_map_ui(self, app):
        font_title = pygame.font.Font(None, int(FONT_SIZE_DEFAULT * 1.5))
        font_normal = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLOR_WHITE)
        app.screen.blit(overlay, (0, 0))
        title = font_title.render("SELECT MAP TO LOAD", True, COLOR_BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        app.screen.blit(title, title_rect)
        start_idx = app.map_page * app.maps_per_page
        end_idx = min(start_idx + app.maps_per_page, len(app.map_list))
        map_y = 120
        for i in range(start_idx, end_idx):
            map_dir = app.map_list[i]
            map_name = os.path.basename(map_dir)
            is_selected = i == app.map_selected_index
            text_color = (255, 0, 0) if is_selected else COLOR_BLACK
            prefix = "> " if is_selected else "  "
            map_text = font_normal.render(f"{prefix}{map_name}", True, text_color)
            map_rect = map_text.get_rect(topleft=(100, map_y))
            app.screen.blit(map_text, map_rect)
            map_y += 50
        instructions_y = WINDOW_HEIGHT - 100
        instructions = [
            "UP/DOWN: Navigate   ENTER: Load   Q: Cancel",
            f"Page {app.map_page + 1} / {(len(app.map_list) + app.maps_per_page - 1) // app.maps_per_page}",
        ]
        for i, instruction in enumerate(instructions):
            instr_text = font_normal.render(instruction, True, COLOR_BLACK)
            instr_rect = instr_text.get_rect(
                center=(WINDOW_WIDTH // 2, instructions_y + i * 30)
            )
            app.screen.blit(instr_text, instr_rect)

    def draw_navigation_bar(self, app):
        pygame.draw.rect(app.screen, COLOR_WHITE, app.nav_rect)
        menu_options = list(MENU_ITEMS.values()) + ["ESC: Exit"]
        menu_text = "  |  ".join(menu_options)
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        text_surface = font.render(menu_text, True, COLOR_BLACK)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, app.nav_rect.centery)
        )
        app.screen.blit(text_surface, text_rect)

    def draw_separator(self, app):
        pygame.draw.rect(app.screen, COLOR_BLACK, app.separator_rect)

    def render(self, app):
        app.screen.fill(COLOR_WHITE)
        if app.load_map_mode:
            self.draw_load_map_ui(app)
        else:
            self.draw_navigation_bar(app)
            self.draw_separator(app)
            self.draw_content_area(app)
        pygame.display.flip()
