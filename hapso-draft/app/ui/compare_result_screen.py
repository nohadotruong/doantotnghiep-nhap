"""
Compare Results Screen (F4) - Multi-algorithm comparison.

This screen:
- Runs all four algorithms (A*, PSO, APSO, HAPSO) on the current map
- Displays results in a comparison table
- Shows metrics for each algorithm
- Highlights the best result

Uses planning.api.run_experiment() as the interface to run all algorithms.
"""

import time
from typing import Optional, Dict, List
import pygame

import planning.api as plan_api
from app.state import AppState


class CompareResultScreen:
    """Compare results from all pathfinding algorithms."""

    def __init__(self, state: AppState):
        """Initialize compare result screen."""
        self.state = state
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_large = pygame.font.Font(None, 32)

        self.running = True
        self.is_running_experiment = False
        self.experiment_result: Optional[plan_api.ExperimentResult] = None

        # UI colors
        self.COLOR_BACKGROUND = (240, 240, 240)
        self.COLOR_TABLE_HEADER = (100, 100, 200)
        self.COLOR_TABLE_ROW = (200, 200, 200)
        self.COLOR_TABLE_BEST = (100, 255, 100)
        self.COLOR_TEXT = (0, 0, 0)
        self.COLOR_TEXT_LIGHT = (255, 255, 255)

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle keyboard events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

            # Run experiment
            elif event.key == pygame.K_SPACE:
                self._run_experiment()

    def update(self) -> None:
        """Update screen state."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw compare result screen."""
        screen.fill(self.COLOR_BACKGROUND)

        title = self.font_large.render("Algorithm Comparison", True, self.COLOR_TEXT)
        screen.blit(title, (20, 20))

        if self.is_running_experiment:
            status = self.font_normal.render(
                "Running experiment...", True, (255, 100, 100)
            )
            screen.blit(status, (20, 70))

        if self.experiment_result:
            self._draw_results_table(screen, 20, 80, screen.get_width() - 40)
        else:
            instruction = self.font_normal.render(
                "Press SPACE to run comparison", True, self.COLOR_TEXT
            )
            screen.blit(instruction, (20, 100))

    def _run_experiment(self) -> None:
        """Run all algorithms and store results."""
        if not self.state.start or not self.state.goal:
            return

        try:
            self.is_running_experiment = True

            # Convert app state to planning API types
            grid = plan_api.Grid(
                width=self.state.grid_width,
                height=self.state.grid_height,
                obstacles=list(self.state.obstacles),
            )
            start = plan_api.Point(x=self.state.start[0], y=self.state.start[1])
            goal = plan_api.Point(x=self.state.goal[0], y=self.state.goal[1])

            # Create experiment config
            config = plan_api.ExperimentConfig(
                grid=grid,
                start=start,
                goal=goal,
                run_astar=True,
                run_pso=True,
                run_apso=True,
                run_hapso=True,
                astar_prune_collinear=self.state.astar_prune_collinear,
                astar_prune_transitions=self.state.astar_prune_transitions,
                astar_avoid_corner_cutting=self.state.astar_avoid_corner_cutting,
                pso_particles=self.state.pso_particles,
                pso_iterations=self.state.pso_iterations,
            )

            # Run experiment via planning API
            self.experiment_result = plan_api.run_experiment(config)

            # Store results in state for later use
            self.state.experiment_results = {}
            for algo_name, plan_result in self.experiment_result.results.items():
                if plan_result.success:
                    self.state.experiment_results[algo_name] = {
                        "path_length": plan_result.metrics.path_length,
                        "waypoints": plan_result.metrics.waypoint_count,
                        "computation_time": plan_result.metrics.computation_time,
                        "rotation": plan_result.metrics.total_rotation,
                        "found": True,
                    }
                else:
                    self.state.experiment_results[algo_name] = {
                        "found": False,
                        "error": plan_result.error_message,
                    }

            self.is_running_experiment = False

        except Exception as e:
            self.is_running_experiment = False

    def _draw_results_table(
        self, screen: pygame.Surface, x: int, y: int, width: int
    ) -> None:
        """Draw results comparison table."""
        if not self.experiment_result:
            return

        col_width = width / 5
        row_height = 30

        # Header
        headers = ["Algorithm", "Path Length", "Waypoints", "Time (s)", "Status"]
        for i, header in enumerate(headers):
            text = self.font_small.render(header, True, self.COLOR_TEXT_LIGHT)
            pygame.draw.rect(
                screen,
                self.COLOR_TABLE_HEADER,
                (x + i * col_width, y, col_width, row_height),
            )
            text_rect = text.get_rect(
                center=(x + i * col_width + col_width / 2, y + row_height / 2)
            )
            screen.blit(text, text_rect)

        # Rows
        row_y = y + row_height
        best_algo = self.experiment_result.best_algorithm

        for algo_name, plan_result in sorted(self.experiment_result.results.items()):
            row_color = (
                self.COLOR_TABLE_BEST
                if algo_name == best_algo
                else self.COLOR_TABLE_ROW
            )

            pygame.draw.rect(screen, row_color, (x, row_y, width, row_height))
            pygame.draw.rect(screen, self.COLOR_TEXT, (x, row_y, width, row_height), 1)

            # Algorithm name
            text = self.font_small.render(algo_name, True, self.COLOR_TEXT)
            screen.blit(text, (x + 5, row_y + 5))

            if plan_result.success and plan_result.metrics:
                # Path length
                length_text = f"{plan_result.metrics.path_length:.2f}"
                text = self.font_small.render(length_text, True, self.COLOR_TEXT)
                text_rect = text.get_rect(
                    center=(x + col_width * 1.5, row_y + row_height / 2)
                )
                screen.blit(text, text_rect)

                # Waypoints
                wp_text = str(plan_result.metrics.waypoint_count)
                text = self.font_small.render(wp_text, True, self.COLOR_TEXT)
                text_rect = text.get_rect(
                    center=(x + col_width * 2.5, row_y + row_height / 2)
                )
                screen.blit(text, text_rect)

                # Time
                time_text = f"{plan_result.metrics.computation_time:.3f}"
                text = self.font_small.render(time_text, True, self.COLOR_TEXT)
                text_rect = text.get_rect(
                    center=(x + col_width * 3.5, row_y + row_height / 2)
                )
                screen.blit(text, text_rect)

                # Status
                status_text = "✓ Found"
                text = self.font_small.render(status_text, True, (0, 200, 0))
                text_rect = text.get_rect(
                    center=(x + col_width * 4.5, row_y + row_height / 2)
                )
                screen.blit(text, text_rect)
            else:
                # Failed
                status_text = "✗ Failed"
                text = self.font_small.render(status_text, True, (255, 0, 0))
                text_rect = text.get_rect(
                    center=(x + col_width * 4.5, row_y + row_height / 2)
                )
                screen.blit(text, text_rect)

            row_y += row_height

        # Best result info
        if best_algo:
            info_y = row_y + 20
            best_text = (
                f"Best: {best_algo} ({self.experiment_result.best_path_length:.2f})"
            )
            text = self.font_normal.render(best_text, True, (0, 150, 0))
            screen.blit(text, (x, info_y))


__all__ = ["CompareResultScreen"]
