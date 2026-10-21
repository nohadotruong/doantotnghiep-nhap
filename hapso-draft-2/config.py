WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 680
FPS = 60
WINDOW_TITLE = "HAPSO Simulation"
FULLSCREEN = False
CENTER_WINDOW = True
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_GRAY = (240, 240, 240)
COLOR_DARK_GRAY = (50, 50, 50)
NAV_HEIGHT = 40
SEPARATOR_HEIGHT = 2
VERTICAL_SEPARATOR_WIDTH = 2
CONTENT_LEFT_RATIO = 0.25
CONTENT_RIGHT_RATIO = 0.75
FONT_SIZE_DEFAULT = 24
FONT_SIZE_SMALL = 18
F1_MENU_ITEMS = [
    "1: Obstacle",
    "2: Ecrease",
    "S: Start",
    "G: Goal",
    "Enter: Save",
    "L: Load",
    "C: Clear",
]
F2_MENU_ITEMS = [
    "A: A*",
    "P: PSO",
    "S: APSO",
    "H: HAPSO",
    "1: Remove redundant",
    "2: Remove trans. redund.",
    "3: Avoid corner cut",
    "4: SIW (PSO)",
    "5: SOBL (PSO)",
    "Space: Run",
    "Enter: Save result",
]
F3_MENU_ITEMS = [
    "B: Bresenham",
    "V: Fast voxel (Incremental)",
    "D: DDA runs (Runs of Runs)",
    "S: Start (copy from F1)",
    "G: Goal (copy from F1)",
    "C: Clear",
    "Space: Run algorithm",
]
F5_MENU_ITEMS = [
    "R: Run/Refresh compare",
    "Auto-run when open F5",
]
import pygame

MENU_ITEMS = {
    pygame.K_F1: "F1: Map Editor",
    pygame.K_F2: "F2: Pathfinding",
    pygame.K_F3: "F3: Line Grid",
    pygame.K_F4: "F4: Weight Compare",
    pygame.K_F5: "F5: Result Compare",
}
GRID_SIZE = 30
GRID_CELL_SIZE = 20
MAP_DIR = "maps"
RESULTS_DIR = "results"
