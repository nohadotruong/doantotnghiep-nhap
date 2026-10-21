import json
from datetime import datetime
from pathlib import Path
import sys
import time

import pygame

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.algo_config import (
    DEFAULT_MAP_PATH,
    RESULT_DIR,
)
from core.algorithms import APSO, Astar, Dijkstra, HAPSO, PRM, RRT, RRTStar
from core.metrics import compute_all_metrics
from map.map_serializer import MapSerializer
from map.map_validator import MapValidator
from config.ui_config import (
    GRID_CELL_SIZE,
    AXIS_LABEL_WIDTH,
    AXIS_LABEL_HEIGHT,
    AXIS_TO_GRID,
    MARGIN,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_WAYPOINT,
    FONT_SIZE_DEFAULT,
)


def load_map(path: str):
    grid_map = MapSerializer.load(path)
    if grid_map is None:
        print(f"[SIMULATOR]: Error loading map from {path}")
        sys.exit(1)
    return grid_map


def create_result_directory() -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    result_dir = Path(RESULT_DIR) / timestamp
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def save_result(result_dir: Path, result_data: dict, screen) -> None:
    json_path = result_dir / "result.json"
    image_path = result_dir / "result.png"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, indent=2)

    pygame.image.save(screen, str(image_path))


def run_simulator():
    grid_map = load_map(DEFAULT_MAP_PATH)

    if not MapValidator.validate(grid_map):
        print("[SIMULATOR]: Map validation failed")
        sys.exit(1)

    start = grid_map.start
    goal = grid_map.goal

    planner = Astar(grid_map)

    # planner = Dijkstra(grid_map)

    # planner = RRT(grid_map)

    # planner = RRTStar(grid_map)

    # planner = APSO(grid_map)

    # planner = HAPSO(grid_map)

    # planner = PRM(grid_map)

    start_time = time.perf_counter()
    path = planner.find_path(start, goal)
    execution_time = time.perf_counter() - start_time

    obstacle_count = grid_map.get_obstacle_count()
    planner_name = planner.__class__.__name__

    print("\n" + "=" * 50)
    print(f"  {planner_name.upper()} SIMULATOR")
    print("=" * 50)
    print(
        f"Map        : {grid_map.width} x {grid_map.height} | Obstacles: {obstacle_count}"
    )
    print(f"Start      : {start} -> Goal: {goal}")
    print("-" * 50)

    if path:
        print("Status     : SUCCESS")
        print("-" * 50)
        metrics = compute_all_metrics(path, grid_map, execution_time)
        print(f"Path Length    : {metrics['path_length']:.2f}")
        print(f"Waypoints      : {metrics['waypoints']}")
        print(f"Turning Angle  : {metrics['turning_angle']:.2f} rad")
        print(f"Min Clearance  : {metrics['min_clearance']:.2f}")
        print(f"Execution Time : {metrics['execution_time']:.4f}s")
        print("=" * 50 + "\n")
        result_data = {
            "planner": planner_name,
            "status": "SUCCESS",
            "map": {
                "width": grid_map.width,
                "height": grid_map.height,
                "start": start,
                "goal": goal,
            },
            "path": path,
            "metrics": metrics,
        }
        visualize_path(
            grid_map,
            path,
            f"{planner_name} Path Planning Simulator",
            result_data,
        )
    else:
        print("Status     : FAILED")
        print("-" * 50)
        print("No path found")
        print("=" * 50 + "\n")
        metrics = compute_all_metrics([], grid_map, execution_time)
        result_data = {
            "planner": planner_name,
            "status": "FAILED",
            "map": {
                "width": grid_map.width,
                "height": grid_map.height,
                "start": start,
                "goal": goal,
            },
            "path": [],
            "metrics": metrics,
        }
        visualize_path(
            grid_map,
            None,
            f"{planner_name} Path Planning Simulator",
            result_data,
        )


