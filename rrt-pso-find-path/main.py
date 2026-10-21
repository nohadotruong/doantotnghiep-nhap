import pandas as pd
import time

from algorithms import AStarPlanner, PSOOptimizer, RRTPlanner
from utils import path_length, smoothness_penalty, calculate_path_safety
from environment.environment import UAVEnvironment


def main():
    paths = {}

    print("\n===== UAV PATH FINDING =====")

    # ================================================
    # LOADING MAP
    # ================================================
    print("[MAP] Loading map...")
    uav_map = UAVEnvironment.load_map(
        r"D:\DEV\_Projects\TLU\DoAn\rrt-pso-find-path\maps\map_20260302_164324\config.json"
    )
    if not uav_map:
        print("[MAP] Failed to load the map!")
        return

    print("[MAP] Map loaded successfully!")
    print("[MAP] Setting up start and goal positions...")
    start, goal = (0, 0), (100, 100)
    print(f"[MAP] Start: {start}")
    print(f"[MAP] Goal: {goal}")

    # ================================================
    # A*
    # ================================================

    astar_planner = AStarPlanner(uav_map, start, goal)
    print(f"\n[A*] A* Parameters:")
    print(f"[A*] - Grid resolution: 2.0")
    print(f"[A*] - Heuristic: Euclidean distance")
    print(f"[A*] - Diagonal movement: Enabled")
    print(f"\n[A*] Starting path planning using A*...")

    astar_start_time = time.time()
    astar_path = astar_planner.plan()
    astar_end_time = time.time()
    astar_time = astar_end_time - astar_start_time

    if astar_path is None:
        print(f"\n[A*] Path planning failed after {astar_time:.3f} seconds.")
    else:
        astar_length = path_length(astar_path)
        astar_waypoints = len(astar_path)
        astar_smoothy = smoothness_penalty(astar_path)
        astar_safety_score, astar_min_dis, astar_safe = calculate_path_safety(
            astar_path, uav_map.obstacles
        )

        print("\n[A*] Path found successfully!")
        print(f"[A*] - Number of waypoints: {astar_waypoints}")
        print(f"[A*] - Path length: {astar_length:.3f}")
        print(f"[A*] - Smoothness penalty: {astar_smoothy:.3f}")
        print(f"[A*] - Safety score: {int(astar_safety_score)}%")
        print(f"[A*] - Execution time: {astar_time:.3f} seconds")

        paths["A*"] = astar_path
        # uav_map.visualize(astar_path)

    # ================================================
    # RRT
    # ================================================

    # rrt_planner = RRTPlanner(uav_map, start, goal)
    # print(f"\n[RRT] RRT Parameters:")
    # print(f"[RRT] - Step size: 5.0")
    # print(f"[RRT] - Max iterations: 5000")
    # print(f"[RRT] - Goal sample rate: 0.2")
    # print(f"\n[RRT] Starting path planning using RRT...")

    # rrt_start_time = time.time()
    # rrt_path = rrt_planner.plan()
    # rrt_end_time = time.time()
    # rrt_time = rrt_end_time - rrt_start_time

    # if rrt_path is None:
    #     print(f"\n[RRT] Path planning failed after {rrt_time:.3f} seconds.")
    # else:
    #     rrt_length = path_length(rrt_path)
    #     rrt_waypoints = len(rrt_path)
    #     rrt_smoothy = smoothness_penalty(rrt_path)
    #     rrt_safety_score, rrt_min_dis, rrt_safe = calculate_path_safety(
    #         rrt_path, uav_map.obstacles
    #     )

    #     print("\n[RRT] Path found successfully!")
    #     print(f"[RRT] - Number of waypoints: {rrt_waypoints}")
    #     print(f"[RRT] - Path length: {rrt_length:.3f}")
    #     print(f"[RRT] - Smoothness penalty: {rrt_smoothy:.3f}")
    #     print(f"[RRT] - Safety score: {rrt_safety_score}%")
    #     print(f"[RRT] - Execution time: {rrt_time:.3f} seconds")

    #     paths["RRT"] = rrt_path
    # uav_map.visualize(rrt_path)

    # ================================================
    # A* x PSO
    # ================================================

    print("\n[PSO] Start A* optimization with PSO... ")
    if len(astar_path) <= 2:
        print("[PSO] Path too short! Skip optimizer!")
        pso_astar_path = astar_path
        pso_astar_length = astar_length
        pso_astar_waypoints = astar_waypoints
        pso_astar_smoothy = astar_smoothy
        pso_astart_safety = astar_safety_score
        pso_astar_time = 0
    else:
        pso_astar_optimizer = PSOOptimizer(uav_map, astar_path)

        pso_astar_start_time = time.time()
        pso_astar_path = pso_astar_optimizer.optimize()
        pso_astar_end_time = time.time()
        pso_astar_time = pso_astar_end_time - pso_astar_start_time

        if pso_astar_path is None:
            print("\n[PSO] A* optimizer failed!")
        else:
            pso_astar_length = path_length(pso_astar_path)
            pso_astar_waypoints = len(pso_astar_path)
            pso_astar_smoothy = smoothness_penalty(pso_astar_path)
            pso_astar_safety, pso_astar_min_dis, pso_astar_safe = calculate_path_safety(
                pso_astar_path, uav_map.obstacles
            )
            paths["A* x PSO"] = pso_astar_path

        print("\n[PSO] A* optimizer completed!")
        print(f"[PSO] - Number of waypoints: {pso_astar_waypoints}")
        print(f"[PSO] - Path length: {pso_astar_length:.3f}")
        print(f"[PSO] - Smoothness penalty: {pso_astar_smoothy:.3f}")
        print(f"[PSO] - Safety score: {pso_astar_safety}%")
        print(f"[PSO] - Execution time: {pso_astar_time:.3f} seconds")

    # ================================================
    # RRT x PSO
    # ================================================

    # print("\n[PSO] Start RRT optimization with PSO... ")
    # if len(rrt_path) <= 2:
    #     print("[PSO] Path too short! Skip optimizer!")
    #     pso_rrt_path = rrt_path
    #     pso_rrt_length = rrt_length
    #     pso_rrt_waypoints = rrt_waypoints
    #     pso_rrt_smoothy = rrt_smoothy
    #     pso_rrtt_safety = rrt_safety_score
    #     pso_rrt_time = 0
    # else:
    #     pso_rrt_optimizer = PSOOptimizer(uav_map, rrt_path)

    #     pso_rrt_start_time = time.time()
    #     pso_rrt_path = pso_rrt_optimizer.optimize()
    #     pso_rrt_end_time = time.time()
    #     pso_rrt_time = pso_rrt_end_time - pso_rrt_start_time

    #     if pso_rrt_path is None:
    #         print("\n[PSO] RRT optimizer failed!")
    #     else:
    #         pso_rrt_length = path_length(pso_rrt_path)
    #         pso_rrt_waypoints = len(pso_rrt_path)
    #         pso_rrt_smoothy = smoothness_penalty(pso_rrt_path)
    #         pso_rrt_safety, pso_rrt_min_dis, pso_rrt_safe = calculate_path_safety(
    #             pso_rrt_path, uav_map.obstacles
    #         )
    #         paths["RRT x PSO"] = pso_rrt_path

    #     print("\n[PSO] RRT optimizer completed!")
    #     print(f"[PSO] - Number of waypoints: {pso_rrt_waypoints}")
    #     print(f"[PSO] - Path length: {pso_rrt_length:.3f}")
    #     print(f"[PSO] - Smoothness penalty: {pso_rrt_smoothy:.3f}")
    #     print(f"[PSO] - Safety score: {pso_rrt_safety}%")
    #     print(f"[PSO] - Execution time: {pso_rrt_time:.3f} seconds")

    # ================================================
    # COMPARE TABLE
    # ================================================
    data = [
        [
            "A*",
            astar_waypoints,
            astar_length,
            astar_smoothy,
            astar_safety_score,
            astar_time,
        ],
        # ["RRT", rrt_waypoints, rrt_length, rrt_smoothy, rrt_safety_score, rrt_time],
        [
            "A* x PSO",
            pso_astar_waypoints,
            pso_astar_length,
            pso_astar_smoothy,
            pso_astar_safety,
            pso_astar_time,
        ],
        # [
        #     "RRT x PSO",
        #     pso_rrt_waypoints,
        #     pso_rrt_length,
        #     pso_rrt_smoothy,
        #     pso_rrt_safety,
        #     pso_rrt_time,
        # ],
    ]

    columns = [
        "Algorithm",
        "Number of waypoints",
        "Path length",
        "Smoothness penalty",
        "Safety score",
        "Execution time (s)",
    ]

    df = pd.DataFrame(data, columns=columns)
    print(df)

    # ================================================
    # RESULT
    # ================================================

    if len(paths) > 0:
        uav_map.visualize_multiple_paths(paths)


if __name__ == "__main__":
    main()
