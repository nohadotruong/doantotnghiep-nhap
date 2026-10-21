"""HAPSO Pathfinding Application - Main Entry Point.

Initializes the refactored architecture:
1. Load UI configuration
2. Initialize AppState singleton
3. Create GUI Application
4. Start main event loop
"""

from config.ui_config import WINDOW_TITLE
from gui.app import App
from state.app_state import get_app_state


def main() -> None:
    """Initialize and run HAPSO application."""
    # Initialize AppState singleton (must be done before GUI)
    state = get_app_state()

    # Create and run GUI application
    app = App()
    app.run()


if __name__ == "__main__":
    main()
