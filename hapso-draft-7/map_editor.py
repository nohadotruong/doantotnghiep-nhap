from config.ui_config import (
    COLOR_BLACK,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    F1_MENU_ITEMS,
    FONT_SIZE_DEFAULT,
    GRID_CELL_SIZE,
    GRID_SIZE,
)
from map.grid_map import GridMap
from map.map_serializer import MapSerializer

import os
import pygame


class MapEditor:
    COLOR_GRID = (200, 200, 200)
    COLOR_OBSTACLE = (50, 50, 50)
    COLOR_START = (0, 200, 0)
    COLOR_GOAL = (200, 0, 0)
    COLOR_HIGHLIGHT = (100, 100, 255)

    def __init__(self) -> None:
        self.menu_items = F1_MENU_ITEMS
        self.editor_status = self.menu_items[0].split(": ", 1)[1]

    def draw(self, app) -> None:
        self.draw_menu(app)
        self.draw_info_panel(app)
        self.draw_grid(app)

    def draw_menu(self, app) -> None:
        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        status_y = app.content_left_rect.y + 10
        status_text = f"Status: {self.editor_status}"
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

    def draw_grid(self, app) -> None:
        pygame.draw.rect(
            app.screen,
            COLOR_WHITE,
            (
                app.content_right_rect.x,
                app.content_right_rect.y,
                app.content_right_rect.width,
                app.content_right_rect.height,
            ),
        )

        available_width = app.content_right_rect.width - 20
        available_height = app.content_right_rect.height - 20
        cell_size_w = available_width // GRID_SIZE
        cell_size_h = available_height // GRID_SIZE
        cell_size = min(cell_size_w, cell_size_h)

        grid_start_x = app.content_right_rect.x + 10
        grid_start_y = app.content_right_rect.y + 10

        for x in range(GRID_SIZE + 1):
            pygame.draw.line(
                app.screen,
                self.COLOR_GRID,
                (grid_start_x + x * cell_size, grid_start_y),
                (grid_start_x + x * cell_size, grid_start_y + GRID_SIZE * cell_size),
            )

        for y in range(GRID_SIZE + 1):
            pygame.draw.line(
                app.screen,
                self.COLOR_GRID,
                (grid_start_x, grid_start_y + y * cell_size),
                (grid_start_x + GRID_SIZE * cell_size, grid_start_y + y * cell_size),
            )

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell_x = grid_start_x + x * cell_size
                cell_y = grid_start_y + y * cell_size

                if app.grid_map.grid[y][x] == GridMap.OBSTACLE:
                    pygame.draw.rect(
                        app.screen,
                        self.COLOR_OBSTACLE,
                        (cell_x, cell_y, cell_size, cell_size),
                    )
                elif app.grid_map.grid[y][x] == GridMap.START:
                    pygame.draw.rect(
                        app.screen,
                        self.COLOR_START,
                        (cell_x, cell_y, cell_size, cell_size),
                    )
                elif app.grid_map.grid[y][x] == GridMap.GOAL:
                    pygame.draw.rect(
                        app.screen,
                        self.COLOR_GOAL,
                        (cell_x, cell_y, cell_size, cell_size),
                    )

        if app.mouse_pressed and app.mouse_start_pos and app.mouse_current_pos:
            preview_points = self.get_preview_line_points(
                app, app.mouse_start_pos, app.mouse_current_pos
            )
            mode = self.editor_status
            if mode == "Obstacle":
                preview_color = (100, 100, 100)
            elif mode == "Erase":
                preview_color = (200, 200, 200)
            elif mode == "Set Start":
                preview_color = (0, 150, 0)
            elif mode == "Set Goal":
                preview_color = (150, 0, 0)
            else:
                preview_color = None

            if preview_color:
                for x, y in preview_points:
                    cell_x = grid_start_x + x * cell_size
                    cell_y = grid_start_y + y * cell_size
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    pygame.draw.rect(app.screen, preview_color, cell_rect, 2)

        app.grid_area = {
            "start_x": grid_start_x,
            "start_y": grid_start_y,
            "cell_size": cell_size,
        }

    def handle_key_press(self, app, key: int) -> None:
        if key == pygame.K_1:
            app.selected_item = 0
            self.editor_status = "Obstacle"
            print("[MAP_EDITOR]: Mode: Obstacle")

        elif key == pygame.K_2:
            app.selected_item = 1
            self.editor_status = "Erase"
            print("[MAP_EDITOR]: Mode: Erase")

        elif key == pygame.K_s:
            app.selected_item = 2
            self.editor_status = "Set Start"
            print("[MAP_EDITOR]: Mode: Set Start")

        elif key == pygame.K_g:
            app.selected_item = 3
            self.editor_status = "Set Goal"
            print("[MAP_EDITOR]: Mode: Set Goal")

        elif key == pygame.K_RETURN:
            self._save_map(app)

        elif key == pygame.K_l:
            print("[MAP_EDITOR]: Loading map...")
            self._load_map(app)

        elif key == pygame.K_c:
            app.grid_map.clear_map()
            self.editor_status = "Cleared"
            print("[MAP_EDITOR]: Map cleared")

    def handle_mouse_click(self, app, pos: tuple[int, int], button: int) -> None:
        if button == 1:
            app.mouse_pressed = True
            app.mouse_start_pos = pos
            app.mouse_current_pos = pos

    def handle_mouse_motion(self, app, pos: tuple[int, int]) -> None:
        if app.mouse_pressed:
            app.mouse_current_pos = pos

    def handle_mouse_release(self, app, pos: tuple[int, int]) -> None:
        if app.mouse_pressed and app.grid_area:
            self._paint_line(app, app.mouse_start_pos, pos)
        app.mouse_pressed = False
        app.mouse_start_pos = None
        app.mouse_current_pos = None

    def _paint_line(
        self, app, start_pos: tuple[int, int], end_pos: tuple[int, int]
    ) -> None:
        start_grid = self._pixel_to_grid(app, start_pos)
        end_grid = self._pixel_to_grid(app, end_pos)

        if start_grid is None or end_grid is None:
            return

        start_grid_x, start_grid_y = start_grid
        end_grid_x, end_grid_y = end_grid

        points = self._bresenham_line(
            start_grid_x, start_grid_y, end_grid_x, end_grid_y
        )

        mode = self.editor_status
        for x, y in points:
            if mode == "Obstacle":
                app.grid_map.set_obstacle(x, y, True)
            elif mode == "Erase":
                app.grid_map.set_obstacle(x, y, False)
            elif mode == "Set Start":
                app.grid_map.set_start(x, y)
            elif mode == "Set Goal":
                app.grid_map.set_goal(x, y)

    def _pixel_to_grid(self, app, pixel_pos: tuple[int, int]) -> tuple[int, int] | None:
        if not app.grid_area:
            return None

        grid_start_x = app.grid_area["start_x"]
        grid_start_y = app.grid_area["start_y"]
        cell_size = app.grid_area["cell_size"]

        grid_end_x = grid_start_x + GRID_SIZE * cell_size
        grid_end_y = grid_start_y + GRID_SIZE * cell_size

        x, y = pixel_pos

        if not (grid_start_x <= x <= grid_end_x and grid_start_y <= y <= grid_end_y):
            return None

        grid_x = int((x - grid_start_x) // cell_size)
        grid_y = int((y - grid_start_y) // cell_size)

        grid_x = max(0, min(grid_x, GRID_SIZE - 1))
        grid_y = max(0, min(grid_y, GRID_SIZE - 1))

        return (grid_x, grid_y)

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

    def get_preview_line_points(
        self, app, start_pos: tuple[int, int], end_pos: tuple[int, int]
    ) -> list[tuple[int, int]]:
        if not app.grid_area or not start_pos or not end_pos:
            return []

        start_grid = self._pixel_to_grid(app, start_pos)
        end_grid = self._pixel_to_grid(app, end_pos)

        if start_grid is None or end_grid is None:
            return []

        start_grid_x, start_grid_y = start_grid
        end_grid_x, end_grid_y = end_grid

        points = self._bresenham_line(
            start_grid_x, start_grid_y, end_grid_x, end_grid_y
        )
        mode = self.editor_status
        if mode in ("Obstacle", "Erase", "Set Start", "Set Goal"):
            return points
        return []

    def _save_map(self, app) -> None:
        if not app.grid_map.start or not app.grid_map.goal:
            self.editor_status = "Set Start and Goal before saving"
            return

        result = MapSerializer.save(
            app.grid_map,
            map_dir="data/maps",
            screenshot_func=self._create_screenshot,
        )

        if result:
            json_path, image_path = result
            self.editor_status = f"Saved: {json_path}"
            print(f"[MAP_EDITOR] Map saved to {json_path}")
            if image_path:
                print(f"[MAP_EDITOR] Preview saved to {image_path}")
        else:
            self.editor_status = "Save failed"

    def _load_map(self, app) -> None:
        self.editor_status = "Load map - not implemented yet"
        print("[MAP_EDITOR] Load map temporarily disabled")

    def _create_screenshot(self, map_dir: str) -> str | None:
        cell_size = 30
        surface = pygame.Surface((GRID_SIZE * cell_size, GRID_SIZE * cell_size))
        surface.fill(COLOR_WHITE)

        for x in range(GRID_SIZE):
            pygame.draw.line(
                surface,
                self.COLOR_GRID,
                (x * cell_size, 0),
                (x * cell_size, GRID_SIZE * cell_size),
            )

        for y in range(GRID_SIZE):
            pygame.draw.line(
                surface,
                self.COLOR_GRID,
                (0, y * cell_size),
                (GRID_SIZE * cell_size, y * cell_size),
            )

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                grid = GridMap(GRID_SIZE, GRID_SIZE)
                if grid.grid[y][x] == GridMap.OBSTACLE:
                    pygame.draw.rect(
                        surface,
                        self.COLOR_OBSTACLE,
                        (x * cell_size, y * cell_size, cell_size, cell_size),
                    )
                elif grid.grid[y][x] == GridMap.START:
                    pygame.draw.rect(
                        surface,
                        self.COLOR_START,
                        (x * cell_size, y * cell_size, cell_size, cell_size),
                    )
                elif grid.grid[y][x] == GridMap.GOAL:
                    pygame.draw.rect(
                        surface,
                        self.COLOR_GOAL,
                        (x * cell_size, y * cell_size, cell_size, cell_size),
                    )

        image_path = os.path.join(map_dir, "preview.png")
        pygame.image.save(surface, image_path)
        return image_path


class AppStub:
    def __init__(self, window_width: int = 850, window_height: int = 650):
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Map Editor")
        self.clock = pygame.time.Clock()
        self.running = True

        left_width = int(window_width * 0.25)
        right_width = window_width - left_width - 2

        class Rect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

        self.content_left_rect = Rect(0, 0, left_width, window_height)
        self.content_right_rect = Rect(left_width + 2, 0, right_width, window_height)

        self.grid_map = GridMap(GRID_SIZE, GRID_SIZE)
        self.selected_item = 0
        self.grid_area = None

        self.mouse_pressed = False
        self.mouse_start_pos = None
        self.mouse_current_pos = None

    def draw_background(self):
        self.screen.fill(COLOR_WHITE)

        pygame.draw.line(
            self.screen,
            COLOR_DARK_GRAY,
            (self.content_left_rect.width + 1, 0),
            (self.content_left_rect.width + 1, self.screen.get_height()),
            2,
        )

    def run(self):
        editor = MapEditor()
        print("[MAP_EDITOR] Running standalone map editor...")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        editor.handle_key_press(self, event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    editor.handle_mouse_click(self, event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    editor.handle_mouse_release(self, event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    editor.handle_mouse_motion(self, event.pos)

            self.draw_background()
            editor.draw(self)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        print("[MAP_EDITOR] Map editor closed")


def main() -> None:
    app = AppStub()
    app.run()


if __name__ == "__main__":
    main()
