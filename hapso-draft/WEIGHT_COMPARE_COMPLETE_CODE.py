"""
COMPLETE CODE FOR WEIGHT COMPARE FEATURE
=========================================

This file consolidates all code related to the Initial Weight Compare functionality.
Includes:
1. Inertia weight strategies (LDIW, NDIW, AIW, SIW)
2. UI Screen for comparing weight schedules
3. Chart generation logic

Usage:
------
Main entry point is CompareWeightScreen class in ui/compare_weight_screen.py
Requires: matplotlib, pygame, numpy

Key Components:
- 4 Inertia Weight Strategies
- Interactive UI with parameters: Iterations, w_min, w_max
- Real-time chart generation using matplotlib
- Pygame Surface rendering
"""

# ============================================================================
# PART 1: INERTIA WEIGHT STRATEGIES
# ============================================================================
# File: planners/inertia_weight.py

from abc import ABC, abstractmethod
import math
import numpy as np
import random


class InertiaWeight(ABC):
    """Abstract base for inertia weight strategies in PSO.

    Inertia weight controls the balance between exploration and exploitation
    in PSO algorithms. These strategies define how w changes over iterations.

    Parameters:
        w_min: Minimum inertia weight (default: 0.4)
        w_max: Maximum inertia weight (default: 0.9)
    """

    def __init__(self, w_min: float = 0.4, w_max: float = 0.9) -> None:
        self.w_min = w_min
        self.w_max = w_max

    @abstractmethod
    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        """Compute inertia weight at iteration k out of t_max.

        Args:
            k: Current iteration (1-indexed)
            t_max: Maximum iterations
            **kwargs: Additional parameters (e.g., fitness ratios for AIW)

        Returns:
            Inertia weight value for this iteration
        """
        pass


class LDIW(InertiaWeight):
    """Linear Decreasing Inertia Weight (LDIW).

    Inertia decreases linearly from w_max to w_min over iterations.
    Formula: w_max - (w_max - w_min) * (k / t_max)

    Characteristics:
    - Smooth linear decrease
    - Balanced exploration → exploitation transition
    - Easy to tune with w_min and w_max
    """

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        """Compute LDIW inertia weight."""
        if t_max == 0:
            return self.w_min
        return self.w_max - (self.w_max - self.w_min) * (k / t_max)


class NDIW(InertiaWeight):
    """Nonlinear Decreasing Inertia Weight (NDIW).

    Inertia decreases nonlinearly with exponential curve.
    Formula: w_min + (w_max - w_min) * exp(-2*k/t_max)

    Characteristics:
    - Rapid decrease at start (more exploration)
    - Accelerated convergence at end (more exploitation)
    - Better for complex search spaces
    """

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        """Compute NDIW inertia weight."""
        if t_max == 0:
            return self.w_min
        exponent = -2.0 * k / t_max
        return self.w_min + (self.w_max - self.w_min) * math.exp(exponent)


class AIW(InertiaWeight):
    """Adaptive Inertia Weight (AIW).

    Inertia adapts based on fitness improvement ratio.
    - High improvement → more exploration (higher w)
    - Low improvement → more exploitation (lower w)

    Formula: Adapts based on pk_gbest / pk1_gbest ratio

    Characteristics:
    - Responds to algorithm performance
    - Dynamic adaptation during optimization
    - Requires fitness metrics passed via kwargs
    """

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        """Compute AIW inertia weight.

        Args:
            k: Current iteration
            t_max: Maximum iterations
            pk_gbest: Current best fitness (kwarg)
            pk1_gbest: Previous best fitness (kwarg)
        """
        pk_gbest = kwargs.get("pk_gbest", 1.0)
        pk1_gbest = kwargs.get("pk1_gbest", pk_gbest)

        # Calculate fitness improvement ratio
        if pk1_gbest != 0:
            fitness_ratio = pk_gbest / pk1_gbest
        else:
            fitness_ratio = 1.0

        # Adapt w based on ratio
        return (self.w_max + self.w_min) * fitness_ratio - self.w_max * (
            k / max(1, t_max)
        )


class SIW(InertiaWeight):
    """Stochastic Inertia Weight (SIW).

    Linear decreasing inertia with random perturbation.
    Formula: LDIW * exp(random_noise), where rb ~ U(-0.1, 0.1)

    Characteristics:
    - Adds randomness to prevent premature convergence
    - Maintains diversity while decreasing w
    - Useful when stuck in local optima
    """

    def compute(self, k: int, t_max: int, **kwargs: float) -> float:
        """Compute SIW inertia weight."""
        if t_max == 0:
            return self.w_min

        # Base weight from linear decreasing
        w_base = self.w_max - (self.w_max - self.w_min) * (k / t_max)

        # Random perturbation
        rb = random.uniform(-0.1, 0.1)
        perturbation = math.exp(rb)

        return w_base * perturbation


