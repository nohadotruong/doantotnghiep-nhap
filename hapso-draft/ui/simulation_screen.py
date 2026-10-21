from __future__ import annotations

import pygame

from app_io.result_io import save_result_bundle
from evaluation.metrics import node_count, objective, total_rotation, path_length
from planners.astar import AStarPlanner
from planners.hybrid import HybridPlanner
from planners.pso_optimizer import PSOOptimizer
from planners.pso_planner import PSOPlanner
from ui.common import FONT_NORMAL, FONT_SMALL, PALETTE, Button, draw_title


class SimulationScreen:
    def __init__(self, app: object) -> None:
        self.app = app
        self.grid_origin = (0, 0)
        self.right_panel_x = 0
        self.algorithm = "HAPSO"
        self.last_status = "Press SPACE to run planner"
        self.path_info: dict[str, float | int] | None = None
        self.remove_points = True
        self.remove_waypoints = True
        self.avoid_corner_cutting = True
        self.controls = [
            Button(pygame.Rect(24, 117, 294, 30), "A*", "A"),
            Button(pygame.Rect(24, 152, 294, 30), "PSO", "P"),
            Button(pygame.Rect(24, 187, 294, 30), "APSO", "O"),
            Button(pygame.Rect(24, 222, 294, 30), "HAPSO", "H"),
            Button(pygame.Rect(24, 257, 294, 30), "Run Planner", "SPACE"),
            Button(pygame.Rect(24, 292, 294, 30), "Save Result", "K"),
            Button(pygame.Rect(24, 327, 294, 30), "Toggle Remove Points", "1"),
            Button(pygame.Rect(24, 362, 294, 30), "Toggle Waypoint Prune", "2"),
            Button(pygame.Rect(24, 397, 294, 30), "Toggle Corner Cutting", "3"),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_a:
            self.algorithm = "A*"
        elif event.key == pygame.K_p:
            self.algorithm = "PSO"
        elif event.key == pygame.K_o:
            self.algorithm = "APSO"
        elif event.key == pygame.K_h:
            self.algorithm = "HAPSO"
        elif event.key == pygame.K_1:
            self.remove_points = not self.remove_points
        elif event.key == pygame.K_2:
            self.remove_waypoints = not self.remove_waypoints
        elif event.key == pygame.K_3:
            self.avoid_corner_cutting = not self.avoid_corner_cutting
        elif event.key == pygame.K_k:
            self._save_result()
        elif event.key == pygame.K_SPACE:
            self._run_planner()

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()
        surface.fill(PALETTE["bg"])

        # Calculate panel boundaries for 3-4-3 ratio
        left_panel_width = int(self.app.window_width * 0.3)
        center_panel_width = int(self.app.window_width * 0.4)
        right_panel_x = left_panel_width + center_panel_width

        content_top = 40
        content_bottom = self.app.window_height

        # Draw borders: left (border-right), center (no border), right (border-left)
        # Left panel border-right
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (left_panel_width, content_top),
            (left_panel_width, content_bottom),
            2,
        )
        # Right panel border-left
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (right_panel_x, content_top),
            (right_panel_x, content_bottom),
            2,
        )

        draw_title(surface, "Simulation", "Run A* / PSO / APSO / HAPSO")

        font = pygame.font.Font(None, FONT_NORMAL)
        for c in self.controls:
            c.draw(surface, font)

        surface.blit(
            font.render(f"Selected: {self.algorithm}", True, PALETTE["accent"]),
            (21, 432),
        )
        status = pygame.font.Font(None, FONT_SMALL).render(
            self.last_status, True, PALETTE["muted"]
        )
        surface.blit(status, (21, 457))

        if self.algorithm == "A*":
            toggle_lines = [
                f"1 Remove redundant points: {self.remove_points}",
                f"2 Remove redundant waypoints: {self.remove_waypoints}",
                f"3 Avoid corner cutting: {self.avoid_corner_cutting}",
                "A* uses 8-direction movement",
            ]
            for idx, line in enumerate(toggle_lines):
                line_surface = pygame.font.Font(None, FONT_SMALL).render(
                    line, True, PALETTE["muted"]
                )
                surface.blit(line_surface, (21, 482 + idx * 24))

        self._draw_grid(surface)
        self._draw_path(surface)
        self._draw_path_info(surface)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        cs = self.app.cell_size
        ox, oy = self.grid_origin
        grid_width = len(self.app.grid[0])
        grid_height = len(self.app.grid)

        for y, row in enumerate(self.app.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(ox + x * cs, oy + y * cs, cs, cs)
                pygame.draw.rect(
                    surface, PALETTE["obstacle"] if cell else (250, 249, 246), rect
                )
                pygame.draw.rect(surface, PALETTE["grid"], rect, 1)

        # Draw X-axis coordinates (0 to grid_width-1, left to right)
        coord_font = pygame.font.Font(None, 16)
        for x in range(grid_width):
            label = coord_font.render(str(x), True, (0, 0, 0))
            x_pos = ox + x * cs + cs // 2 - label.get_width() // 2
            y_pos = oy - 20
            surface.blit(label, (x_pos, y_pos))

        # Draw Y-axis coordinates (grid_height-1 to 0, bottom to top)
        for y in range(grid_height):
            display_y = grid_height - 1 - y  # Flip y-axis so it goes bottom-to-top
            label = coord_font.render(str(display_y), True, (0, 0, 0))
            x_pos = ox - 25
            y_pos = oy + y * cs + cs // 2 - label.get_height() // 2
            surface.blit(label, (x_pos, y_pos))

        if self.app.start:
            self._draw_dot(surface, self.app.start, PALETTE["start"])
        if self.app.goal:
            self._draw_dot(surface, self.app.goal, PALETTE["goal"])

    def _draw_dot(
        self,
        surface: pygame.Surface,
        point: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        cs = self.app.cell_size
        ox, oy = self.grid_origin
        x, y = point
        pygame.draw.circle(
            surface,
            color,
            (ox + x * cs + cs // 2, oy + y * cs + cs // 2),
            max(4, cs // 2 - 2),
        )

    def _draw_path(self, surface: pygame.Surface) -> None:
        if len(self.app.path) < 2:
            return
        cs = self.app.cell_size
        ox, oy = self.grid_origin
        points = [
            (ox + x * cs + cs // 2, oy + y * cs + cs // 2) for x, y in self.app.path
        ]
        pygame.draw.lines(surface, PALETTE["path"], False, points, 3)

    def _run_planner(self) -> None:
        if self.app.start is None or self.app.goal is None:
            self.last_status = "Please set start and goal first"
            return

        planner = self._build_algorithm()
        self.app.path = planner.plan(self.app.grid, self.app.start, self.app.goal)

        if self.app.path:
            self.last_status = f"Found path with {len(self.app.path)} nodes"
            self.path_info = {
                "length": path_length(self.app.path),
                "nodes": node_count(self.app.path),
                "rotation": total_rotation(self.app.path),
                "objective": objective(self.app.path, self.app.grid),
            }
        else:
            self.last_status = "No path found"
            self.path_info = None

    def _save_result(self) -> None:
        if not self.app.path:
            self.last_status = "No path to save"
            return

        saved_dir = save_result_bundle(
            grid=self.app.grid,
            path=self.app.path,
            start=self.app.start,
            goal=self.app.goal,
            algorithm=self.algorithm,
            metrics=self.path_info,
            settings={
                "remove_redundant_points": self.remove_points,
                "remove_redundant_waypoints": self.remove_waypoints,
                "avoid_corner_cutting": self.avoid_corner_cutting,
            },
            cell_size=self.app.cell_size,
        )
        self.last_status = f"Saved result: {saved_dir.name}"

    def _draw_path_info(self, surface: pygame.Surface) -> None:
        font_title = pygame.font.Font(None, FONT_NORMAL)
        font_row = pygame.font.Font(None, FONT_SMALL)

        # Calculate right panel width (30% of window width)
        right_panel_width = int(self.app.window_width * 0.3)
        panel_rect = pygame.Rect(
            self.right_panel_x,
            60,
            right_panel_width,
            self.app.window_height - 60,
        )

        y = panel_rect.y
        x_offset = panel_rect.x + 5  # 5px content padding only
        surface.blit(
            font_title.render("Path Metrics", True, PALETTE["ink"]),
            (x_offset, y),
        )
        y += 28

        if not self.path_info:
            surface.blit(
                font_row.render("No path metrics yet", True, PALETTE["muted"]),
                (x_offset, y),
            )
            return

        rows = [
            f"Length: {self.path_info['length']:.2f}",
            f"Nodes: {self.path_info['nodes']}",
            f"Total rotation(rad): {self.path_info['rotation']:.3f}",
            f"Objective: {self.path_info['objective']:.3f}",
        ]
        for row in rows:
            surface.blit(font_row.render(row, True, PALETTE["muted"]), (x_offset, y))
            y += 30

    def _update_layout(self) -> None:
        # For 3-4-3 layout
        left_panel_width = int(self.app.window_width * 0.3)
        center_panel_width = int(self.app.window_width * 0.4)
        right_panel_x = left_panel_width + center_panel_width
        right_panel_width = self.app.window_width - right_panel_x

        content_top = 40
        content_bottom = self.app.window_height
        panel_height = content_bottom - content_top

        # Calculate grid size in pixels
        grid_px = len(self.app.grid[0]) * self.app.cell_size
        grid_height_px = len(self.app.grid) * self.app.cell_size

        # Account for coordinate display: 25px left for Y-axis, 20px top for X-axis
        total_width_with_coords = grid_px + 25
        total_height_with_coords = grid_height_px + 20

        # Center grid + coordinates within the center panel
        offset_x = (center_panel_width - total_width_with_coords) // 2
        offset_y = (panel_height - total_height_with_coords) // 2

        # grid_origin should account for the 25px left margin and 20px top margin
        grid_origin_x = left_panel_width + offset_x + 25
        grid_origin_y = content_top + offset_y + 20

        self.grid_origin = (grid_origin_x, grid_origin_y)
        self.right_panel_x = right_panel_x + 16  # 16px padding

    def _build_algorithm(self):
        if self.algorithm == "A*":
            return AStarPlanner(
                remove_redundant_points=self.remove_points,
                remove_redundant_waypoints=self.remove_waypoints,
                corner_collision_check=self.avoid_corner_cutting,
            )
        if self.algorithm == "PSO":
            return HybridPlanner(PSOPlanner(), PSOOptimizer())
        if self.algorithm == "APSO":
            return HybridPlanner(AStarPlanner(True, True, False), PSOOptimizer())
        return HybridPlanner(AStarPlanner(True, True, True), PSOOptimizer())
