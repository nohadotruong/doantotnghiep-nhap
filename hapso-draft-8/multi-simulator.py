from datetime import datetime
from pathlib import Path

import json
import sys
import time

import pygame

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.algo_config import (
    DEFAULT_MAP_PATH,
    PRM_CONNECTION_RADIUS,
    PRM_N_SAMPLES,
    RRT_GOAL_SAMPLE_RATE,
    RRT_MAX_ITERATIONS,
    RRT_STAR_MAX_ITERATIONS,
    RRT_STAR_NEIGHBOR_RADIUS,
    RRT_STEP_SIZE,
    RESULT_DIR,
)
from core.algorithms import APSO, HAPSO, Astar, Dijkstra, PRM, RRT, RRTStar
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
    LEGEND_PANEL_WIDTH,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_SMALL,
)

ALGORITHMS = [
    (
        "Astar",
        (0, 120, 255),
        lambda grid_map: Astar(grid_map),
    ),
    # (
    #     "Dijkstra",
    #     (0, 200, 200),
    #     lambda grid_map: Dijkstra(grid_map),
    # ),
    # (
    #     "APSO",
    #     (255, 140, 0),
    #     lambda grid_map: APSO(grid_map),
    # ),
    (
        "HAPSO",
        (170, 0, 255),
        lambda grid_map: HAPSO(grid_map),
    ),
    # (
    #     "RRT",
    #     (0, 180, 120),
    #     lambda grid_map: RRT(
    #         grid_map,
    #         max_iter=RRT_MAX_ITERATIONS,
    #         step_size=RRT_STEP_SIZE,
    #         goal_sample_rate=RRT_GOAL_SAMPLE_RATE,
    #     ),
    # ),
    # (
    #     "RRTStar",
    #     (255, 80, 80),
    #     lambda grid_map: RRTStar(
    #         grid_map,
    #         max_iter=RRT_STAR_MAX_ITERATIONS,
    #         step_size=RRT_STEP_SIZE,
    #         goal_sample_rate=RRT_GOAL_SAMPLE_RATE,
    #         neighbor_radius=RRT_STAR_NEIGHBOR_RADIUS,
    #     ),
    # ),
    # (
    #     "PRM",
    #     (50, 200, 150),
    #     lambda grid_map: PRM(
    #         grid_map,
    #         n_samples=PRM_N_SAMPLES,
    #         connection_radius=PRM_CONNECTION_RADIUS,
    #     ),
    # ),
]


def load_map(path: str):
    grid_map = MapSerializer.load(path)
    if grid_map is None:
        print(f"[MULTI_SIMULATOR]: Error loading map from {path}")
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


def clone_grid_map(grid_map):
    return grid_map.__class__.from_dict(grid_map.to_dict())


def run_algorithm(name, color, planner_factory, grid_map, start, goal):
    planner = planner_factory(grid_map)
    start_time = time.perf_counter()
    path = planner.find_path(start, goal)
    execution_time = time.perf_counter() - start_time
    metrics = compute_all_metrics(path, grid_map, execution_time)

    return {
        "name": name,
        "color": color,
        "path": path,
        "metrics": metrics,
        "status": "SUCCESS" if path else "FAILED",
    }


def run_simulator():
    base_grid_map = load_map(DEFAULT_MAP_PATH)

    if not MapValidator.validate(base_grid_map):
        print("[MULTI_SIMULATOR]: Map validation failed")
        sys.exit(1)

    start = base_grid_map.start
    goal = base_grid_map.goal

    results = []
    for name, color, planner_factory in ALGORITHMS:
        algorithm_map = clone_grid_map(base_grid_map)
        result = run_algorithm(name, color, planner_factory, algorithm_map, start, goal)
        results.append(result)

    print("\n" + "=" * 108)
    print("  MULTI SIMULATOR")
    print("=" * 108)
    print(f"Map        : {base_grid_map.width} x {base_grid_map.height}")
    print(f"Start      : {start}")
    print(f"Goal       : {goal}")
    print("-" * 108)
    print(
        f"{'Algorithm':<12} {'Status':<10} {'Length':>10} {'Waypoints':>10} {'Turn(rad)':>12} {'Clearance':>12} {'Time(s)':>10}"
    )
    print("-" * 108)

    for result in results:
        metrics = result["metrics"]
        print(
            f"{result['name']:<12} {result['status']:<10} "
            f"{metrics['path_length']:>10.2f} {metrics['waypoints']:>10} "
            f"{metrics['turning_angle']:>12.2f} {metrics['min_clearance']:>12.2f} "
            f"{metrics['execution_time']:>10.4f}"
        )

    print("=" * 108 + "\n")

    result_data = {
        "map": {
            "width": base_grid_map.width,
            "height": base_grid_map.height,
            "start": start,
            "goal": goal,
        },
        "results": [
            {
                "planner": result["name"],
                "status": result["status"],
                "path": result["path"] if result["path"] else [],
                "metrics": result["metrics"],
            }
            for result in results
        ],
    }

    visualize_paths(
        base_grid_map, results, "Multi Path Planning Simulator", result_data
    )


def visualize_paths(grid_map, results, title, result_data):
    pygame.init()
    grid_width = grid_map.width * GRID_CELL_SIZE
    grid_height = grid_map.height * GRID_CELL_SIZE
    window_width = (
        MARGIN
        + AXIS_LABEL_WIDTH
        + AXIS_TO_GRID
        + grid_width
        + MARGIN
        + LEGEND_PANEL_WIDTH
    )
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

                if grid_map.grid[i][j] == grid_map.OBSTACLE:
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

        for result in results:
            path = result["path"]
            if not path:
                continue

            color = result["color"]
            if len(path) >= 2:
                for i in range(len(path) - 1):
                    x1 = axis_x_x + path[i][0] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    y1 = axis_y_y + path[i][1] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    x2 = (
                        axis_x_x + path[i + 1][0] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    )
                    y2 = (
                        axis_y_y + path[i + 1][1] * GRID_CELL_SIZE + GRID_CELL_SIZE // 2
                    )
                    pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

                for x, y in path[1:-1]:
                    cell_x = axis_x_x + x * GRID_CELL_SIZE
                    cell_y = axis_y_y + y * GRID_CELL_SIZE
                    pygame.draw.circle(
                        screen,
                        color,
                        (cell_x + GRID_CELL_SIZE // 2, cell_y + GRID_CELL_SIZE // 2),
                        GRID_CELL_SIZE // 6,
                    )

        start = grid_map.start
        start_x = axis_x_x + start[0] * GRID_CELL_SIZE
        start_y = axis_y_y + start[1] * GRID_CELL_SIZE
        pygame.draw.rect(
            screen,
            COLOR_GREEN,
            (start_x, start_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
        )

        goal = grid_map.goal
        goal_x = axis_x_x + goal[0] * GRID_CELL_SIZE
        goal_y = axis_y_y + goal[1] * GRID_CELL_SIZE
        pygame.draw.rect(
            screen,
            COLOR_RED,
            (goal_x, goal_y, GRID_CELL_SIZE, GRID_CELL_SIZE),
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

        font_legend = pygame.font.Font(None, FONT_SIZE_SMALL)
        legend_x = axis_x_x + grid_width + 30
        legend_y = 4
        for index, result in enumerate(results):
            y = legend_y + index * 18
            pygame.draw.line(
                screen,
                result["color"],
                (legend_x, y + 8),
                (legend_x + 18, y + 8),
                4,
            )
            text = font_legend.render(result["name"], True, COLOR_BLACK)
            screen.blit(text, (legend_x + 24, y))

        # Results are saved when the user presses Enter

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_simulator()
