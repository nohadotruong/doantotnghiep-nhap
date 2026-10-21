
from config import F5_MENU_ITEMS
from config.ui_config import (
    CENTER_WINDOW,
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    CONTENT_LEFT_RATIO,
    CONTENT_RIGHT_RATIO,
    F1_MENU_ITEMS,
    F2_MENU_ITEMS,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_SMALL,
    FPS,
    FULLSCREEN,
    GRID_CELL_SIZE,
    GRID_SIZE,
    MAP_DIR,
    NAV_HEIGHT,
    RESULTS_DIR,
    SEPARATOR_HEIGHT,
    VERTICAL_SEPARATOR_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from core.algorithms.apso import APSO
from core.algorithms.astar import AStar
from core.algorithms.hapso import HAPSO
from core.algorithms.pso_planner import PSOPlanner
from core.models import PathResult, ComparisonMetrics
from gui.event_handler import EventHandler
from gui.renderer import Renderer
from map.grid_map import GridMap
from map.map_serializer import MapSerializer
from state.app_state import get_app_state

import matplotlib
import os
import pygame
import sys
import time

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
        self.f2_algorithm_display = None
        self.f2_remove_redundant = False
        self.f2_remove_trans_redundant = False
        self.f2_avoid_corner_cutting = False
        self.f2_use_siw = False
        self.f2_use_sobl = False
        self.f2_running = False
        self.f2_result = None
        self.f2_all_results = []

        self.f3_algorithm = None
        self.f3_line_start = None
        self.f3_line_end = None
        self.f3_result_cells = []
        self.f3_drawing_line = False

        self.f5_status = "Ready"
        self.f5_results = {}
        self.f5_chart_surface = None

        self.renderer = Renderer()
        self.event_handler = EventHandler()
        self._calculate_layout()
        self._init_f4_state()

    def draw_content_area(self):
        self.renderer.draw_content_area(self)

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
        self.renderer.draw_grid(self)

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
        self.renderer.draw_load_map_ui(self)

    def draw_navigation_bar(self):
        self.renderer.draw_navigation_bar(self)

    def draw_separator(self):
        self.renderer.draw_separator(self)

    def handle_events(self):
        self.event_handler.handle_events(self)

    def render(self):
        self.renderer.render(self)

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
            print(f"[APP]: Error capturing screenshot: {e}")
            return None

    def get_preview_line_points(self, start_pos, end_pos):
        """Returns the points for a preview line when mouse is held down during drawing."""
        if not self.grid_area or not start_pos or not end_pos:
            return []
        (start_grid_x, start_grid_y) = self._pixel_to_grid(start_pos)
        (end_grid_x, end_grid_y) = self._pixel_to_grid(end_pos)
        if start_grid_x is None or end_grid_x is None:
            return []
        points = self._bresenham_line(start_grid_x, start_grid_y, end_grid_x, end_grid_y)
        mode = self.editor_status
        if mode in ("Obstacle", "Ecrase", "Start", "Goal"):
            return points
        return []

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
            print(f"[APP]: Map file not found: {json_path}")
            return
        loaded_map = MapSerializer.load(json_path)
        if loaded_map:
            self.grid_map = loaded_map
            map_name = os.path.basename(map_dir)
            self.editor_status = self._truncate_status(f"Loaded: {map_name}")
            print(f"[APP]: Map loaded from: {json_path}")
        else:
            self.editor_status = self._truncate_status("Load failed")
            print("[APP]: Failed to load map")

    def _save_map(self):
        save_result = MapSerializer.save(
            self.grid_map,
            map_dir=MAP_DIR,
            screenshot_func=self._capture_screenshot,
        )
        if save_result:
            json_path, _ = save_result
            name = os.path.basename(os.path.dirname(json_path))
            self.editor_status = self._truncate_status(f"Saved: {name}")
            print(f"[APP]: Map saved: {name}")
        else:
            self.editor_status = self._truncate_status("Save failed")
            print("[APP]: Failed to save map")

    def _save_result(self):
        if not self.f2_result:
            self.editor_status = self._truncate_status("No result to save")
            print("[APP]: No result available")
            return
        # Result serialization now handled by AppState instead of direct saving
        # result_path = ResultSerializer.save(self.f2_result, results_dir=RESULTS_DIR)
        # if result_path:
        #     name = os.path.basename(os.path.dirname(result_path))
        self.editor_status = self._truncate_status(f"Result saved to AppState")
        print("[APP]: Result saved to AppState")

    def _open_load_map_ui(self):
        import glob

        print("[APP]: Opening load map UI...")
        if not os.path.exists(MAP_DIR):
            self.editor_status = self._truncate_status("No maps found")
            print(f"[APP]: No maps directory at: {MAP_DIR}")
            return
        self.map_list = sorted(glob.glob(os.path.join(MAP_DIR, "*")), reverse=True)
        if not self.map_list:
            self.editor_status = self._truncate_status("No maps to load")
            print("[APP]: No maps found")
            return
        self.load_map_mode = True
        self.map_selected_index = 0
        self.map_page = 0
        print(f"[APP]: Found {len(self.map_list)} map(s)")

    def _paint_line(self, start_pos, end_pos):
        if not self.grid_area:
            return
        (start_grid_x, start_grid_y) = self._pixel_to_grid(start_pos)
        (end_grid_x, end_grid_y) = self._pixel_to_grid(end_pos)
        if start_grid_x is None or end_grid_x is None:
            return

        # Use inline Bresenham implementation
        points = self._bresenham_line(
            start_grid_x, start_grid_y, end_grid_x, end_grid_y
        )

        mode = self.editor_status
        for x, y in points:
            if mode == "Obstacle":
                self.grid_map.set_obstacle(x, y, True)
            elif mode == "Ecrase":
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

    @staticmethod
    def _bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
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

    # Deprecated: _run_line_grid_algorithm was for old F3 line grid page (removed)
    # def _run_line_grid_algorithm(self):
    #     start = self.grid_map.start
    #     end = self.grid_map.goal
    #     self.f3_line_start = start
    #     self.f3_line_end = end
    #     if not self.f3_algorithm:
    #         self.editor_status = "Select algorithm (B/V/D/S)"
    #         print("[F3]  No algorithm selected")
    #         return
    #     if start is None or end is None:
    #         self.editor_status = "F1 missing Start/Goal"
    #         print("[F3]  Start or Goal not set in F1")
    #         return
    #     print(f"\n[F3] Running {self.f3_algorithm} from {start} to {end}")
    #     try:
    #         if self.f3_algorithm == "bresenham":
    #             self.f3_result_cells = LineDrawer.bresenham(start, end)
    #         elif self.f3_algorithm == "incremental":
    #             self.f3_result_cells = LineDrawer.incremental(start, end)
    #         elif self.f3_algorithm == "parametric":
    #             self.f3_result_cells = LineDrawer.parametric(start, end)
    #         elif self.f3_algorithm == "runs":
    #             self.f3_result_cells = LineDrawer.runs_of_runs(start, end)
    #         self.editor_status = (
    #             f"{self.f3_algorithm}: {len(self.f3_result_cells)} cells"
    #         )
    #         print(f"[F3]  Result: {len(self.f3_result_cells)} cells")
    #         print(
    #             f"[F3] Cells: {self.f3_result_cells[:10]}{('...' if len(self.f3_result_cells) > 10 else '')}\n"
    #         )
    #     except Exception as e:
    #         print(f"[F3]  Error: {e}")
    #         self.editor_status = f"Error: {str(e)[:30]}"

    def _run_all_algorithms(self):
        state = get_app_state()
        self.f2_running = True
        self.editor_status = "Running comparison..."

        algorithms = [
            (
                "A*",
                {
                    "remove_redundant": False,
                    "remove_transitive": False,
                    "avoid_corner_cutting": False,
                },
            ),
            ("PSO", {"use_siw": False, "use_sobl": False}),
            ("APSO", {}),
            ("HAPSO", {}),
        ]

        comparison = ComparisonMetrics(algorithm_results={})

        print(f"\n{'=' * 60}")
        print("[COMPARISON] Running all algorithms...")
        print(f"[COMPARISON]: Start: {self.grid_map.start}, Goal: {self.grid_map.goal}")
        print(f"{'=' * 60}")

        for algo_name, params in algorithms:
            start_time = time.time()
            path = None
            success = False
            error_msg = ""

            try:
                if algo_name == "A*":
                    astar = AStar(self.grid_map, **params)
                    path = astar.find_path(self.grid_map.start, self.grid_map.goal)
                    success = path is not None

                elif algo_name == "PSO":
                    pso = PSOPlanner(self.grid_map, **params)
                    path = pso.find_path(self.grid_map.start, self.grid_map.goal)
                    success = path is not None

                elif algo_name == "APSO":
                    apso = APSO(self.grid_map)
                    path = apso.find_path(self.grid_map.start, self.grid_map.goal)
                    success = path is not None

                elif algo_name == "HAPSO":
                    hapso = HAPSO(self.grid_map)
                    path = hapso.find_path(self.grid_map.start, self.grid_map.goal)
                    success = path is not None

            except Exception as e:
                error_msg = str(e)
                print(f"[COMPARISON] Error running {algo_name}: {e}")
                success = False

            execution_time = time.time() - start_time

            # Create PathResult
            result = PathResult(
                algorithm=algo_name,
                path=path if path else None,
                metrics={"waypoints": len(path) if path else 0},
                execution_time=execution_time,
                success=success,
                error_message=error_msg,
            )

            comparison.add_result(algo_name, result)

            status_msg = (
                f"{algo_name}: {len(path)} waypoints, {execution_time:.4f}s"
                if path
                else f"{algo_name}: No path"
            )
            print(f"[COMPARISON] {status_msg}")

        print(f"{'=' * 60}\n")

        # Save to AppState
        state.set_f3_comparison(comparison)

        # Auto-switch to F3 page
        self.current_page = pygame.K_F3
        self.editor_status = "Comparison done! Switched to F3"
        self.f2_running = False

        print("[COMPARISON] Results saved to AppState, switched to F3")

    def _run_simulation(self):
        state = get_app_state()
        if not self.f2_algorithm:
            self.editor_status = "Select algorithm"
            return
        if not self.grid_map.start or not self.grid_map.goal:
            self.editor_status = "Need Start and Goal"
            return

        if self.f2_algorithm == "All":
            self._run_all_algorithms()
            return

        self.f2_running = True
        self.editor_status = "On progress"
        self.f2_all_results = []
        print(f"\n{'=' * 60}")
        print(f"[F2-SIM] Starting {self.f2_algorithm} simulation")
        print(f"[F2-SIM] Start: {self.grid_map.start}, Goal: {self.grid_map.goal}")
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
                    use_siw=self.f2_use_siw,
                    use_sobl=self.f2_use_sobl,
                )
                path = pso.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running PSO: {e}")
                path = None
        elif self.f2_algorithm == "APSO":
            try:
                apso = APSO(self.grid_map)
                path = apso.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running APSO: {e}")
                path = None
        elif self.f2_algorithm == "HAPSO":
            try:
                hapso = HAPSO(self.grid_map)
                path = hapso.find_path(self.grid_map.start, self.grid_map.goal)
                if path:
                    path_length = len(path)
            except Exception as e:
                print(f"[F2-SIM]  Error running HAPSO: {e}")
                path = None

        execution_time = time.time() - start_time
        print(f"[F2-SIM] Execution time: {execution_time:.4f}s")

        success = path is not None
        error_msg = "" if success else "No path found"

        if path:
            print(f"[F2-SIM]  Path found with {len(path)} waypoints")
        else:
            print("[F2-SIM]  No path found")

        # Create PathResult and save to AppState
        result = PathResult(
            algorithm=self.f2_algorithm,
            path=path if path else None,
            metrics={"waypoints": len(path) if path else 0},
            execution_time=execution_time,
            success=success,
            error_message=error_msg,
        )
        state.add_f2_result(self.f2_algorithm, result)

        # Keep old format for backward compatibility with renderer
        self.f2_result = {
            "algorithm": self.f2_algorithm,
            "path": path if path else [],
            "execution_time": execution_time,
        }

        self.f2_running = False
        if path:
            self.editor_status = self._truncate_status(
                f"Done! Path: {len(path)} steps, Time: {execution_time:.4f}s"
            )
        else:
            self.editor_status = "No path found"
        print(f"{'=' * 60}\n")

    # Deprecated methods (kept for reference, but not used in new architecture)
    # def _run_f5_compare(self):
    #     if not self.grid_map.start or not self.grid_map.goal:
    #         self.f5_status = "Need Start and Goal"
    #         self.f5_chart_surface = None
    #         self.f5_results = {}
    #         return
    #     self.f5_status = "Running benchmark..."
    #     # self.f5_results = ComparisonRunner.run_all(self.grid_map)
    #     self._update_f5_chart()
    #     self.f5_status = "Compare complete"
    #
    # def _update_f5_chart(self):
    #     # self.f5_chart_surface = ChartBuilder.build_comparison_chart(self.f5_results)
    #     pass
    #
    # def _update_f4_chart(self):
    #     # self.f4_chart_surface = ChartBuilder.build_weight_chart(
    #     #     self.f4_w_min,
    #     #     self.f4_w_max,
    #     #     self.f4_iteration,
    #     # )
    #     # self.f4_chart_ready = True
    #     pass

    def _truncate_status(self, text: str, max_len: int = 30) -> str:
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."
