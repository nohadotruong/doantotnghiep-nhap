import pygame
from typing import List, Optional, Tuple

from algorithms.astar import Astar
from algorithms.pso import PSOPlanner
from config import (
    COLOR_FREE,
    COLOR_OBSTACLE,
    DEFAULT_GRID_HEIGHT,
    DEFAULT_GRID_WIDTH,
    FONT_NORMAL,
    RESULTS_DIR,
    SIMULATION_WINDOW_HEIGHT,
    SIMULATION_WINDOW_WIDTH,
)
from environment.grid_map import GridMap
from gui.grid_editor import GridEditor
from gui.menu import MapMenu, StartMenu
from utils.message_handler import MessageHandler
from utils.layout_calculator import calculate_layout
from utils.geometry import calculate_path_metrics
from utils.results_saver import save_all_results
from utils.visualization import draw_grid, draw_path


class PathfindingSimulator:
    def __init__(self):
        pygame.init()
        self.running = True
        self.grid: Optional[GridMap] = None
        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.current_algorithm = 1  # 1: A*, 2: PSO
        self.algorithm_name = "A* (Grid)"
        self.message_handler = MessageHandler()
        self.simulation_screen: Optional[pygame.Surface] = None
        self.path_metrics: Optional[dict] = None

    def run(self):
        while self.running:
            start_menu = StartMenu()
            choice = start_menu.run()

            if choice is None:
                print("Exiting application...")
                self.running = False
                break

            if choice == "new":
                print("Creating new map...")
                self._create_new_map()
            else:
                print("Loading map...")
                if not self._load_map():
                    continue

            if not self.running or self.grid is None:
                break

            if not self._edit_map():
                continue

            self._run_simulation()

        pygame.quit()
        print("Application closed.")

    def _create_new_map(self):
        self.grid = GridMap(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)

    def _load_map(self) -> bool:
        map_menu = MapMenu()
        map_path = map_menu.run()

        if map_path is None:
            print("Map loading cancelled.")
            return False

        self.grid = GridMap.load_from_path(map_path)
        if self.grid is None:
            print(f"Failed to load map from {map_path}")
            return False

        print(f"Map loaded successfully!")
        return True

    def _edit_map(self):
        if self.grid is None:
            self.grid = GridMap(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)

        print("Opening grid editor...\nInstructions:")
        print("  - Click to toggle obstacles")
        print("  - Drag to draw obstacle lines")
        print("  - S: Set start position")
        print("  - G: Set goal position")
        print("  - ENTER or SPACE: Save and run simulation")
        print("  - C: Clear map")
        print("  - ESC: Return to menu")

        editor = GridEditor(self.grid)
        proceed_to_simulation = editor.run()

        if not proceed_to_simulation:
            print("Returning to menu...")
            return False

        print("Map ready! Starting simulation...")
        return True

    def _run_simulation(self):
        if self.grid is None or self.grid.start is None or self.grid.goal is None:
            print("Invalid grid. Returning to map creation.")
            return

        layout = calculate_layout(
            self.grid.width,
            self.grid.height,
            SIMULATION_WINDOW_WIDTH,
            SIMULATION_WINDOW_HEIGHT,
        )
        screen = pygame.display.set_mode((layout.window_width, layout.window_height))
        pygame.display.set_caption("Pathfinding Simulator")
        clock = pygame.time.Clock()
        font_normal = pygame.font.Font(None, FONT_NORMAL)

        self.simulation_screen = screen
        self.current_path = None
        self.path_metrics = None
        running = True

        print(f"\n{'='*60}")
        print(f"Algorithm: {self.algorithm_name}")
        print(f"Start: {self.grid.start}, Goal: {self.grid.goal}")
        print(f"{'='*60}")
        print("Controls:")
        print("  SPACE: Run algorithm")
        print("  1: A* |  2: PSO")
        print("  S: Save results | R: Create new map | ESC: Exit")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._find_path()
                    elif event.key == pygame.K_1:
                        self.current_algorithm = 1
                        self.algorithm_name = "A* (Grid)"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message(
                            "Algorithm switched to A* (Grid)"
                        )
                        print("\nAlgorithm switched to A* (Grid)")
                    elif event.key == pygame.K_2:
                        self.current_algorithm = 2
                        self.algorithm_name = "PSO (Grid)"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message(
                            "Algorithm switched to PSO (Grid)"
                        )
                        print("\nAlgorithm switched to PSO (Grid)")
                    elif event.key == pygame.K_s:
                        self._save_results()
                    elif event.key == pygame.K_r:
                        print("\nCreating new map...")
                        running = False

            screen.fill(COLOR_FREE)
            draw_grid(screen, self.grid, layout.left_x, layout.left_y)
            if self.current_path:
                draw_path(
                    screen, self.current_path, layout.left_x, layout.left_y, thickness=3
                )
            y_offset = layout.right_y
            message = self.message_handler.get_message()
            if message:
                msg_surface = font_normal.render(message, True, COLOR_OBSTACLE)
                screen.blit(msg_surface, (layout.right_x, y_offset))
                y_offset += 30
            y_offset += 10
            algo_label = font_normal.render("Algorithm:", True, COLOR_OBSTACLE)
            screen.blit(algo_label, (layout.right_x, y_offset))
            y_offset += 25
            algo_name = font_normal.render(self.algorithm_name, True, COLOR_OBSTACLE)
            screen.blit(algo_name, (layout.right_x, y_offset))
            y_offset += 40
            status_label = font_normal.render("Status:", True, COLOR_OBSTACLE)
            screen.blit(status_label, (layout.right_x, y_offset))
            y_offset += 25

            start_text = font_normal.render(
                f"Start: {self.grid.start}", True, COLOR_OBSTACLE
            )
            screen.blit(start_text, (layout.right_x, y_offset))
            y_offset += 25

            goal_text = font_normal.render(
                f"Goal: {self.grid.goal}", True, COLOR_OBSTACLE
            )
            screen.blit(goal_text, (layout.right_x, y_offset))
            y_offset += 40
            path_label = font_normal.render("Path Info:", True, COLOR_OBSTACLE)
            screen.blit(path_label, (layout.right_x, y_offset))
            y_offset += 25

            if self.current_path and self.path_metrics:
                length_text = font_normal.render(
                    f"Length: {self.path_metrics['length']:.1f}", True, COLOR_OBSTACLE
                )
                screen.blit(length_text, (layout.right_x, y_offset))
                y_offset += 20
                waypoint_text = font_normal.render(
                    f"Waypoints: {self.path_metrics['waypoint_count']}",
                    True,
                    COLOR_OBSTACLE,
                )
                screen.blit(waypoint_text, (layout.right_x, y_offset))
                y_offset += 20
            else:
                no_path_text = font_normal.render("No path yet", True, COLOR_OBSTACLE)
                screen.blit(no_path_text, (layout.right_x, y_offset))
            y_offset += 40
            instr_label = font_normal.render("Controls:", True, COLOR_OBSTACLE)
            screen.blit(instr_label, (layout.right_x, y_offset))
            y_offset += 25

            instructions = [
                "SPACE: Run | 1-2: Select Algorithm",
                "1: A* (Grid) | 2: PSO (Grid)",
                "S: Save | R: New Map | ESC: Exit",
            ]
            for instr in instructions:
                instr_text = font_normal.render(instr, True, COLOR_OBSTACLE)
                screen.blit(instr_text, (layout.right_x, y_offset))
                y_offset += 20

            pygame.display.flip()
            clock.tick(60)

    def _find_path(self):
        if self.grid is None or self.grid.start is None or self.grid.goal is None:
            self.message_handler.set_message("Invalid start or goal")
            return

        print(f"\nFinding path using {self.algorithm_name}...")

        try:
            if self.current_algorithm == 1:
                # A* (Grid-based)
                astar = Astar(self.grid)
                self.current_path = astar.plan()
            elif self.current_algorithm == 2:
                # PSO (Grid-based)
                pso = PSOPlanner(self.grid, num_waypoints=20)
                self.current_path = pso.plan()

            if self.current_path:
                self.path_metrics = calculate_path_metrics(self.grid, self.current_path)
                print(f"Path found! Length: {self.path_metrics['length']:.1f}")
                self.message_handler.set_message(
                    f"Path found! Length: {self.path_metrics['length']:.1f}"
                )
            else:
                print(f"No path found")
                self.message_handler.set_message("No path found!")
                self.path_metrics = None
        except Exception as e:
            print(f"Error during pathfinding: {e}")
            self.message_handler.set_message(f"Error: {str(e)[:50]}")
            self.path_metrics = None

    def _save_results(self):
        if self.grid is None or self.simulation_screen is None:
            self.message_handler.set_message("Cannot save - no simulation active")
            print("Cannot save results - no simulation active")
            return

        print(f"\nSaving results...")
        success, results_dir = save_all_results(
            self.simulation_screen,
            RESULTS_DIR,
            self.grid,
            self.current_path,
            self.algorithm_name,
        )

        if success:
            self.message_handler.set_message(f"Results saved to: results/<timestamp>")
            print(f"Results successfully saved!")
        else:
            self.message_handler.set_message("Failed to save results")
            print(f"Failed to save results")
