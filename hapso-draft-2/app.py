from datetime import datetime
from io import BytesIO
import json
import os
import sys
import time
import pygame
import matplotlib
import matplotlib.pyplot as plt
from apso import APSO
from astar import AStar
from config import (
    CENTER_WINDOW,
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    CONTENT_LEFT_RATIO,
    CONTENT_RIGHT_RATIO,
    F1_MENU_ITEMS,
    F2_MENU_ITEMS,
    F5_MENU_ITEMS,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_SMALL,
    FPS,
    FULLSCREEN,
    GRID_CELL_SIZE,
    GRID_SIZE,
    MAP_DIR,
    MENU_ITEMS,
    NAV_HEIGHT,
    RESULTS_DIR,
    SEPARATOR_HEIGHT,
    VERTICAL_SEPARATOR_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from get_line_grid import (
    get_line_grid_bresenham,
    get_line_grid_incremental_traversal,
    get_line_grid_parametric_discretization,
    get_line_grid_runs_of_runs,
)
from grid_map import GridMap
from hapso import HAPSO
from metrics import PathMetrics
from pso import PSOPlanner

matplotlib.use("Agg")


class App:

    def __init__(self):
        pygame.init()
        if CENTER_WINDOW and (not FULLSCREEN):
            info = pygame.display.Info()
            screen_width = info.current_w
            screen_height = info.current_h
            x = (screen_width - WINDOW_WIDTH) // 2
            y = (screen_height - WINDOW_HEIGHT) // 2
            os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_page = pygame.K_F1
        self.selected_item = 0
        self.editor_status = F1_MENU_ITEMS[0].split(": ", 1)[1]
        self.grid_map = GridMap(GRID_SIZE, GRID_SIZE)
        self.mouse_pressed = False
        self.mouse_start_pos = None
        self.mouse_current_pos = None
        self.grid_area = None
        self.load_map_mode = False
        self.map_list = []
        self.map_selected_index = 0
        self.maps_per_page = 5
        self.map_page = 0
        self.f2_algorithm = None
        self.f2_remove_redundant = False
        self.f2_remove_trans_redundant = False
        self.f2_avoid_corner_cutting = False
        self.f2_use_siw = False
        self.f2_use_sobl = False
        self.f2_running = False
        self.f2_result = None
        self.f3_algorithm = None
        self.f3_line_start = None
        self.f3_line_end = None
        self.f3_result_cells = []
        self.f3_drawing_line = False
        self.f5_status = "Ready"
        self.f5_results = {}
        self.f5_chart_surface = None
        self._calculate_layout()
        self._init_f4_state()

    def draw_content_area(self):
        pygame.draw.rect(self.screen, COLOR_WHITE, self.content_left_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.vertical_separator_rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, self.content_right_rect)
        if self.current_page == pygame.K_F1:
            self.draw_f1_menu()
            self.draw_info_panel()
            self.draw_grid()
        elif self.current_page == pygame.K_F2:
            self.draw_f2_menu()
            self.draw_f2_info_panel()
            self.draw_grid()
            self.draw_f2_metrics()
        elif self.current_page == pygame.K_F3:
            self.draw_f3_menu()
            self.draw_f3_info_panel()
            self.draw_grid()
        elif self.current_page == pygame.K_F4:
            self.draw_f4_panel()
        elif self.current_page == pygame.K_F5:
            self.draw_f5_menu()
            self.draw_f5_info_panel()
            self.draw_f5_compare_panel()
        else:
            font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
            text_right = font.render("Page Content", True, COLOR_BLACK)
            text_rect_right = text_right.get_rect(
                topleft=(self.content_right_rect.x + 10, self.content_right_rect.y + 10)
            )
            self.screen.blit(text_right, text_rect_right)

    def draw_f1_menu(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = self.content_left_rect.y + 10
        truncated_status = self._truncate_status(self.editor_status, 30)
        status_text = f"Status: {truncated_status}"
        status_surface = font.render(status_text, True, COLOR_BLACK)
        status_rect = status_surface.get_rect(
            topleft=(self.content_left_rect.x + 10, status_y)
        )
        self.screen.blit(status_surface, status_rect)
        y_offset = status_y + 45
        for i, item in enumerate(F1_MENU_ITEMS):
            text_surface = font.render(item, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, y_offset)
            )
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_f2_info_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = self.content_left_rect.y + 10 + 45 + len(F2_MENU_ITEMS) * 30 + 20
        algo_text = self.f2_algorithm if self.f2_algorithm else "None"
        redundant_text = "ON" if self.f2_remove_redundant else "OFF"
        trans_text = "ON" if self.f2_remove_trans_redundant else "OFF"
        corner_text = "ON" if self.f2_avoid_corner_cutting else "OFF"
        siw_text = "ON" if self.f2_use_siw else "OFF"
        sobl_text = "ON" if self.f2_use_sobl else "OFF"
        info_lines = [
            f"Algorithm: {algo_text}",
            f"Red.redundant (A*): {redundant_text}",
            f"Trans.redund. (A*): {trans_text}",
            f"Corner cut (A*): {corner_text}",
            f"SIW (PSO): {siw_text}",
            f"SOBL (PSO): {sobl_text}",
        ]
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, info_y + i * 30)
            )
            self.screen.blit(text_surface, text_rect)

    def draw_f2_menu(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = self.content_left_rect.y + 10
        truncated_status = self._truncate_status(self.editor_status, 30)
        status_text = f"Status: {truncated_status}"
        status_surface = font.render(status_text, True, COLOR_BLACK)
        status_rect = status_surface.get_rect(
            topleft=(self.content_left_rect.x + 10, status_y)
        )
        self.screen.blit(status_surface, status_rect)
        y_offset = status_y + 45
        for i, item in enumerate(F2_MENU_ITEMS):
            text_surface = font.render(item, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, y_offset)
            )
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_f2_metrics(self):
        if not self.f2_result or not self.f2_result.get("metrics"):
            return
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        metrics = self.f2_result["metrics"]
        grid_area = self.grid_area
        if not grid_area:
            return
        metrics_x = grid_area.right + 20
        metrics_y = grid_area.y
        metrics_lines = [
            f"Path Length: {metrics['min_d']:.2f}",
            f"Waypoints: {metrics['min_p']}",
            f"Turning: {metrics['min_i']:.4f}",
            f"Exec: {metrics['min_c']:.4f}s",
            f"Total: {metrics['min_t']:.4f}",
        ]
        for i, line in enumerate(metrics_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(topleft=(metrics_x, metrics_y + i * 30))
            self.screen.blit(text_surface, text_rect)

    def draw_f3_info_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = self.content_left_rect.y + 10 + 45 + 5 * 30 + 20
        algo_text = self.f3_algorithm if self.f3_algorithm else "None"
        start_text = f"{self.grid_map.start}" if self.grid_map.start else "None"
        end_text = f"{self.grid_map.goal}" if self.grid_map.goal else "None"
        info_lines = [
            f"Algorithm: {algo_text}",
            f"Start (F1): {start_text}",
            f"End (F1): {end_text}",
        ]
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, info_y + i * 28)
            )
            self.screen.blit(text_surface, text_rect)
        if self.f3_result_cells:
            cells_label_y = info_y + len(info_lines) * 28 + 10
            cells_label = font.render(
                f"Cells ({len(self.f3_result_cells)}):", True, COLOR_BLACK
            )
            self.screen.blit(
                cells_label, (self.content_left_rect.x + 10, cells_label_y)
            )
            cells_start_y = cells_label_y + 28
            cells_per_line = 5
            cell_list_height = self.content_left_rect.height - (
                cells_start_y - self.content_left_rect.y
            )
            lines = [
                ", ".join(
                    (
                        f"({x},{y})"
                        for (x, y) in self.f3_result_cells[i : i + cells_per_line]
                    )
                )
                for i in range(0, len(self.f3_result_cells), cells_per_line)
            ]
            for idx, line in enumerate(lines):
                if idx * 30 >= cell_list_height:
                    break
                cell_y = cells_start_y + idx * 28
                cell_surface = font.render(line, True, COLOR_DARK_GRAY)
                self.screen.blit(cell_surface, (self.content_left_rect.x + 10, cell_y))

    def draw_f3_menu(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = self.content_left_rect.y + 10
        truncated_status = self._truncate_status(self.editor_status, 30)
        status_text = f"Status: {truncated_status}"
        status_surface = font.render(status_text, True, COLOR_BLACK)
        status_rect = status_surface.get_rect(
            topleft=(self.content_left_rect.x + 10, status_y)
        )
        self.screen.blit(status_surface, status_rect)
        f3_menu_items = [
            "B: Bresenham",
            "V: Incremental",
            "D: Runs of Runs",
            "S: Supercover",
            "Space: Run",
        ]
        y_offset = status_y + 45
        for item in f3_menu_items:
            text_surface = font.render(item, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, y_offset)
            )
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_f4_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        pygame.font.Font(None, FONT_SIZE_SMALL)
        left_x = self.content_left_rect.x + 20
        left_y = self.content_left_rect.y + 40
        label_gap = 60
        (box_w, box_h) = (120, 36)
        color_inactive = (180, 180, 180)
        color_active = (100, 180, 255)
        label_spacing = 3
        label_test = font.render("w_min (wmin): [I]", True, COLOR_BLACK)
        label_height = label_test.get_height()
        label1 = font.render("w_min (wmin): [I]", True, COLOR_BLACK)
        self.screen.blit(label1, (left_x, left_y))
        box1_y = left_y + label_height + label_spacing
        box1_rect = pygame.Rect(left_x, box1_y, box_w, box_h)
        pygame.draw.rect(
            self.screen,
            color_active if self.f4_input_active == "w_min" else color_inactive,
            box1_rect,
            2,
        )
        val1_text = (
            self.f4_input_string
            if self.f4_input_active == "w_min"
            else f"{self.f4_w_min:.3f}"
        )
        val1 = font.render(val1_text, True, COLOR_BLACK)
        self.screen.blit(val1, (box1_rect.x + 10, box1_rect.y + 4))
        label2 = font.render("w_max (wmax): [A]", True, COLOR_BLACK)
        self.screen.blit(label2, (left_x, left_y + label_gap))
        box2_y = left_y + label_gap + label_height + label_spacing
        box2_rect = pygame.Rect(left_x, box2_y, box_w, box_h)
        pygame.draw.rect(
            self.screen,
            color_active if self.f4_input_active == "w_max" else color_inactive,
            box2_rect,
            2,
        )
        val2_text = (
            self.f4_input_string
            if self.f4_input_active == "w_max"
            else f"{self.f4_w_max:.3f}"
        )
        val2 = font.render(val2_text, True, COLOR_BLACK)
        self.screen.blit(val2, (box2_rect.x + 10, box2_rect.y + 4))
        label3 = font.render("Iteration (Tmax): [T]", True, COLOR_BLACK)
        self.screen.blit(label3, (left_x, left_y + label_gap * 2))
        box3_y = left_y + label_gap * 2 + label_height + label_spacing
        box3_rect = pygame.Rect(left_x, box3_y, box_w, box_h)
        pygame.draw.rect(
            self.screen,
            color_active if self.f4_input_active == "iteration" else color_inactive,
            box3_rect,
            2,
        )
        val3_text = (
            self.f4_input_string
            if self.f4_input_active == "iteration"
            else f"{self.f4_iteration}"
        )
        val3 = font.render(val3_text, True, COLOR_BLACK)
        self.screen.blit(val3, (box3_rect.x + 10, box3_rect.y + 4))
        hint_y = box3_y + box_h + 20
        hint_lines = [
            "SPACE: Run",
            "ENTER: Confirm input",
            "BACKSPACE: Delete char",
            "ESC: Cancel input",
        ]
        for i, hint_text in enumerate(hint_lines):
            hint = font.render(hint_text, True, COLOR_BLACK)
            self.screen.blit(hint, (left_x, hint_y + i * 25))
        if self.f4_chart_ready and self.f4_chart_surface:
            right_panel_width = self.content_right_rect.width
            chart_width = int(right_panel_width * 0.85)
            orig_rect = self.f4_chart_surface.get_rect()
            scale_factor = chart_width / orig_rect.width if orig_rect.width > 0 else 1
            new_width = int(orig_rect.width * scale_factor)
            new_height = int(orig_rect.height * scale_factor)
            scaled_chart = pygame.transform.scale(
                self.f4_chart_surface, (new_width, new_height)
            )
            chart_x = self.content_right_rect.x + (right_panel_width - new_width) // 2
            chart_y = (
                self.content_right_rect.y
                + (self.content_right_rect.height - new_height) // 2
            )
            self.screen.blit(scaled_chart, (chart_x, chart_y))
        elif not self.f4_chart_ready:
            placeholder = font.render(
                "Press SPACE to generate chart", True, COLOR_BLACK
            )
            placeholder_rect = placeholder.get_rect(
                center=(
                    self.content_right_rect.centerx,
                    self.content_right_rect.centery,
                )
            )
            self.screen.blit(placeholder, placeholder_rect)

    def draw_f5_menu(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = self.content_left_rect.y + 10
        status_text = f"Status: {self._truncate_status(self.f5_status, 28)}"
        status_surface = font.render(status_text, True, COLOR_BLACK)
        status_rect = status_surface.get_rect(
            topleft=(self.content_left_rect.x + 10, status_y)
        )
        self.screen.blit(status_surface, status_rect)
        y_offset = status_y + 45
        for item in F5_MENU_ITEMS:
            text_surface = font.render(item, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, y_offset)
            )
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_f5_info_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = self.content_left_rect.y + 10 + 45 + len(F5_MENU_ITEMS) * 30 + 20
        if not self.f5_results:
            info_lines = ["A*: N/A", "PSO: N/A", "APSO: N/A", "HAPSO: N/A"]
        else:
            info_lines = []
            for algo in ["A*", "PSO", "APSO", "HAPSO"]:
                result = self.f5_results.get(algo)
                if result and result.get("metrics"):
                    info_lines.append(f"{algo}: {result['execution_time']:.4f}s")
                else:
                    info_lines.append(f"{algo}: failed")
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, info_y + i * 28)
            )
            self.screen.blit(text_surface, text_rect)

    def draw_f5_compare_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        if not self.f5_chart_surface:
            placeholder = font.render(
                "Open F5 or press R to run compare", True, COLOR_BLACK
            )
            placeholder_rect = placeholder.get_rect(
                center=(
                    self.content_right_rect.centerx,
                    self.content_right_rect.centery,
                )
            )
            self.screen.blit(placeholder, placeholder_rect)
            return
        max_w = self.content_right_rect.width - 24
        max_h = self.content_right_rect.height - 24
        src_w = self.f5_chart_surface.get_width()
        src_h = self.f5_chart_surface.get_height()
        scale = min(max_w / src_w, max_h / src_h)
        dst_w = max(1, int(src_w * scale))
        dst_h = max(1, int(src_h * scale))
        chart_surface = pygame.transform.smoothscale(
            self.f5_chart_surface, (dst_w, dst_h)
        )
        chart_x = (
            self.content_right_rect.x + (self.content_right_rect.width - dst_w) // 2
        )
        chart_y = (
            self.content_right_rect.y + (self.content_right_rect.height - dst_h) // 2
        )
        self.screen.blit(chart_surface, (chart_x, chart_y))

    def draw_grid(self):
        font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        axis_label_width = 50
        grid_x = self.content_right_rect.x + axis_label_width
        grid_y = self.content_right_rect.y + 10
        grid_width = GRID_SIZE * GRID_CELL_SIZE
        grid_height = GRID_SIZE * GRID_CELL_SIZE
        grid_area = pygame.Rect(grid_x, grid_y, grid_width, grid_height)
        self.grid_area = grid_area
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = grid_area.x + x * GRID_CELL_SIZE
                cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
                cell_value = self.grid_map.grid[y][x]
                if cell_value == self.grid_map.OBSTACLE:
                    pygame.draw.rect(self.screen, COLOR_BLACK, cell_rect)
                elif cell_value == self.grid_map.START:
                    pygame.draw.rect(self.screen, (0, 255, 0), cell_rect)
                elif cell_value == self.grid_map.GOAL:
                    pygame.draw.rect(self.screen, (255, 0, 0), cell_rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_WHITE, cell_rect)
        for i in range(GRID_SIZE + 1):
            x = grid_area.x + i * GRID_CELL_SIZE
            pygame.draw.line(
                self.screen,
                COLOR_LIGHT_GRAY,
                (x, grid_area.y),
                (x, grid_area.bottom),
                1,
            )
            y = grid_area.y + i * GRID_CELL_SIZE
            pygame.draw.line(
                self.screen, COLOR_LIGHT_GRAY, (grid_area.x, y), (grid_area.right, y), 1
            )
        if (
            self.current_page == pygame.K_F2
            and self.f2_result
            and self.f2_result.get("path")
        ):
            path = self.f2_result["path"]
            if len(path) > 1:
                for i in range(len(path) - 1):
                    (x1, y1) = path[i]
                    (x2, y2) = path[i + 1]
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
                        self.screen, (100, 149, 237), (px1, py1), (px2, py2), 2
                    )
        if self.current_page == pygame.K_F3:
            if self.f3_result_cells:
                for x, y in self.f3_result_cells:
                    cell_x = grid_area.x + x * GRID_CELL_SIZE
                    cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                    cell_rect = pygame.Rect(
                        cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, (200, 220, 255), cell_rect)
                    pygame.draw.rect(self.screen, (0, 100, 200), cell_rect, 2)
            if self.f3_line_start:
                (sx, sy) = self.f3_line_start
                start_x = grid_area.x + sx * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                start_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - sy) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                pygame.draw.circle(self.screen, (0, 255, 0), (start_x, start_y), 8)
                pygame.draw.circle(self.screen, (0, 200, 0), (start_x, start_y), 8, 2)
            if self.f3_line_end:
                (ex, ey) = self.f3_line_end
                end_x = grid_area.x + ex * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                end_y = (
                    grid_area.y
                    + (GRID_SIZE - 1 - ey) * GRID_CELL_SIZE
                    + GRID_CELL_SIZE // 2
                )
                pygame.draw.circle(self.screen, (255, 0, 0), (end_x, end_y), 8)
                pygame.draw.circle(self.screen, (200, 0, 0), (end_x, end_y), 8, 2)
            if self.f3_line_start and self.f3_line_end:
                (sx, sy) = self.f3_line_start
                (ex, ey) = self.f3_line_end
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
                    self.screen, (150, 150, 150), (start_x, start_y), (end_x, end_y), 1
                )
        if self.mouse_pressed and self.mouse_start_pos and self.mouse_current_pos:
            self._draw_preview_line(
                grid_area, self.mouse_start_pos, self.mouse_current_pos
            )
        for i in range(GRID_SIZE):
            x = grid_area.x + i * GRID_CELL_SIZE + GRID_CELL_SIZE / 2
            y = grid_area.bottom + 15
            label = font_small.render(str(i), True, COLOR_BLACK)
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)
        for i in range(GRID_SIZE):
            y = grid_area.y + (GRID_SIZE - 1 - i) * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
            x = grid_area.x - 35
            label = font_small.render(str(i), True, COLOR_BLACK)
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)

    def draw_info_panel(self):
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        info_y = self.content_left_rect.y + 10 + 45 + len(F1_MENU_ITEMS) * 30 + 20
        total_cells = GRID_SIZE * GRID_SIZE
        obstacle_count = self.grid_map.get_obstacle_count()
        info_lines = [
            f"Start: {(self.grid_map.start if self.grid_map.start else 'None')}",
            f"Goal: {(self.grid_map.goal if self.grid_map.goal else 'None')}",
            f"Obstacles: {obstacle_count}/{total_cells}",
        ]
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, COLOR_BLACK)
            text_rect = text_surface.get_rect(
                topleft=(self.content_left_rect.x + 10, info_y + i * 30)
            )
            self.screen.blit(text_surface, text_rect)

    def draw_load_map_ui(self):
        font_title = pygame.font.Font(None, int(FONT_SIZE_DEFAULT * 1.5))
        font_normal = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLOR_WHITE)
        self.screen.blit(overlay, (0, 0))
        title = font_title.render("SELECT MAP TO LOAD", True, COLOR_BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        start_idx = self.map_page * self.maps_per_page
        end_idx = min(start_idx + self.maps_per_page, len(self.map_list))
        map_y = 120
        for i in range(start_idx, end_idx):
            map_dir = self.map_list[i]
            map_name = os.path.basename(map_dir)
            is_selected = i == self.map_selected_index
            text_color = (255, 0, 0) if is_selected else COLOR_BLACK
            prefix = "> " if is_selected else "  "
            map_text = font_normal.render(f"{prefix}{map_name}", True, text_color)
            map_rect = map_text.get_rect(topleft=(100, map_y))
            self.screen.blit(map_text, map_rect)
            map_y += 50
        instructions_y = WINDOW_HEIGHT - 100
        instructions = [
            "UP/DOWN: Navigate   ENTER: Load   Q: Cancel",
            f"Page {self.map_page + 1} / {(len(self.map_list) + self.maps_per_page - 1) // self.maps_per_page}",
        ]
        for i, instruction in enumerate(instructions):
            instr_text = font_normal.render(instruction, True, COLOR_BLACK)
            instr_rect = instr_text.get_rect(
                center=(WINDOW_WIDTH // 2, instructions_y + i * 30)
            )
            self.screen.blit(instr_text, instr_rect)

    def draw_navigation_bar(self):
        pygame.draw.rect(self.screen, COLOR_WHITE, self.nav_rect)
        menu_options = list(MENU_ITEMS.values()) + ["ESC: Exit"]
        menu_text = "  |  ".join(menu_options)
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        text_surface = font.render(menu_text, True, COLOR_BLACK)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, self.nav_rect.centery)
        )
        self.screen.blit(text_surface, text_rect)

    def draw_separator(self):
        pygame.draw.rect(self.screen, COLOR_BLACK, self.separator_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.load_map_mode:
                    if event.key == pygame.K_q:
                        self.load_map_mode = False
                    elif event.key == pygame.K_UP:
                        self.map_selected_index = max(0, self.map_selected_index - 1)
                        if self.map_selected_index < self.map_page * self.maps_per_page:
                            self.map_page = max(0, self.map_page - 1)
                    elif event.key == pygame.K_DOWN:
                        self.map_selected_index = min(
                            len(self.map_list) - 1, self.map_selected_index + 1
                        )
                        if (
                            self.map_selected_index
                            >= (self.map_page + 1) * self.maps_per_page
                        ):
                            self.map_page += 1
                    elif event.key == pygame.K_RETURN:
                        self._load_selected_map()
                        self.load_map_mode = False
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in MENU_ITEMS:
                    self.current_page = event.key
                    self.selected_item = 0
                    page_name = MENU_ITEMS[event.key]
                    print(f"\n{'=' * 60}")
                    print(f"SWITCHED TO: {page_name}")
                    print(f"{'=' * 60}")
                    if event.key == pygame.K_F1:
                        self.editor_status = "Obstacle"
                    elif event.key == pygame.K_F2:
                        self.editor_status = "Ready"
                    elif event.key == pygame.K_F5:
                        self._run_f5_compare()
                elif self.current_page == pygame.K_F1:
                    if event.key == pygame.K_1:
                        self.selected_item = 0
                        self.editor_status = "Obstacle"
                        print("[F1] Mode: Obstacle")
                    elif event.key == pygame.K_2:
                        self.selected_item = 1
                        self.editor_status = "Ecrease"
                        print("[F1] Mode: Ecrease")
                    elif event.key == pygame.K_s:
                        self.selected_item = 2
                        self.editor_status = "Start"
                        print("[F1] Mode: Set Start point")
                    elif event.key == pygame.K_g:
                        self.selected_item = 3
                        self.editor_status = "Goal"
                        print("[F1] Mode: Set Goal point")
                    elif event.key == pygame.K_RETURN:
                        self._save_map()
                    elif event.key == pygame.K_l:
                        self._open_load_map_ui()
                    elif event.key == pygame.K_c:
                        self.grid_map.clear_map()
                        self.editor_status = "Clear"
                        print("[F1] Grid cleared")
                elif self.current_page == pygame.K_F2:
                    if event.key == pygame.K_a:
                        self.f2_algorithm = "A*"
                        self.editor_status = "Algorithm: A*"
                        print("[F2] Algorithm selected: A*")
                    elif event.key == pygame.K_p:
                        self.f2_algorithm = "PSO"
                        self.editor_status = "Algorithm: PSO"
                        print("[F2] Algorithm selected: PSO")
                    elif event.key == pygame.K_s:
                        self.f2_algorithm = "APSO"
                        self.editor_status = "Algorithm: APSO"
                        print("[F2] Algorithm selected: APSO")
                    elif event.key == pygame.K_h:
                        self.f2_algorithm = "HAPSO"
                        self.editor_status = "Algorithm: HAPSO"
                        print("[F2] Algorithm selected: HAPSO")
                    elif event.key == pygame.K_1:
                        self.f2_remove_redundant = not self.f2_remove_redundant
                        status = "ON" if self.f2_remove_redundant else "OFF"
                        self.editor_status = f"Remove redundant: {status}"
                        print(f"[F2] Remove redundant: {status}")
                    elif event.key == pygame.K_2:
                        self.f2_remove_trans_redundant = (
                            not self.f2_remove_trans_redundant
                        )
                        status = "ON" if self.f2_remove_trans_redundant else "OFF"
                        self.editor_status = f"Remove trans. redund.: {status}"
                        print(f"[F2] Remove trans. redundant: {status}")
                    elif event.key == pygame.K_3:
                        self.f2_avoid_corner_cutting = not self.f2_avoid_corner_cutting
                        status = "ON" if self.f2_avoid_corner_cutting else "OFF"
                        self.editor_status = f"Avoid corner cut: {status}"
                        print(f"[F2] Avoid corner cutting: {status}")
                    elif event.key == pygame.K_4:
                        self.f2_use_siw = not self.f2_use_siw
                        status = "ON" if self.f2_use_siw else "OFF"
                        self.editor_status = f"SIW (PSO): {status}"
                        print(f"[F2] SIW enabled: {status}")
                    elif event.key == pygame.K_5:
                        self.f2_use_sobl = not self.f2_use_sobl
                        status = "ON" if self.f2_use_sobl else "OFF"
                        self.editor_status = f"SOBL (PSO): {status}"
                        print(f"[F2] SOBL enabled: {status}")
                    elif event.key == pygame.K_SPACE:
                        self._run_simulation()
                    elif event.key == pygame.K_RETURN:
                        self._save_result()
                elif self.current_page == pygame.K_F3:
                    if event.key == pygame.K_b:
                        self.f3_algorithm = "bresenham"
                        self.editor_status = "Algorithm: Bresenham"
                        print("[F3] Algorithm selected: Bresenham")
                    elif event.key == pygame.K_v:
                        self.f3_algorithm = "incremental"
                        self.editor_status = "Algorithm: Incremental"
                        print("[F3] Algorithm selected: Incremental Traversal")
                    elif event.key == pygame.K_d:
                        self.f3_algorithm = "runs"
                        self.editor_status = "Algorithm: Runs of Runs"
                        print("[F3] Algorithm selected: Runs of Runs")
                    elif event.key == pygame.K_s:
                        self.f3_algorithm = "parametric"
                        self.editor_status = "Algorithm: Parametric"
                        print("[F3] Algorithm selected: Parametric (Supercover)")
                    elif event.key == pygame.K_SPACE:
                        self._run_line_grid_algorithm()
                elif self.current_page == pygame.K_F4:
                    if event.key == pygame.K_SPACE:
                        self._update_f4_chart()
                    elif event.key == pygame.K_i:
                        self.f4_input_active = "w_min"
                        self.f4_input_string = ""
                        print("[F4] Input w_min: type value + ENTER")
                    elif event.key == pygame.K_a:
                        self.f4_input_active = "w_max"
                        self.f4_input_string = ""
                        print("[F4] Input w_max: type value + ENTER")
                    elif event.key == pygame.K_t:
                        self.f4_input_active = "iteration"
                        self.f4_input_string = ""
                        print("[F4] Input iteration: type value + ENTER")
                    elif event.key == pygame.K_RETURN:
                        if self.f4_input_active and self.f4_input_string:
                            try:
                                val = (
                                    float(self.f4_input_string)
                                    if "." in self.f4_input_string
                                    else int(self.f4_input_string)
                                )
                                if self.f4_input_active == "w_min":
                                    self.f4_w_min = max(
                                        0.0, min(self.f4_w_max, float(val))
                                    )
                                    print(f"[F4] w_min: {self.f4_w_min:.3f}")
                                elif self.f4_input_active == "w_max":
                                    self.f4_w_max = max(
                                        self.f4_w_min, min(1.0, float(val))
                                    )
                                    print(f"[F4] w_max: {self.f4_w_max:.3f}")
                                elif self.f4_input_active == "iteration":
                                    self.f4_iteration = max(10, min(500, int(val)))
                                    print(f"[F4] iteration: {self.f4_iteration}")
                                self.f4_input_string = ""
                                self.f4_input_active = None
                            except ValueError:
                                print("[F4]  Invalid number")
                                self.f4_input_string = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.f4_input_string = self.f4_input_string[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.f4_input_active = None
                        self.f4_input_string = ""
                    elif event.unicode.isdigit() or (
                        event.unicode == "." and "." not in self.f4_input_string
                    ):
                        if self.f4_input_active:
                            self.f4_input_string += event.unicode
                elif self.current_page == pygame.K_F5:
                    if event.key == pygame.K_r:
                        self._run_f5_compare()
            elif not self.load_map_mode and self.current_page == pygame.K_F1:
                self._handle_f1_mouse_event(event)
            elif self.current_page == pygame.K_F3:
                self._handle_f3_mouse_event(event)

    def render(self):
        self.screen.fill(COLOR_WHITE)
        if self.load_map_mode:
            self.draw_load_map_ui()
        else:
            self.draw_navigation_bar()
            self.draw_separator()
            self.draw_content_area()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def _bresenham_line(self, x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        (x, y) = (x0, y0)
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return points

    def _calculate_layout(self):
        self.nav_rect = pygame.Rect(0, 0, WINDOW_WIDTH, NAV_HEIGHT)
        self.separator_rect = pygame.Rect(0, NAV_HEIGHT, WINDOW_WIDTH, SEPARATOR_HEIGHT)
        content_y = NAV_HEIGHT + SEPARATOR_HEIGHT
        content_height = WINDOW_HEIGHT - content_y
        left_width = int(WINDOW_WIDTH * CONTENT_LEFT_RATIO)
        right_width = int(WINDOW_WIDTH * CONTENT_RIGHT_RATIO)
        self.content_left_rect = pygame.Rect(0, content_y, left_width, content_height)
        separator_x = left_width
        self.vertical_separator_rect = pygame.Rect(
            separator_x, content_y, VERTICAL_SEPARATOR_WIDTH, content_height
        )
        right_x = separator_x + VERTICAL_SEPARATOR_WIDTH
        self.content_right_rect = pygame.Rect(
            right_x, content_y, right_width, content_height
        )

    def _capture_screenshot(self, map_path: str) -> str:
        try:
            if not self.grid_area:
                return None
            padding = 50
            screenshot_width = self.grid_area.width + padding * 2
            screenshot_height = self.grid_area.height + padding * 2
            screenshot_surface = pygame.Surface((screenshot_width, screenshot_height))
            screenshot_surface.fill(COLOR_WHITE)
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    cell_x = padding + x * GRID_CELL_SIZE
                    cell_y = padding + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
                    cell_rect = pygame.Rect(
                        cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE
                    )
                    cell_value = self.grid_map.grid[y][x]
                    if cell_value == self.grid_map.OBSTACLE:
                        pygame.draw.rect(screenshot_surface, COLOR_BLACK, cell_rect)
                    elif cell_value == self.grid_map.START:
                        pygame.draw.rect(screenshot_surface, (0, 255, 0), cell_rect)
                    elif cell_value == self.grid_map.GOAL:
                        pygame.draw.rect(screenshot_surface, (255, 0, 0), cell_rect)
                    else:
                        pygame.draw.rect(screenshot_surface, COLOR_WHITE, cell_rect)
                    pygame.draw.rect(screenshot_surface, COLOR_LIGHT_GRAY, cell_rect, 1)
            if self.f2_result and self.f2_result.get("path"):
                path = self.f2_result["path"]
                if len(path) > 1:
                    for i in range(len(path) - 1):
                        (x1, y1) = path[i]
                        (x2, y2) = path[i + 1]
                        px1 = padding + x1 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                        py1 = (
                            padding
                            + (GRID_SIZE - 1 - y1) * GRID_CELL_SIZE
                            + GRID_CELL_SIZE // 2
                        )
                        px2 = padding + x2 * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                        py2 = (
                            padding
                            + (GRID_SIZE - 1 - y2) * GRID_CELL_SIZE
                            + GRID_CELL_SIZE // 2
                        )
                        pygame.draw.line(
                            screenshot_surface,
                            (100, 149, 237),
                            (px1, py1),
                            (px2, py2),
                            2,
                        )
            image_path = os.path.join(map_path, "preview.png")
            pygame.image.save(screenshot_surface, image_path)
            return image_path
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def _draw_preview_line(self, grid_area, start_pos, end_pos):
        (start_grid_x, start_grid_y) = self._pixel_to_grid(start_pos)
        (end_grid_x, end_grid_y) = self._pixel_to_grid(end_pos)
        if start_grid_x is None or end_grid_x is None:
            return
        points = self._bresenham_line(
            start_grid_x, start_grid_y, end_grid_x, end_grid_y
        )
        mode = self.editor_status
        if mode == "Obstacle":
            preview_color = (100, 100, 100)
        elif mode == "Ecrease":
            preview_color = (200, 200, 200)
        else:
            return
        grid_area = self.grid_area
        for x, y in points:
            cell_x = grid_area.x + x * GRID_CELL_SIZE
            cell_y = grid_area.y + (GRID_SIZE - 1 - y) * GRID_CELL_SIZE
            cell_rect = pygame.Rect(cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
            pygame.draw.rect(self.screen, preview_color, cell_rect, 2)

    def _handle_f1_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_pressed = True
                self.mouse_start_pos = event.pos
                self.mouse_current_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.mouse_pressed and self.grid_area:
                    end_pos = event.pos
                    self._paint_line(self.mouse_start_pos, end_pos)
                self.mouse_pressed = False
                self.mouse_start_pos = None
                self.mouse_current_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_pressed:
                self.mouse_current_pos = event.pos

    def _handle_f3_mouse_event(self, event):
        pass

    def _init_f4_state(self):
        self.f4_w_min = 0.4
        self.f4_w_max = 0.9
        self.f4_iteration = 250
        self.f4_input_active = None
        self.f4_chart_surface = None
        self.f4_chart_ready = False
        self.f4_input_string = ""

    def _load_selected_map(self):
        if self.map_selected_index >= len(self.map_list):
            return
        map_dir = self.map_list[self.map_selected_index]
        json_path = os.path.join(map_dir, "map.json")
        if not os.path.exists(json_path):
            self.editor_status = self._truncate_status("Map file not found")
            print(f"[F1-LOAD]  Map file not found: {json_path}")
            return
        loaded_map = GridMap.load_map(json_path)
        if loaded_map:
            self.grid_map = loaded_map
            map_name = os.path.basename(map_dir)
            self.editor_status = self._truncate_status(f"Loaded: {map_name}")
            print(f"[F1-LOAD]  Map loaded from: {json_path}")
        else:
            self.editor_status = self._truncate_status("Load failed")
            print("[F1-LOAD]  Failed to load map")

    def _save_with_screenshot(self, data: dict, directory: str, filename: str) -> str:
        """Save JSON data with screenshot (shared helper for map & result)"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_dir = os.path.join(directory, timestamp)
            os.makedirs(save_dir, exist_ok=True)

            json_path = os.path.join(save_dir, filename)
            with open(json_path, "w") as f:
                json.dump(data, f, indent=2)

            image_path = self._capture_screenshot(save_dir)
            print(f"Saved to {save_dir}")
            return os.path.basename(save_dir)
        except Exception as e:
            print(f"Error in _save_with_screenshot: {e}")
            return None

    def _save_map(self):
        name = self._save_with_screenshot(self.grid_map.to_dict(), MAP_DIR, "map.json")
        if name:
            self.editor_status = self._truncate_status(f"Saved: {name}")
            print(f"[F1-SAVE] Map saved: {name}")
        else:
            self.editor_status = self._truncate_status("Save failed")
            print("[F1-SAVE] Failed to save map")

    def _save_result(self):
        if not self.f2_result:
            self.editor_status = self._truncate_status("No result to save")
            print("[F2-SAVE] No result available")
            return
        name = self._save_with_screenshot(self.f2_result, RESULTS_DIR, "result.json")
        if name:
            self.editor_status = self._truncate_status(f"Saved: {name}")
            print(f"[F2-SAVE] Result saved: {name}")
        else:
            self.editor_status = self._truncate_status("Save failed")
            print("[F2-SAVE] Failed to save result")

    def _open_load_map_ui(self):
        import glob

        print("[F1-LOAD] Opening load map UI...")
        if not os.path.exists(MAP_DIR):
            self.editor_status = self._truncate_status("No maps found")
            print(f"[F1-LOAD]  No maps directory at: {MAP_DIR}")
            return
        self.map_list = sorted(glob.glob(os.path.join(MAP_DIR, "*")), reverse=True)
        if not self.map_list:
            self.editor_status = self._truncate_status("No maps to load")
            print("[F1-LOAD]  No maps found")
            return
        self.load_map_mode = True
        self.map_selected_index = 0
        self.map_page = 0
        print(f"[F1-LOAD]  Found {len(self.map_list)} map(s)")

    def _paint_line(self, start_pos, end_pos):
        if not self.grid_area:
            return
        (start_grid_x, start_grid_y) = self._pixel_to_grid(start_pos)
        (end_grid_x, end_grid_y) = self._pixel_to_grid(end_pos)
        if start_grid_x is None or end_grid_x is None:
            return
        points = self._bresenham_line(
            start_grid_x, start_grid_y, end_grid_x, end_grid_y
        )
        mode = self.editor_status
        for x, y in points:
            if mode == "Obstacle":
                self.grid_map.set_obstacle(x, y, True)
            elif mode == "Ecrease":
                self.grid_map.set_obstacle(x, y, False)
            elif mode == "Start":
                self.grid_map.set_start(x, y)
            elif mode == "Goal":
                self.grid_map.set_goal(x, y)

    def _pixel_to_grid(self, pixel_pos):
        if not self.grid_area or not self.grid_area.collidepoint(pixel_pos):
            return (None, None)
        x = int((pixel_pos[0] - self.grid_area.x) / GRID_CELL_SIZE)
        pixel_y = int((pixel_pos[1] - self.grid_area.y) / GRID_CELL_SIZE)
        y = GRID_SIZE - 1 - pixel_y
        x = max(0, min(x, GRID_SIZE - 1))
        y = max(0, min(y, GRID_SIZE - 1))
        return (x, y)

    def _run_line_grid_algorithm(self):
        start = self.grid_map.start
        end = self.grid_map.goal
        self.f3_line_start = start
        self.f3_line_end = end
        if not self.f3_algorithm:
            self.editor_status = "Select algorithm (B/V/D/S)"
            print("[F3]  No algorithm selected")
            return
        if start is None or end is None:
            self.editor_status = "F1 missing Start/Goal"
            print("[F3]  Start or Goal not set in F1")
            return
        print(f"\n[F3] Running {self.f3_algorithm} from {start} to {end}")
        try:
            if self.f3_algorithm == "bresenham":
                self.f3_result_cells = get_line_grid_bresenham(start, end)
            elif self.f3_algorithm == "incremental":
                self.f3_result_cells = get_line_grid_incremental_traversal(start, end)
            elif self.f3_algorithm == "parametric":
                self.f3_result_cells = get_line_grid_parametric_discretization(
                    start, end
                )
            elif self.f3_algorithm == "runs":
                self.f3_result_cells = get_line_grid_runs_of_runs(start, end)
            self.editor_status = (
                f"{self.f3_algorithm}: {len(self.f3_result_cells)} cells"
            )
            print(f"[F3]  Result: {len(self.f3_result_cells)} cells")
            print(
                f"[F3] Cells: {self.f3_result_cells[:10]}{('...' if len(self.f3_result_cells) > 10 else '')}\n"
            )
        except Exception as e:
            print(f"[F3]  Error: {e}")
            self.editor_status = f"Error: {str(e)[:30]}"

    def _run_simulation(self):
        if not self.f2_algorithm:
            self.editor_status = "Select algorithm"
            return
        if not self.grid_map.start or not self.grid_map.goal:
            self.editor_status = "Need Start and Goal"
            return
        self.f2_running = True
        self.editor_status = self._truncate_status(f"Running {self.f2_algorithm}...")
        print(f"\n{'=' * 60}")
        print(f"[F2-SIM] Starting {self.f2_algorithm} simulation")
        print(f"[F2-SIM] Start: {self.grid_map.start}, Goal: {self.grid_map.goal}")
        print(f"[F2-SIM] Remove redundant: {self.f2_remove_redundant}")
        print(f"[F2-SIM] Remove trans redundant: {self.f2_remove_trans_redundant}")
        print(f"[F2-SIM] Avoid corner cutting: {self.f2_avoid_corner_cutting}")
        print(f"{'=' * 60}")
        path = None
        path_length = 0
        execution_time = 0.0
        start_time = time.time()
        if self.f2_algorithm == "A*":
            try:
                astar = AStar(
                    self.grid_map,
                    remove_redundant=self.f2_remove_redundant,
                    remove_transitive=self.f2_remove_trans_redundant,
                    avoid_corner_cutting=self.f2_avoid_corner_cutting,
                )
                path = astar.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running A: {e}")
                path = None
        elif self.f2_algorithm == "PSO":
            try:
                pso = PSOPlanner(
                    self.grid_map,
                    start=self.grid_map.start,
                    goal=self.grid_map.goal,
                    n_waypoints=3,
                    n_particles=30,
                    max_iter=100,
                    w=0.7,
                    c1=1.5,
                    c2=1.5,
                    use_siw=self.f2_use_siw,
                    use_sobl=self.f2_use_sobl,
                )
                path = pso.plan()
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running PSO: {e}")
                path = None
        elif self.f2_algorithm == "APSO":
            try:
                apso = APSO(
                    self.grid_map,
                    n_particles=20,
                    max_iter=50,
                    c1=1.5,
                    c2=1.5,
                    w_min=0.4,
                    w_max=0.9,
                )
                path = apso.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running APSO: {e}")
                path = None
        elif self.f2_algorithm == "HAPSO":
            try:
                hapso = HAPSO(
                    self.grid_map,
                    n_particles=20,
                    max_iter=50,
                    c1=1.5,
                    c2=1.5,
                    w_min=0.4,
                    w_max=0.9,
                )
                path = hapso.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running HAPSO: {e}")
                path = None
        execution_time = time.time() - start_time
        print(f"[F2-SIM] Execution time: {execution_time:.4f}s")
        metrics = {}
        if path:
            print(f"[F2-SIM]  Path found with {len(path)} waypoints")
            metrics = PathMetrics.calculate_metrics(path, execution_time)
            print(
                f"[F2-SIM] Metrics: d={metrics['min_d']:.2f}, p={metrics['min_p']}, i={metrics['min_i']:.4f}"
            )
        else:
            print("[F2-SIM]  No path found")
        self.f2_result = {
            "algorithm": self.f2_algorithm,
            "start": self.grid_map.start,
            "goal": self.grid_map.goal,
            "path": path if path else [],
            "path_length": path_length,
            "execution_time": execution_time,
            "metrics": metrics,
            "remove_redundant": self.f2_remove_redundant,
            "remove_trans_redundant": self.f2_remove_trans_redundant,
            "avoid_corner_cutting": self.f2_avoid_corner_cutting,
        }
        self.f2_running = False
        if path:
            self.editor_status = self._truncate_status(
                f"Done! Path: {len(path)} steps, Time: {execution_time:.4f}s"
            )
        else:
            self.editor_status = "No path found"
        print(f"{'=' * 60}\n")

    def _run_f5_compare(self):
        if not self.grid_map.start or not self.grid_map.goal:
            self.f5_status = "Need Start and Goal"
            self.f5_chart_surface = None
            self.f5_results = {}
            return
        self.f5_status = "Running benchmark..."
        algorithms = ["A*", "PSO", "APSO", "HAPSO"]
        results = {}
        for algo in algorithms:
            path = None
            path_length = 0
            execution_time = 0.0
            metrics = {}
            try:
                start_time = time.time()
                if algo == "A*":
                    planner = AStar(
                        self.grid_map,
                        remove_redundant=True,
                        remove_transitive=True,
                        avoid_corner_cutting=True,
                    )
                    path = planner.find_path(self.grid_map.start, self.grid_map.goal)
                elif algo == "PSO":
                    planner = PSOPlanner(
                        self.grid_map,
                        start=self.grid_map.start,
                        goal=self.grid_map.goal,
                        n_waypoints=3,
                        n_particles=30,
                        max_iter=100,
                        w=0.7,
                        c1=1.5,
                        c2=1.5,
                        use_siw=False,
                        use_sobl=False,
                    )
                    path = planner.plan()
                elif algo == "APSO":
                    planner = APSO(
                        self.grid_map,
                        n_particles=20,
                        max_iter=50,
                        c1=1.5,
                        c2=1.5,
                        w_min=0.4,
                        w_max=0.9,
                    )
                    path = planner.find_path(self.grid_map.start, self.grid_map.goal)
                elif algo == "HAPSO":
                    planner = HAPSO(
                        self.grid_map,
                        n_particles=20,
                        max_iter=50,
                        c1=1.5,
                        c2=1.5,
                        w_min=0.4,
                        w_max=0.9,
                    )
                    path = planner.find_path(self.grid_map.start, self.grid_map.goal)
                execution_time = time.time() - start_time
                if path:
                    path_length = len(path)
                    metrics = PathMetrics.calculate_metrics(path, execution_time)
            except Exception:
                path = None
            results[algo] = {
                "algorithm": algo,
                "path": path if path else [],
                "path_length": path_length,
                "execution_time": execution_time,
                "metrics": metrics,
            }
        self.f5_results = results
        self._update_f5_chart()
        self.f5_status = "Compare complete"

    def _update_f5_chart(self):
        if not self.f5_results:
            self.f5_chart_surface = None
            return
        names = ["A*", "PSO", "APSO", "HAPSO"]
        length_values = []
        turning_values = []
        time_values = []
        waypoint_values = []
        for name in names:
            result = self.f5_results.get(name, {})
            metrics = result.get("metrics", {})
            length_values.append(metrics.get("min_d", 0.0) if metrics else 0.0)
            turning_values.append(metrics.get("min_i", 0.0) if metrics else 0.0)
            time_values.append(metrics.get("min_c", 0.0) if metrics else 0.0)
            waypoint_values.append(metrics.get("min_p", 0) if metrics else 0)
        fig, axes = plt.subplots(2, 2, figsize=(9.0, 5.6), dpi=100)
        fig.suptitle("F5 Result Compare - Metrics", fontsize=12)
        color_set = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2"]

        ax_len = axes[0][0]
        ax_len.bar(names, length_values, color=color_set)
        ax_len.set_title("Length")
        for i, value in enumerate(length_values):
            ax_len.text(i, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

        ax_turn = axes[0][1]
        ax_turn.bar(names, turning_values, color=color_set)
        ax_turn.set_title("Turning")
        for i, value in enumerate(turning_values):
            ax_turn.text(i, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)

        ax_time = axes[1][0]
        ax_time.bar(names, time_values, color=color_set)
        ax_time.set_title("Time")
        for i, value in enumerate(time_values):
            ax_time.text(i, value, f"{value:.3f}", ha="center", va="bottom", fontsize=8)

        ax_waypoint = axes[1][1]
        ax_waypoint.bar(names, waypoint_values, color=color_set)
        ax_waypoint.set_title("Waypoint")
        for i, value in enumerate(waypoint_values):
            ax_waypoint.text(
                i, value, f"{int(value)}", ha="center", va="bottom", fontsize=8
            )

        for ax in [ax_len, ax_turn, ax_time, ax_waypoint]:
            ax.tick_params(axis="x", labelrotation=0)
        fig.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        self.f5_chart_surface = pygame.image.load(
            buffer, "f5_chart.png"
        ).convert_alpha()

    def _truncate_status(self, text: str, max_len: int = 30) -> str:
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def _update_f4_chart(self):
        from io import BytesIO
        import pygame
        from f4_weight_compare import plot_inertia_weights

        plt = plot_inertia_weights(self.f4_w_min, self.f4_w_max, self.f4_iteration)
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        self.f4_chart_surface = pygame.image.load(buf).convert_alpha()
        self.f4_chart_ready = True
