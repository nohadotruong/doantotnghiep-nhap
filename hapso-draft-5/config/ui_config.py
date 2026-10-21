WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 680
FPS: int = 60
WINDOW_TITLE: str = "HAPSO Simulation"
FULLSCREEN: bool = False
CENTER_WINDOW: bool = True

COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK: tuple[int, int, int] = (0, 0, 0)
COLOR_LIGHT_GRAY: tuple[int, int, int] = (240, 240, 240)
COLOR_DARK_GRAY: tuple[int, int, int] = (50, 50, 50)

NAV_HEIGHT: int = 40
SEPARATOR_HEIGHT: int = 2
VERTICAL_SEPARATOR_WIDTH: int = 2
CONTENT_LEFT_RATIO: float = 0.25
CONTENT_RIGHT_RATIO: float = 0.75

FONT_SIZE_DEFAULT: int = 24
FONT_SIZE_SMALL: int = 18

F1_MENU_ITEMS: list[str] = [
    "1: Set obstacle",
    "2: Ecrase",
    "S: Set start",
    "G: Set goal",
    "Enter: Save map",
    "L: Load map",
    "C: Clear",
]

F2_MENU_ITEMS: list[str] = [
    "1: A*",
    "2: PSO",
    "3: APSO",
    "4: HAPSO",
    "A: Run All",
    "Space: Run",
    "Enter: Save result",
]

F3_MENU_ITEMS: list[str] = [
    "Comparison (auto after Run All)",
    "Read-only metrics from AppState",
]

MENU_ITEMS: dict[int, str] = {
    1073741882: "F1: Map Editor",
    1073741883: "F2: Pathfinding",
    1073741884: "F3: Compare",
}

GRID_SIZE: int = 30
GRID_CELL_SIZE: int = 20
MAP_DIR: str = "data/maps"
RESULTS_DIR: str = "data/results"
