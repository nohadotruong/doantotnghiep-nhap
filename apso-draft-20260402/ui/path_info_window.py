"""
Path Information Window - Display path details and metrics with 2-column layout.
"""

import pygame
from typing import List, Optional, Tuple
from config import (
    CELL_SIZE,
    COLOR_FREE,
    COLOR_GOAL,
    COLOR_GRID,
    COLOR_OBSTACLE,
    COLOR_PATH,
    COLOR_START,
    FONT_NORMAL,
    FONT_SMALL,
    SIMULATION_WINDOW_WIDTH,
    SIMULATION_WINDOW_HEIGHT,
)
from environment.grid_map import GridMap
from utils.visualization import draw_grid, draw_path
from utils.layout_calculator import calculate_layout


class PathInfoWindow:
    """Display detailed path information in a separate window with 2-column layout."""

    def __init__(self):
        self.window_width = SIMULATION_WINDOW_WIDTH
        self.window_height = SIMULATION_WINDOW_HEIGHT
        self.margin = 15

        self.font_normal = pygame.font.Font(None, FONT_NORMAL)
        self.font_small = pygame.font.Font(None, FONT_SMALL)

        self.grid: Optional[GridMap] = None
        self.path: Optional[List[Tuple[int, int]]] = None
        self.metrics: Optional[dict] = None
        self.angle_metrics: Optional[dict] = None

        self.layout = None

    def set_data(
        self,
        grid: GridMap,
        path: Optional[List[Tuple[int, int]]],
        metrics: Optional[dict] = None,
        angle_metrics: Optional[dict] = None,
    ):
        """Update path data for display."""
        self.grid = grid
        self.path = path
        self.metrics = metrics
        self.angle_metrics = angle_metrics

        # Calculate layout (55% left for grid, 45% right for info)
        if grid:
            self.layout = calculate_layout(
                grid.width,
                grid.height,
                self.window_width,
                self.window_height,
                margin=self.margin,
                axes_margin=30,
                left_ratio=0.55,
            )

    def run(self):
        """Display path info window (blocking)."""
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Path Information")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return True

            self._draw_window(screen)
            pygame.display.flip()
            clock.tick(60)

        return True

    def _draw_window(self, screen: pygame.Surface):
        """Draw the path info window with 2-column layout."""
        screen.fill((255, 255, 255))

        # Draw title
        title = self.font_normal.render("Path Information", True, (0, 0, 0))
        screen.blit(title, (self.margin, self.margin))

        # Draw divider line below title
        title_bottom = self.margin + 30
        pygame.draw.line(
            screen,
            (200, 200, 200),
            (self.margin, title_bottom),
            (self.window_width - self.margin, title_bottom),
            2,
        )

        if self.grid and self.layout:
            # LEFT COLUMN: Grid visualization with path
            self._draw_left_column(screen)

            # RIGHT COLUMN: Path metrics
            self._draw_right_column(screen)

        # Draw footer instruction
        footer_y = self.window_height - 25
        instr = self.font_small.render(
            "ESC: Close window  |  View detailed pathfinding analysis",
            True,
            (100, 100, 100),
        )
        screen.blit(instr, (self.margin, footer_y))

    def _draw_left_column(self, screen: pygame.Surface):
        """Draw grid visualization on the left side."""
        if not self.grid or not self.layout:
            return

        # Draw grid with proper scaling
        draw_grid(screen, self.grid, self.layout.left_x, self.layout.left_y, CELL_SIZE)

        # Draw path if available
        if self.path and len(self.path) > 0:
            draw_path(
                screen,
                self.path,
                self.layout.left_x,
                self.layout.left_y,
                thickness=2,
            )

    def _draw_right_column(self, screen: pygame.Surface):
        """Draw metrics and analysis on the right side."""
        if not self.layout:
            return

        right_x = self.layout.right_x
        y = self.layout.right_y + 10

        # PATH METRICS SECTION
        self._draw_metrics_section(screen, right_x, y)
        y += 180

        # ANGLE METRICS SECTION
        self._draw_angle_section(screen, right_x, y)

    def _draw_metrics_section(self, screen: pygame.Surface, x: int, y: int):
        """Draw path metrics section."""
        # Section title
        title = self.font_normal.render("📊 PATH METRICS", True, (0, 100, 200))
        screen.blit(title, (x, y))
        y += 30

        # Divider
        pygame.draw.line(screen, (200, 200, 200), (x, y), (x + 180, y), 1)
        y += 10

        if not self.path:
            text = self.font_small.render("No path available", True, (150, 150, 150))
            screen.blit(text, (x, y))
            return

        # Waypoints
        text = self.font_small.render(f"Waypoints: {len(self.path)}", True, (0, 0, 0))
        screen.blit(text, (x, y))
        y += 20

        # Path length
        if self.metrics and "length" in self.metrics:
            length = self.metrics["length"]
            text = self.font_small.render(f"Path Length: {length:.2f}", True, (0, 0, 0))
        else:
            text = self.font_small.render("Path Length: N/A", True, (150, 150, 150))
        screen.blit(text, (x, y))
        y += 20

        # Smoothness
        if self.metrics and "smoothness" in self.metrics:
            smoothness = self.metrics["smoothness"]
            text = self.font_small.render(
                f"Smoothness: {smoothness:.4f}", True, (0, 0, 0)
            )
        else:
            text = self.font_small.render("Smoothness: N/A", True, (150, 150, 150))
        screen.blit(text, (x, y))
        y += 20

        # Collision status
        if self.metrics and "has_collision" in self.metrics:
            collision = (
                "Yes (WARNING)" if self.metrics["has_collision"] else "No (Clear)"
            )
            color = (200, 0, 0) if self.metrics["has_collision"] else (0, 150, 0)
            text = self.font_small.render(f"Collision: {collision}", True, color)
        else:
            text = self.font_small.render("Collision: N/A", True, (150, 150, 150))
        screen.blit(text, (x, y))

    def _draw_angle_section(self, screen: pygame.Surface, x: int, y: int):
        """Draw angle metrics section."""
        # Section title
        title = self.font_normal.render("📐 ANGLE METRICS", True, (200, 100, 0))
        screen.blit(title, (x, y))
        y += 30

        # Divider
        pygame.draw.line(screen, (200, 200, 200), (x, y), (x + 180, y), 1)
        y += 10

        if not self.path or len(self.path) < 3:
            text = self.font_small.render(
                "Less than 3 waypoints", True, (150, 150, 150)
            )
            screen.blit(text, (x, y))
            return

        # Max turning angle
        if self.angle_metrics and "max_angle" in self.angle_metrics:
            max_angle = self.angle_metrics["max_angle"]
            text = self.font_small.render(
                f"Max Turning Angle: {max_angle:.2f}°", True, (0, 0, 0)
            )
        else:
            text = self.font_small.render(
                "Max Turning Angle: N/A", True, (150, 150, 150)
            )
        screen.blit(text, (x, y))
        y += 20

        # Average turning angle
        if self.angle_metrics and "avg_angle" in self.angle_metrics:
            avg_angle = self.angle_metrics["avg_angle"]
            text = self.font_small.render(
                f"Avg Turning Angle: {avg_angle:.2f}°", True, (0, 0, 0)
            )
        else:
            text = self.font_small.render(
                "Avg Turning Angle: N/A", True, (150, 150, 150)
            )
        screen.blit(text, (x, y))
        y += 20

        # Total angle change
        if self.angle_metrics and "total_angle" in self.angle_metrics:
            total_angle = self.angle_metrics["total_angle"]
            text = self.font_small.render(
                f"Total Angle Change: {total_angle:.2f}°", True, (0, 0, 0)
            )
        else:
            text = self.font_small.render(
                "Total Angle Change: N/A", True, (150, 150, 150)
            )
        screen.blit(text, (x, y))
