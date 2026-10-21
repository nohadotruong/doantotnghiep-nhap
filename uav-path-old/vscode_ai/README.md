# Path plot with obstacles

Simple demo that generates many circular obstacles, computes an A* path on a grid, smooths it, and plots the result.

Usage:

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the script:

```bash
python plot_path_with_obstacles.py
```

The script saves `path_with_obstacles.png` and opens an interactive window.

You can edit parameters (map size, number of obstacles) at the top of the script.
