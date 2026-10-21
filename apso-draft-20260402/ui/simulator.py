import pygame
from typing import List, Optional, Tuple

from algorithms.astar import Astar
from config import (
    COLOR_FREE,
    COLOR_OBSTACLE,
    DEFAULT_GRID_HEIGHT,
    DEFAULT_GRID_WIDTH,
    FONT_NORMAL,
    FONT_SMALL,
    RESULTS_DIR,
    SIMULATION_WINDOW_HEIGHT,
    SIMULATION_WINDOW_WIDTH,
)
from environment.grid_map import GridMap
from ui.grid_editor import GridEditor
from ui.menu import MapMenu, StartMenu
from ui.path_info_window import PathInfoWindow
from utils.message_handler import MessageHandler
from utils.layout_calculator import calculate_layout
from utils.geometry import calculate_angle_metrics
from utils.geometry import calculate_path_metrics
from utils.results_saver import save_all_results
from utils.visualization import draw_grid, draw_path


class PathfindingSimulator:
    def __init__(self):
        pygame.init()
        self.running = True
        self.grid: Optional[GridMap] = None
        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.message_handler = MessageHandler()
        self.simulation_screen: Optional[pygame.Surface] = None
        self.path_metrics: Optional[dict] = None
        self.path_info_window = PathInfoWindow()

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
        print(f"Start: {self.grid.start}, Goal: {self.grid.goal}")
        print(f"{'='*60}")
        print("Controls:")
        print("  SPACE: Run | 1: A* | 2: PSO | 3: APSO")
        print("  S: Save | ESC: Exit")
        print("  C: Toggle prune collinear")
        print("  T: Toggle prune transitions")
        print("  N: Toggle corner cut guard")
        print("  I: Path Info")

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
                    elif event.key == pygame.K_i:
                        self._show_path_info()
                    elif event.key == pygame.K_s:
                        self._save_results()

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
            status_label = font_normal.render("Status:", True, COLOR_OBSTACLE)
            screen.blit(status_label, (layout.right_x, y_offset))
            y_offset += 25

            start_goal_text = font_normal.render(
                f"Start: {self.grid.start}   |   Goal: {self.grid.goal}",
                True,
                COLOR_OBSTACLE,
            )
            screen.blit(start_goal_text, (layout.right_x, y_offset))
            y_offset += 40
            instr_label = font_normal.render("Controls:", True, COLOR_OBSTACLE)
            screen.blit(instr_label, (layout.right_x, y_offset))
            y_offset += 25

            instructions = [
                "SPACE: Run | 1: A* | 2: PSO | 3: APSO",
                "S: Save | ESC: Exit",
                "C: Toggle prune collinear",
                "T: Toggle prune transitions",
                "N: Toggle corner cut guard",
                "I: Path Info",
            ]
            instr_font = pygame.font.Font(None, FONT_NORMAL)
            for instr in instructions:
                instr_text = instr_font.render(instr, True, COLOR_OBSTACLE)
                screen.blit(instr_text, (layout.right_x, y_offset))
                y_offset += 18

            pygame.display.flip()
            clock.tick(60)

    def _find_path(self):
        if self.grid is None or self.grid.start is None or self.grid.goal is None:
            self.message_handler.set_message("Invalid start or goal")
            return

        print(f"\nFinding path...")

        try:
            # Use A* algorithm for pathfinding
            astar = Astar(
                self.grid,
                prune_collinear=False,
                prune_transitions=False,
                avoid_corner_cutting=False,
            )
            self.current_path = astar.plan()

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

    def _show_path_info(self):
        """Show detailed path information in a separate window."""
        if self.grid is None or self.current_path is None:
            self.message_handler.set_message("No path to display")
            print("No path found - cannot display path info")
            return

        print(f"\nShowing path information...")

        # Calculate angle metrics for the current path
        angle_metrics = calculate_angle_metrics(self.current_path)

        # Update path info window with current data
        self.path_info_window.set_data(
            self.grid, self.current_path, self.path_metrics, angle_metrics
        )

        # Run path info window (blocking)
        self.path_info_window.run()

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
            "Simulator",
        )

        if success:
            self.message_handler.set_message(
                f"Results saved to: data/results/<timestamp>"
            )
            print(f"Results successfully saved!")
        else:
            self.message_handler.set_message("Failed to save results")
            print(f"Failed to save results")