def visualize_path(grid_map, path, title, result_data):
    pygame.init()
    grid_width = grid_map.width * GRID_CELL_SIZE
    grid_height = grid_map.height * GRID_CELL_SIZE
    window_width = MARGIN + AXIS_LABEL_WIDTH + AXIS_TO_GRID + grid_width + MARGIN
    window_height = MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID + grid_height + MARGIN

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    axis_y_x = MARGIN
    axis_y_y = MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID
    axis_x_x = MARGIN + AXIS_LABEL_WIDTH + AXIS_TO_GRID
    axis_x_y = MARGIN + AXIS_LABEL_HEIGHT + AXIS_TO_GRID + grid_height

    result_dir = None
    is_saved = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if not is_saved:
                        result_dir = create_result_directory()
                        save_result(result_dir, result_data, screen)
                        is_saved = True

        screen.fill(COLOR_WHITE)

        for i in range(grid_map.height):
            for j in range(grid_map.width):
                cell_x = axis_x_x + j * GRID_CELL_SIZE
                cell_y = axis_y_y + i * GRID_CELL_SIZE

                if grid_map.grid[i][j] == 1:
                    pygame.draw.rect(
                        screen,
                        COLOR_BLACK,
                        (cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
                    )
                else:
                    pygame.draw.rect(
                        screen,
                        COLOR_LIGHT_GRAY,
                        (cell_x, cell_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
                        1,
                    )

        start = grid_map.start
        start_x = axis_x_x + start[0] * GRID_CELL_SIZE
        start_y = axis_y_y + start[1] * GRID_CELL_SIZE
        pygame.draw.rect(
            screen, COLOR_GREEN, (start_x, start_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
        )
        pygame.draw.circle(
            screen,
            COLOR_WAYPOINT,
            (start_x + GRID_CELL_SIZE // 2, start_y + GRID_CELL_SIZE // 2),
            GRID_CELL_SIZE // 4,
        )

        goal = grid_map.goal
        goal_x = axis_x_x + goal[0] * GRID_CELL_SIZE
        goal_y = axis_y_y + goal[1] * GRID_CELL_SIZE
        pygame.draw.rect(
            screen, COLOR_RED, (goal_x, goal_y, GRID_CELL_SIZE, GRID_CELL_SIZE)
        )
        pygame.draw.circle(
            screen,
            COLOR_WAYPOINT,
            (goal_x + GRID_CELL_SIZE // 2, goal_y + GRID_CELL_SIZE // 2),
            GRID_CELL_SIZE // 4,
        )

        if path:
            for i in range(len(path) - 1):
                x1 = axis_x_x + path[i][0] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                y1 = axis_y_y + path[i][1] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                x2 = axis_x_x + path[i + 1][0] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                y2 = axis_y_y + path[i + 1][1] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                pygame.draw.line(screen, COLOR_BLUE, (x1, y1), (x2, y2), 2)

            for x, y in path[1:-1]:
                cell_x = axis_x_x + x * GRID_CELL_SIZE
                cell_y = axis_y_y + y * GRID_CELL_SIZE
                pygame.draw.circle(
                    screen,
                    COLOR_WAYPOINT,
                    (cell_x + GRID_CELL_SIZE // 2, cell_y + GRID_CELL_SIZE // 2),
                    GRID_CELL_SIZE // 5,
                )

        for i in range(grid_map.width + 1):
            x = axis_x_x + i * GRID_CELL_SIZE
            pygame.draw.line(screen, COLOR_GRAY, (x, axis_y_y), (x, axis_x_y), 1)

        for i in range(grid_map.height + 1):
            y = axis_y_y + i * GRID_CELL_SIZE
            pygame.draw.line(
                screen, COLOR_GRAY, (axis_x_x, y), (axis_y_x + grid_width, y), 1
            )

        font = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        for i in range(grid_map.width):
            text = font.render(str(i), True, COLOR_BLACK)
            text_rect = text.get_rect()
            x = axis_x_x + i * GRID_CELL_SIZE
            screen.blit(text, (x + (GRID_CELL_SIZE - text_rect.width) // 2, MARGIN + 2))

        for i in range(grid_map.height):
            text = font.render(str(i), True, COLOR_BLACK)
            text_rect = text.get_rect()
            y = axis_y_y + i * GRID_CELL_SIZE
            screen.blit(
                text, (MARGIN + 2, y + (GRID_CELL_SIZE - text_rect.height) // 2)
            )

        # Results are saved when the user presses Enter

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_simulator()
