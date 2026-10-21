"""
Simulation Screen (F2) - Interactive path planning simulator.

This screen allows the user to:
- Select and run different path planning algorithms (A*, PSO, APSO, HAPSO)
- View the planned path on the grid
- Configure algorithm parameters
- Save results

The screen uses planning.api.run_plan() as the single interface to algorithms.
"""

import time
from typing import Optional, Dict
import pygame

import planning.api as plan_api
from app.state import AppState
from app.io.result_io import save_result_bundle


class SimulationScreen:
    """Interactive pathfinding simulator with algorithm comparison."""

    def __init__(self, state: AppState):
        """Initialize simulation screen."""
        self.state = state
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_large = pygame.font.Font(None, 32)

        self.running = True
        self.selected_algorithm = "HAPSO"
        self.algorithm_options = ["ASTAR", "PSO", "APSO", "HAPSO"]

        # UI colors
        self.COLOR_BACKGROUND = (240, 240, 240)
        self.COLOR_GRID_LINE = (200, 200, 200)
        self.COLOR_FREE = (255, 255, 255)
        self.COLOR_OBSTACLE = (0, 0, 0)
        self.COLOR_START = (0, 255, 0)
        self.COLOR_GOAL = (255, 0, 0)
        self.COLOR_PATH = (0, 0, 255)
        self.COLOR_TEXT = (0, 0, 0)
        self.COLOR_ERROR = (255, 100, 100)

    def handle_event(self, event: pygame.event.EventType) -> None:
        """Handle keyboard/mouse events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

            # Algorithm selection (1-4)
            elif event.key == pygame.K_1:
                self.selected_algorithm = "ASTAR"
                self.state.set_message("Selected: A*", time.time())
            elif event.key == pygame.K_2:
                self.selected_algorithm = "PSO"
                self.state.set_message("Selected: PSO", time.time())
            elif event.key == pygame.K_3:
                self.selected_algorithm = "APSO"
                self.state.set_message("Selected: APSO", time.time())
            elif event.key == pygame.K_4:
                self.selected_algorithm = "HAPSO"
                self.state.set_message("Selected: HAPSO", time.time())

            # Toggle A* options
            elif event.key == pygame.K_c:
                self.state.astar_prune_collinear = not self.state.astar_prune_collinear
                msg = (
                    "Remove collinear: ON"
                    if self.state.astar_prune_collinear
                    else "Remove collinear: OFF"
                )
                self.state.set_message(msg, time.time())

            elif event.key == pygame.K_t:
                self.state.astar_prune_transitions = (
                    not self.state.astar_prune_transitions
                )
                msg = (
                    "Smooth path: ON"
                    if self.state.astar_prune_transitions
                    else "Smooth path: OFF"
                )
                self.state.set_message(msg, time.time())

            elif event.key == pygame.K_n:
                self.state.astar_avoid_corner_cutting = (
                    not self.state.astar_avoid_corner_cutting
                )
                msg = (
                    "Corner guard: ON"
                    if self.state.astar_avoid_corner_cutting
                    else "Corner guard: OFF"
                )
                self.state.set_message(msg, time.time())

            # Run planning
            elif event.key == pygame.K_SPACE:
                self._run_planning()

            # Save results
            elif event.key == pygame.K_s:
                if self.state.path and not self.state.last_error:
                    try:
                        # Create a PlanResult from current state
                        result = plan_api.PlanResult(
                            success=True,
                            path=[
                                plan_api.Point(x=p[0], y=p[1]) for p in self.state.path
                            ],
                            metrics=self._get_current_metrics(),
                        )
                        save_result_bundle(result, self.state, "data/results")
                        self.state.set_message("Results saved", time.time())
                    except Exception as e:
                        self.state.set_message(f"Save failed: {str(e)}", time.time())
                else:
                    self.state.set_message("No valid path to save", time.time())

    def update(self) -> None:
        """Update screen state."""
        # Message auto-clear after 3 seconds
        if self.state.last_message:
            if (time.time() - self.state.message_timestamp) > 3.0:
                self.state.last_message = ""

    def draw(self, screen: pygame.Surface) -> None:
        """Draw simulation screen."""
        screen.fill(self.COLOR_BACKGROUND)

        # Calculate layout
        panel_width = 250
        grid_area_width = screen.get_width() - panel_width

        # Draw grid area
        self._draw_grid(screen, 0, 0, grid_area_width, screen.get_height())

        # Draw control panel
        self._draw_panel(screen, grid_area_width, 0, panel_width, screen.get_height())

        # Draw message
        message = self.state.get_message()
        if message:
            text = self.font_small.render(message, True, self.COLOR_TEXT)
            screen.blit(text, (10, screen.get_height() - 30))

    def _run_planning(self) -> None:
        """Execute path planning with current algorithm."""
        if not self.state.start or not self.state.goal:
            self.state.set_message("Set start (S) and goal (G) first", time.time())
            self.state.last_error = "Start/goal not set"
            return

        try:
            self.state.reset_metrics()

            # Convert app state to planning API types
            grid = plan_api.Grid(
                width=self.state.grid_width,
                height=self.state.grid_height,
                obstacles=list(self.state.obstacles),
            )
            start = plan_api.Point(x=self.state.start[0], y=self.state.start[1])
            goal = plan_api.Point(x=self.state.goal[0], y=self.state.goal[1])

            # Create plan request
            algorithm_map = {
                "ASTAR": plan_api.AlgorithmType.ASTAR,
                "PSO": plan_api.AlgorithmType.PSO,
                "APSO": plan_api.AlgorithmType.APSO,
                "HAPSO": plan_api.AlgorithmType.HAPSO,
            }

            request = plan_api.PlanRequest(
                grid=grid,
                start=start,
                goal=goal,
                algorithm=algorithm_map[self.selected_algorithm],
                astar_prune_collinear=self.state.astar_prune_collinear,
                astar_prune_transitions=self.state.astar_prune_transitions,
                astar_avoid_corner_cutting=self.state.astar_avoid_corner_cutting,
                pso_particles=self.state.pso_particles,
                pso_iterations=self.state.pso_iterations,
                pso_cognitive_coeff=self.state.pso_cognitive_coeff,
                pso_social_coeff=self.state.pso_social_coeff,
                pso_max_velocity=self.state.pso_max_velocity,
            )

            # Run planning via planning API
            result = plan_api.run_plan(request)

            if result.success:
                # Convert result path to tuples
                self.state.path = [(p.x, p.y) for p in result.path]
                self.state.last_error = None

                # Store metrics
                if result.metrics:
                    self.state.last_path_length = result.metrics.path_length
                    self.state.last_waypoint_count = result.metrics.waypoint_count
                    self.state.last_computation_time = result.metrics.computation_time
                    self.state.last_total_rotation = result.metrics.total_rotation

                msg = f"Path found: {len(self.state.path)} waypoints, length={self.state.last_path_length:.2f}"
                self.state.set_message(msg, time.time())
            else:
                self.state.path = []
                self.state.last_error = result.error_message
                self.state.set_message(
                    f"Planning failed: {result.error_message}", time.time()
                )

        except Exception as e:
            self.state.last_error = str(e)
            self.state.set_message(f"Error: {str(e)}", time.time())

    def _get_current_metrics(self) -> plan_api.Metrics:
        """Get metrics from current state."""
        return plan_api.Metrics(
            path_length=self.state.last_path_length or 0,
            waypoint_count=self.state.last_waypoint_count or 0,
            total_rotation=self.state.last_total_rotation or 0,
            computation_time=self.state.last_computation_time or 0,
            path_valid=True,
            objective_value=0,
            turn_angles=[],
        )

    def _draw_grid(
        self, screen: pygame.Surface, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw grid representation."""
        cell_w = width // self.state.grid_width
        cell_h = height // self.state.grid_height

        # Draw cells
        for row in range(self.state.grid_height):
            for col in range(self.state.grid_width):
                px = x + col * cell_w
                py = y + row * cell_h

                # Determine cell color
                if (col, row) == self.state.start:
                    color = self.COLOR_START
                elif (col, row) == self.state.goal:
                    color = self.COLOR_GOAL
                elif (col, row) in self.state.obstacles:
                    color = self.COLOR_OBSTACLE
                elif (col, row) in self.state.path:
                    color = self.COLOR_PATH
                else:
                    color = self.COLOR_FREE

                pygame.draw.rect(screen, color, (px, py, cell_w, cell_h))
                pygame.draw.rect(
                    screen, self.COLOR_GRID_LINE, (px, py, cell_w, cell_h), 1
                )

    def _draw_panel(
        self, screen: pygame.Surface, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw control panel."""
        # Panel background
        pygame.draw.rect(screen, (220, 220, 220), (x, y, width, height))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 2)

        # Title
        title = self.font_large.render("Controls", True, self.COLOR_TEXT)
        screen.blit(title, (x + 10, y + 10))

        py = y + 50

        # Algorithm selection
        algo_text = self.font_normal.render("Algorithm:", True, self.COLOR_TEXT)
        screen.blit(algo_text, (x + 10, py))
        py += 25

        for i, algo in enumerate(self.algorithm_options):
            color = (0, 200, 0) if algo == self.selected_algorithm else self.COLOR_TEXT
            text = self.font_small.render(f"{i+1}: {algo}", True, color)
            screen.blit(text, (x + 15, py))
            py += 20

        py += 10

        # A* options
        options_text = self.font_normal.render("A* Options:", True, self.COLOR_TEXT)
        screen.blit(options_text, (x + 10, py))
        py += 25

        col_text = "C: Remove collinear " + (
            "ON" if self.state.astar_prune_collinear else "OFF"
        )
        text = self.font_small.render(col_text, True, self.COLOR_TEXT)
        screen.blit(text, (x + 15, py))
        py += 20

        smo_text = "T: Smooth path " + (
            "ON" if self.state.astar_prune_transitions else "OFF"
        )
        text = self.font_small.render(smo_text, True, self.COLOR_TEXT)
        screen.blit(text, (x + 15, py))
        py += 20

        cor_text = "N: Corner guard " + (
            "ON" if self.state.astar_avoid_corner_cutting else "OFF"
        )
        text = self.font_small.render(cor_text, True, self.COLOR_TEXT)
        screen.blit(text, (x + 15, py))
        py += 20

        py += 10

        # Run button info
        run_text = self.font_normal.render("Run:", True, self.COLOR_TEXT)
        screen.blit(run_text, (x + 10, py))
        py += 25

        space_text = self.font_small.render(
            "SPACE: Run path planning", True, self.COLOR_TEXT
        )
        screen.blit(space_text, (x + 15, py))
        py += 20

        save_text = self.font_small.render("S: Save results", True, self.COLOR_TEXT)
        screen.blit(save_text, (x + 15, py))
        py += 20

        esc_text = self.font_small.render("ESC: Back to menu", True, self.COLOR_TEXT)
        screen.blit(esc_text, (x + 15, py))

        # Display metrics
        if self.state.last_path_length is not None:
            py = y + height - 120
            metrics_text = self.font_normal.render(
                "Last Result:", True, self.COLOR_TEXT
            )
            screen.blit(metrics_text, (x + 10, py))
            py += 25

            length_text = f"Length: {self.state.last_path_length:.2f}"
            text = self.font_small.render(length_text, True, self.COLOR_TEXT)
            screen.blit(text, (x + 15, py))
            py += 20

            wp_text = f"Waypoints: {self.state.last_waypoint_count}"
            text = self.font_small.render(wp_text, True, self.COLOR_TEXT)
            screen.blit(text, (x + 15, py))
            py += 20

            time_text = f"Time: {self.state.last_computation_time:.3f}s"
            text = self.font_small.render(time_text, True, self.COLOR_TEXT)
            screen.blit(text, (x + 15, py))


__all__ = ["SimulationScreen"]
