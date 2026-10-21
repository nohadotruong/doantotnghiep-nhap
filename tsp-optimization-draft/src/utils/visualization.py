"""
Module: Visualization
Purpose: Visualize paths and obstacles
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import LineCollection
from typing import List, Optional, Dict, Tuple
from ..environment import Environment, CircleObstacle, RectangleObstacle


class PathVisualizer:
    """Visualize paths and planning results"""

    def __init__(self, figsize: Tuple[int, int] = (12, 10)):
        """Initialize visualizer"""
        self.figsize = figsize
        self.fig = None
        self.ax = None

    def plot(
        self,
        environment: Environment,
        path: List[np.ndarray],
        waypoints: Optional[List[np.ndarray]] = None,
        title: str = "Path Planning Result",
        save_path: Optional[str] = None,
    ):
        """
        Plot path and environment

        Args:
            environment: Planning environment
            path: Path to plot
            waypoints: Optional waypoints to highlight
            title: Plot title
            save_path: Optional path to save figure
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

        # Plot environment bounds
        self.ax.set_xlim([environment.x_min, environment.x_max])
        self.ax.set_ylim([environment.y_min, environment.y_max])

        # Plot obstacles
        for obstacle in environment.obstacles:
            if isinstance(obstacle, CircleObstacle):
                circle = Circle(
                    obstacle.center,
                    obstacle.radius,
                    color="red",
                    alpha=0.3,
                    label="Obstacles",
                )
                self.ax.add_patch(circle)
            elif isinstance(obstacle, RectangleObstacle):
                rect = Rectangle(
                    (obstacle.x_min, obstacle.y_min),
                    obstacle.x_max - obstacle.x_min,
                    obstacle.y_max - obstacle.y_min,
                    color="red",
                    alpha=0.3,
                    label="Obstacles",
                )
                self.ax.add_patch(rect)

        # Plot path
        if path and len(path) > 0:
            path_array = np.array(path)
            self.ax.plot(
                path_array[:, 0],
                path_array[:, 1],
                "b-",
                linewidth=2,
                label="Path",
                zorder=2,
            )

            # Plot start and goal
            self.ax.plot(
                path_array[0, 0],
                path_array[0, 1],
                "go",
                markersize=10,
                label="Start",
                zorder=3,
            )
            self.ax.plot(
                path_array[-1, 0],
                path_array[-1, 1],
                "r*",
                markersize=15,
                label="Goal",
                zorder=3,
            )

        # Plot waypoints
        if waypoints and len(waypoints) > 0:
            waypoints_array = np.array(waypoints)
            self.ax.plot(
                waypoints_array[:, 0],
                waypoints_array[:, 1],
                "bs",
                markersize=8,
                label="Waypoints",
                zorder=2,
            )

        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")
        self.ax.set_title(title, fontsize=14, fontweight="bold")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        if save_path:
            self.fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return self.fig, self.ax

    def compare_paths(
        self,
        environment: Environment,
        paths: Dict[str, List[np.ndarray]],
        waypoints: Optional[List[np.ndarray]] = None,
        title: str = "Path Comparison",
        save_path: Optional[str] = None,
    ):
        """
        Compare multiple paths

        Args:
            environment: Planning environment
            paths: Dictionary of {method_name: path}
            waypoints: Optional waypoints
            title: Plot title
            save_path: Optional path to save figure
        """
        num_methods = len(paths)
        cols = min(2, num_methods)
        rows = (num_methods + cols - 1) // cols

        self.fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        if num_methods == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        colors = ["blue", "green", "orange", "purple", "brown"]

        for idx, (method_name, path) in enumerate(paths.items()):
            ax = axes[idx]

            # Plot environment bounds
            ax.set_xlim([environment.x_min, environment.x_max])
            ax.set_ylim([environment.y_min, environment.y_max])

            # Plot obstacles
            for obstacle in environment.obstacles:
                if isinstance(obstacle, CircleObstacle):
                    circle = Circle(
                        obstacle.center, obstacle.radius, color="red", alpha=0.3
                    )
                    ax.add_patch(circle)
                elif isinstance(obstacle, RectangleObstacle):
                    rect = Rectangle(
                        (obstacle.x_min, obstacle.y_min),
                        obstacle.x_max - obstacle.x_min,
                        obstacle.y_max - obstacle.y_min,
                        color="red",
                        alpha=0.3,
                    )
                    ax.add_patch(rect)

            # Plot path
            if path and len(path) > 0:
                path_array = np.array(path)
                color = colors[idx % len(colors)]
                ax.plot(
                    path_array[:, 0],
                    path_array[:, 1],
                    color=color,
                    linewidth=2,
                    label="Path",
                )

                # Plot start and goal
                ax.plot(
                    path_array[0, 0],
                    path_array[0, 1],
                    "go",
                    markersize=10,
                    label="Start",
                    zorder=3,
                )
                ax.plot(
                    path_array[-1, 0],
                    path_array[-1, 1],
                    "r*",
                    markersize=15,
                    label="Goal",
                    zorder=3,
                )

            # Plot waypoints
            if waypoints and len(waypoints) > 0:
                waypoints_array = np.array(waypoints)
                ax.plot(
                    waypoints_array[:, 0],
                    waypoints_array[:, 1],
                    "bs",
                    markersize=8,
                    label="Waypoints",
                    zorder=2,
                )

            ax.set_aspect("equal")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper right")
            ax.set_title(f"{method_name}", fontsize=12, fontweight="bold")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

        # Remove extra subplots
        for idx in range(num_methods, len(axes)):
            self.fig.delaxes(axes[idx])

        self.fig.suptitle(title, fontsize=16, fontweight="bold")

        if save_path:
            self.fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return self.fig, axes

    def plot_rrt_tree(
        self,
        environment: Environment,
        rrt_nodes: List[np.ndarray],
        path: Optional[List[np.ndarray]] = None,
        title: str = "RRT* Tree",
        save_path: Optional[str] = None,
    ):
        """Plot RRT* tree structure"""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

        # Plot environment bounds
        self.ax.set_xlim([environment.x_min, environment.x_max])
        self.ax.set_ylim([environment.y_min, environment.y_max])

        # Plot obstacles
        for obstacle in environment.obstacles:
            if isinstance(obstacle, CircleObstacle):
                circle = Circle(
                    obstacle.center, obstacle.radius, color="red", alpha=0.3
                )
                self.ax.add_patch(circle)
            elif isinstance(obstacle, RectangleObstacle):
                rect = Rectangle(
                    (obstacle.x_min, obstacle.y_min),
                    obstacle.x_max - obstacle.x_min,
                    obstacle.y_max - obstacle.y_min,
                    color="red",
                    alpha=0.3,
                )
                self.ax.add_patch(rect)

        # Plot RRT nodes
        if rrt_nodes:
            nodes_array = np.array(rrt_nodes)
            self.ax.plot(
                nodes_array[:, 0], nodes_array[:, 1], "k.", markersize=2, alpha=0.5
            )

        # Plot final path
        if path and len(path) > 0:
            path_array = np.array(path)
            self.ax.plot(
                path_array[:, 0],
                path_array[:, 1],
                "b-",
                linewidth=2,
                label="Final Path",
            )

        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_title(title, fontsize=14, fontweight="bold")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        if save_path:
            self.fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return self.fig, self.ax

    @staticmethod
    def plot_cost_comparison(
        results: Dict[str, float],
        title: str = "Cost Comparison",
        save_path: Optional[str] = None,
    ):
        """Plot cost comparison between methods"""
        fig, ax = plt.subplots(figsize=(10, 6))

        methods = list(results.keys())
        costs = list(results.values())

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        bars = ax.bar(methods, costs, color=colors[: len(methods)], alpha=0.7)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        ax.set_ylabel("Path Cost", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y")

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig, ax

    @staticmethod
    def show():
        """Display all plots"""
        plt.show()
