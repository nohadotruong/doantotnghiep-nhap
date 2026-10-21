import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.algo_config import MAP_SAVE_DIR, DEFAULT_MAP_PATH
from config.ui_config import (
    GRID_HEIGHT,
    GRID_CELL_SIZE,
    AXIS_LABEL_WIDTH,
    AXIS_LABEL_HEIGHT,
    AXIS_TO_GRID,
    GRID_WIDTH,
    MARGIN,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_WAYPOINT,
    FONT_SIZE_DEFAULT,
)
from map.grid_map import GridMap
from map.map_serializer import MapSerializer


class MapEditor:
    def __init__(self) -> None:
        pygame.init()

        loaded = MapSerializer.load(DEFAULT_MAP_PATH)
        if loaded is not None:
            self.grid_map = loaded
        else:
            self.grid_map = GridMap(GRID_WIDTH, GRID_HEIGHT)
        self.grid_width = self.grid_map.width * GRID_CELL_SIZE
        self.grid_height = self.grid_map.height * GRID_CELL_SIZE

        window_width = (
            MARGIN + AXIS_LABEL_WIDTH + AXIS_TO_GRID + self.grid_width + MARGIN
        )
        window_height = (
            MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID + self.grid_height + MARGIN
        )
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Map Editor")
        self.clock = pygame.time.Clock()
        self.running = True

        self.axis_y_x = MARGIN
        self.axis_y_y = MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID
        self.axis_x_x = MARGIN + AXIS_LABEL_WIDTH + AXIS_TO_GRID
        self.axis_x_y = MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID + self.grid_height

        self.mode = "Obstacle"
        self.is_mouse_pressed = False
        self.line_start = None
        self.line_end = None

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

    def handle_keydown(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_1:
            self.mode = "Obstacle"
        elif event.key == pygame.K_2:
            self.mode = "Erase"
        elif event.key == pygame.K_s:
            self.mode = "Start"
        elif event.key == pygame.K_g:
            self.mode = "Goal"
        elif event.key == pygame.K_c:
            self.grid_map.clear_map()
        elif event.key == pygame.K_RETURN:
            self.save_map()

    def handle_mouse_down(self, event) -> None:
        if event.button != 1:
            return
        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return
        if self.mode in ("Obstacle", "Erase"):
            self.is_mouse_pressed = True
            self.line_start = grid_pos
            self.line_end = grid_pos
        elif self.mode == "Start":
            self.grid_map.set_start(grid_pos[0], grid_pos[1])
        elif self.mode == "Goal":
            self.grid_map.set_goal(grid_pos[0], grid_pos[1])

    def handle_mouse_motion(self, event) -> None:
        if not self.is_mouse_pressed:
            return
        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return
        self.line_end = grid_pos

    def handle_mouse_up(self, event) -> None:
        if event.button != 1:
            return
        if self.is_mouse_pressed and self.line_start and self.line_end:
            points = self.bresenham_line(self.line_start, self.line_end)
            self.apply_line(points)
        self.is_mouse_pressed = False
        self.line_start = None
        self.line_end = None

    def screen_to_grid(self, pos) -> tuple[int, int] | None:
        x, y = pos
        if (
            x < self.axis_x_x
            or y < self.axis_y_y
            or x >= self.axis_x_x + self.grid_width
            or y >= self.axis_y_y + self.grid_height
        ):
            return None
        grid_x = (x - self.axis_x_x) // GRID_CELL_SIZE
        grid_y = (y - self.axis_y_y) // GRID_CELL_SIZE
        return (grid_x, grid_y)

    def bresenham_line(self, start, end) -> list[tuple[int, int]]:
        x0, y0 = start
        x1, y1 = end
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

    def apply_line(self, points) -> None:
        for x, y in points:
            if self.mode == "Obstacle":
                self.grid_map.set_obstacle(x, y, True)
            elif self.mode == "Erase":
                self.grid_map.set_obstacle(x, y, False)

    def draw(self) -> None:
        self.screen.fill(COLOR_WHITE)
        self.draw_grid()
        self.draw_axes()
        self.draw_preview()
        pygame.display.flip()

    def draw_grid(self) -> None:
        for i in range(self.grid_map.height):
            for j in range(self.grid_map.width):
                cell_x = self.axis_x_x + j * GRID_CELL_SIZE
                cell_y = self.axis_y_y + i * GRID_CELL_SIZE

                if self.grid_map.grid[i][j] == self.grid_map.OBSTACLE:
                    pygame.draw.rect(
                        self.screen,
                        COLOR_BLACK,
                        (cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        COLOR_LIGHT_GRAY,
                        (cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
                        1,
                    )

        if self.grid_map.start is not None:
            start_x, start_y = self.grid_map.start
            start_px = self.axis_x_x + start_x * GRID_CELL_SIZE
            start_py = self.axis_y_y + start_y * GRID_CELL_SIZE
            pygame.draw.rect(
                self.screen,
                COLOR_GREEN,
                (start_px, start_py, GRID_CELL_SIZE, GRID_CELL_SIZE),
            )
            pygame.draw.circle(
                self.screen,
                COLOR_WAYPOINT,
                (start_px + GRID_CELL_SIZE // 2, start_py + GRID_CELL_SIZE // 2),
                GRID_CELL_SIZE // 5,
            )

        if self.grid_map.goal is not None:
            goal_x, goal_y = self.grid_map.goal
            goal_px = self.axis_x_x + goal_x * GRID_CELL_SIZE
            goal_py = self.axis_y_y + goal_y * GRID_CELL_SIZE
            pygame.draw.rect(
                self.screen,
                COLOR_RED,
                (goal_px, goal_py, GRID_CELL_SIZE, GRID_CELL_SIZE),
            )
            pygame.draw.circle(
                self.screen,
                COLOR_WAYPOINT,
                (goal_px + GRID_CELL_SIZE // 2, goal_py + GRID_CELL_SIZE // 2),
                GRID_CELL_SIZE // 5,
            )

        for i in range(self.grid_map.width + 1):
            x = self.axis_x_x + i * GRID_CELL_SIZE
            pygame.draw.line(
                self.screen, COLOR_GRAY, (x, self.axis_y_y), (x, self.axis_x_y), 1
            )

        for i in range(self.grid_map.height + 1):
            y = self.axis_y_y + i * GRID_CELL_SIZE
            pygame.draw.line(
                self.screen,
                COLOR_GRAY,
                (self.axis_x_x, y),
                (self.axis_y_x + self.grid_width, y),
                1,
            )

    def draw_axes(self) -> None:
        font = pygame.font.Font(None, 24)
        for i in range(self.grid_map.width):
            text = font.render(str(i), True, COLOR_BLACK)
            text_rect = text.get_rect()
            x = self.axis_x_x + i * GRID_CELL_SIZE
            self.screen.blit(
                text, (x + (GRID_CELL_SIZE - text_rect.width) // 2, MARGIN + 2)
            )

        for i in range(self.grid_map.height):
            text = font.render(str(i), True, COLOR_BLACK)
            text_rect = text.get_rect()
            y = self.axis_y_y + i * GRID_CELL_SIZE
            self.screen.blit(
                text, (MARGIN + 2, y + (GRID_CELL_SIZE - text_rect.height) // 2)
            )

    def draw_preview(self) -> None:
        if (
            not self.is_mouse_pressed
            or self.line_start is None
            or self.line_end is None
        ):
            return
        points = self.bresenham_line(self.line_start, self.line_end)
        for x, y in points:
            cell_x = self.axis_x_x + x * GRID_CELL_SIZE
            cell_y = self.axis_y_y + y * GRID_CELL_SIZE
            pygame.draw.rect(
                self.screen,
                COLOR_GRAY,
                (cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
                2,
            )

    def save_map(self) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[MAP_EDITOR]: Error - start or goal missing")
            return

        json_path = MapSerializer.save(self.grid_map, map_dir=MAP_SAVE_DIR)
        if json_path is None:
            print("[MAP_EDITOR]: Error - save failed")
            return

        map_dir = Path(json_path).parent
        image_path = map_dir / "map.png"
        self.save_map_image(str(image_path))
        print(f"[MAP_EDITOR]: Saved to {map_dir}")

    def save_map_image(self, image_path: str) -> None:
        # Save the current display so the saved image includes axes/margins
        pygame.image.save(self.screen, image_path)


if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