def get_strategy(strategy_name: str) -> InertiaWeight:
    """Get inertia weight strategy by name.

    Args:
        strategy_name: "LDIW", "NDIW", "AIW", or "SIW"

    Returns:
        InertiaWeight instance

    Raises:
        ValueError if strategy_name is unknown
    """
    strategies = {
        "LDIW": LDIW,
        "NDIW": NDIW,
        "AIW": AIW,
        "SIW": SIW,
    }

    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    return strategies[strategy_name]()


# ============================================================================
# PART 2: UI SCREEN - COMPARE WEIGHT
# ============================================================================
# File: ui/compare_weight_screen.py

from __future__ import annotations
from io import BytesIO

import matplotlib
import pygame

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Assumes these are defined in ui/common.py:
# - FONT_NORMAL: int (e.g., 14)
# - FONT_SMALL: int (e.g., 11)
# - PALETTE: dict with keys "bg", "panel", "muted"
# - Button class: has draw() and get_rect() methods
# - TextInput class: has handle_event(), draw(), get_int(), get_float() methods
# - draw_title() function: renders title and subtitle


class CompareWeightScreen:
    """Screen for comparing 4 inertia weight strategies.

    Layout:
    - Left panel (30% width): Controls and status
    - Right panel (70% width): Matplotlib chart

    Controls:
    - R key: Recompute chart with current parameters
    - TextInputs for: Iterations, w_min, w_max
    """

    def __init__(self, app: object) -> None:
        """Initialize compare weight screen.

        Args:
            app: Main application object with window_width and window_height
        """
        self.app = app
        self.chart_surface: pygame.Surface | None = None
        self.status = "Press R to generate omega chart"

        # Define buttons
        self.buttons = [Button(pygame.Rect(24, 117, 294, 32), "Recompute Weights", "R")]

        # Define input fields with default values
        self.inputs = [
            TextInput(pygame.Rect(24, 172, 294, 30), "Iterations", "80"),
            TextInput(pygame.Rect(24, 225, 294, 30), "w_min", "0.4"),
            TextInput(pygame.Rect(24, 278, 294, 30), "w_max", "0.9"),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle user input events.

        - Text input handling for parameter fields
        - R key press triggers chart generation
        """
        # Forward events to input fields
        for field in self.inputs:
            field.handle_event(event)

        # Check for R key to rebuild chart
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self._build_chart()

    def update(self) -> None:
        """Update screen state (stub for consistency with other screens)."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entire compare weight screen.

        Layout:
        1. Fill background
        2. Create left/right panels (3:7 ratio)
        3. Draw left panel: title, buttons, inputs, status
        4. Draw right panel: centered matplotlib chart
        """
        # Fill background
        surface.fill(PALETTE["bg"])
        content_top = 40

        # Calculate panel dimensions (3-7 ratio layout)
        left_panel_width = int(self.app.window_width * 0.3)
        right_panel_x = left_panel_width
        right_panel_width = self.app.window_width - left_panel_width
        content_bottom = self.app.window_height

        # Draw left panel background
        pygame.draw.rect(
            surface,
            PALETTE["panel"],
            pygame.Rect(0, content_top, left_panel_width, content_bottom - content_top),
        )

        # Draw borders between panels
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (left_panel_width, content_top),
            (left_panel_width, content_bottom),
            2,
        )
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (right_panel_x, content_top),
            (right_panel_x, content_bottom),
            2,
        )

        # Draw title in left panel
        draw_title(surface, "Weight Compare", "Compare 4 inertia formulas")

        # Draw buttons in left panel
        font = pygame.font.Font(None, FONT_NORMAL)
        for b in self.buttons:
            b.draw(surface, font)

        # Draw input fields in left panel
        small_font = pygame.font.Font(None, FONT_SMALL)
        for field in self.inputs:
            field.draw(surface, small_font)

        # Draw status message in left panel
        status_text = pygame.font.Font(None, FONT_SMALL).render(
            self.status, True, PALETTE["muted"]
        )
        surface.blit(status_text, (21, 313))

        # Draw chart in right panel (centered)
        if self.chart_surface:
            chart_width = self.chart_surface.get_width()
            chart_height = self.chart_surface.get_height()

            # Calculate center position in right panel
            chart_x = right_panel_x + 5 + ((right_panel_width - 10) - chart_width) // 2
            chart_y = 60 + (content_bottom - 60 - chart_height) // 2

            # Blit chart to screen
            surface.blit(self.chart_surface, (chart_x, chart_y))

    def _build_chart(self) -> None:
        """Generate matplotlib chart comparing 4 inertia weight strategies.

        Process:
        1. Extract parameters from input fields
        2. Create 4 strategy instances with w_min and w_max
        3. Calculate weight values for each iteration
        4. Plot all 4 strategies on same graph
        5. Convert matplotlib figure to Pygame Surface
        6. Store in self.chart_surface for rendering
        """
        # Extract parameters from input fields
        t_max = max(5, self.inputs[0].get_int(80))  # Iterations (min 5)
        w_min = self.inputs[1].get_float(0.4)  # Minimum weight
        w_max = self.inputs[2].get_float(0.9)  # Maximum weight

        # Create instances of all 4 strategies
        formulas = {
            "LDIW": LDIW(w_min=w_min, w_max=w_max),
            "NDIW": NDIW(w_min=w_min, w_max=w_max),
            "AIW": AIW(w_min=w_min, w_max=w_max),
            "SIW": SIW(w_min=w_min, w_max=w_max),
        }

        # Generate iteration array
        k_values = np.arange(1, t_max + 1)

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(5.3, 4.9), dpi=100)
        fig.patch.set_facecolor((1.0, 1.0, 1.0))  # White background
        ax.set_facecolor((1.0, 1.0, 1.0))  # White axis background

        # Plot each strategy as a line
        for label, model in formulas.items():
            # Calculate weight values for each iteration
            vals = [
                model.compute(k, t_max, pk_gbest=1.0 / (k + 2), pk1_gbest=1.0 / (k + 1))
                for k in k_values
            ]
            # Plot the line
            ax.plot(k_values, vals, label=label, linewidth=2.2)

        # Configure chart appearance
        ax.set_title("Inertia Weight Schedules", fontsize=13)
        ax.set_xlabel("Iteration")
        ax.set_ylabel("w")
        ax.grid(alpha=0.2)
        ax.legend()

        # Convert matplotlib figure to PNG in memory
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

        # Load PNG as Pygame Surface
        buf.seek(0)
        self.chart_surface = pygame.image.load(buf).convert_alpha()

        # Update status message
        self.status = "Chart updated with custom parameters"


# ============================================================================
# INTEGRATION POINTS
# ============================================================================

"""
1. MAIN.PY INTEGRATION:
   - Import: from ui.compare_weight_screen import CompareWeightScreen
   - Keyboard shortcut: F3 key triggers this screen
   - Navigation text: "F3: Weight Compare"

2. UI/COMMON.PY REQUIREMENTS:
   - FONT_NORMAL: Font size constant
   - FONT_SMALL: Font size constant
   - PALETTE: Color dictionary
   - Button class: Interactive button component
   - TextInput class: Text input field component
   - draw_title(): Function to draw title/subtitle

3. DEPENDENCIES:
   - matplotlib: Chart generation (Agg backend for headless rendering)
   - numpy: Array operations
   - pygame: Display and event handling
   - io.BytesIO: In-memory PNG generation

4. EXPECTED PARAMETERS:
   - app.window_width: Application window width
   - app.window_height: Application window height

5. USER INTERACTION:
   - Press R: Recompute chart with current parameter values
   - Modify inputs: Iterations, w_min, w_max values
   - View: Real-time comparison of 4 strategies
"""

# ============================================================================
# FORMULAS REFERENCE
# ============================================================================

"""
LDIW (Linear Decreasing Inertia Weight):
    w(k) = w_max - (w_max - w_min) * (k / t_max)
    - Simple linear interpolation
    - Best for: Consistent problems with predictable difficulty

NDIW (Nonlinear Decreasing Inertia Weight):
    w(k) = w_min + (w_max - w_min) * exp(-2*k/t_max)
    - Exponential decay curve
    - Best for: Problems requiring adaptive exploration/exploitation balance

AIW (Adaptive Inertia Weight):
    w(k) adapts based on fitness improvement ratio
    - Dynamic adjustment during optimization
    - Best for: Variable difficulty landscapes

SIW (Stochastic Inertia Weight):
    w(k) = LDIW(k) * exp(rb), where rb ~ U(-0.1, 0.1)
    - Adds randomness to prevent premature convergence
    - Best for: Avoiding local optima
"""

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
# In your main application:

class MyApp:
    def __init__(self):
        self.window_width = 1200
        self.window_height = 800
        self.compare_weight_screen = CompareWeightScreen(self)
    
    def handle_event(self, event):
        self.compare_weight_screen.handle_event(event)
    
    def update(self):
        self.compare_weight_screen.update()
    
    def render(self, surface):
        self.compare_weight_screen.draw(surface)

# User workflow:
1. Press F3 to open Weight Compare screen
2. Modify Iterations, w_min, w_max values as needed
3. Press R to regenerate chart
4. Observe how different strategies behave
5. Use insights to select best strategy for your problem
"""
