from __future__ import annotations

import pygame

from app_io.map_io import list_saved_maps, load_map_from_dir, save_map_bundle
from ui.common import FONT_NORMAL, FONT_SMALL, PALETTE, Button, draw_title
from utils.grid_utils import Grid, Point, is_valid


class MapEditorScreen:
    def __init__(self, app: object) -> None:
        self.app = app
        self.mode = "Obstacle"
        self.cell_size = app.cell_size
        self.grid_origin = (0, 0)
        self.dragging = False
        self.drag_start_cell: tuple[int, int] | None = None
        self.drag_end_cell: tuple[int, int] | None = None
        self.status_text = "Ready"
        self.load_menu_open = False  # Ensure menu is closed at start
        self.map_choices: list[str] = []
        self.selected_map_idx = 0
        self.current_page = 0
        self.maps_per_page = 5

        self.actions = [
            Button(pygame.Rect(24, 117, 294, 36), "Obstacle Mode", "1"),
            Button(pygame.Rect(24, 158, 294, 36), "Erase Mode", "2"),
            Button(pygame.Rect(24, 199, 294, 36), "Set Start", "S"),
            Button(pygame.Rect(24, 240, 294, 36), "Set Goal", "G"),
            Button(pygame.Rect(24, 281, 294, 36), "Clear Map", "C"),
            Button(pygame.Rect(24, 322, 294, 36), "Save Map", "M"),
            Button(pygame.Rect(24, 363, 294, 36), "Load Map", "L"),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        self._update_layout()

        if self.load_menu_open:
            self._handle_load_menu_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.mode = "Obstacle"
            elif event.key == pygame.K_2:
                self.mode = "Erase"
            elif event.key == pygame.K_s:
                self.mode = "Start"
            elif event.key == pygame.K_g:
                self.mode = "Goal"
            elif event.key == pygame.K_c:
                self._clear_map()
            elif event.key == pygame.K_m:
                saved_dir = save_map_bundle(
                    self.app.grid,
                    self.app.start,
                    self.app.goal,
                    self.app.cell_size,
                )
                self.status_text = f"Saved: {saved_dir.name}"
            elif event.key == pygame.K_l:
                self._open_load_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_start_cell = self._to_grid(event.pos)
            if self.drag_start_cell != (None, None):
                self.drag_end_cell = self.drag_start_cell
                self.dragging = True

        if event.type == pygame.MOUSEMOTION and self.dragging:
            current = self._to_grid(event.pos)
            if current != (None, None):
                self.drag_end_cell = current

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag_start_cell and self.drag_end_cell:
                self._paint_line(self.drag_start_cell, self.drag_end_cell)
            self.dragging = False
            self.drag_start_cell = None
            self.drag_end_cell = None

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self._update_layout()
        surface.fill(PALETTE["bg"])

        # Calculate panel boundaries for 3-4-3 ratio
        left_panel_width = int(self.app.window_width * 0.3)
        center_panel_width = int(self.app.window_width * 0.4)
        right_panel_x = left_panel_width + center_panel_width
        right_panel_width = self.app.window_width - right_panel_x

        content_top = 40
        content_bottom = self.app.window_height

        # Draw borders: left (border-right), center (no border), right (border-left)
        # Left panel border-right
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (left_panel_width, content_top),
            (left_panel_width, content_bottom),
            2,
        )
        # Right panel border-left
        pygame.draw.line(
            surface,
            (0, 0, 0),
            (right_panel_x, content_top),
            (right_panel_x, content_bottom),
            2,
        )

        draw_title(surface, "Map Editor", "Draw map, set start and goal")

        font = pygame.font.Font(None, FONT_NORMAL)
        for b in self.actions:
            b.draw(surface, font)

        mode_text = font.render(f"Current mode: {self.mode}", True, PALETTE["accent"])
        surface.blit(mode_text, (21, 404))
        hint = pygame.font.Font(None, FONT_SMALL).render(
            "Drag draws obstacle lines", True, PALETTE["muted"]
        )
        surface.blit(hint, (21, 429))

        self._draw_right_panel(surface, right_panel_x, right_panel_width)

        self._draw_grid(surface)

        if self.load_menu_open:
            self._draw_load_menu(surface)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        ox, oy = self.grid_origin
        grid: Grid = self.app.grid
        grid_width = len(grid[0])
        grid_height = len(grid)

        # Draw grid cells
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    ox + x * self.cell_size,
                    oy + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                color = PALETTE["obstacle"] if cell == 1 else (250, 249, 246)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, PALETTE["grid"], rect, 1)

        # Draw X-axis coordinates (0 to grid_width-1, left to right)
        coord_font = pygame.font.Font(None, 16)
        for x in range(grid_width):
            label = coord_font.render(str(x), True, (0, 0, 0))
            x_pos = (
                ox + x * self.cell_size + self.cell_size // 2 - label.get_width() // 2
            )
            y_pos = oy - 20
            surface.blit(label, (x_pos, y_pos))

        # Draw Y-axis coordinates (grid_height-1 to 0, bottom to top)
        for y in range(grid_height):
            display_y = grid_height - 1 - y  # Flip y-axis so it goes bottom-to-top
            label = coord_font.render(str(display_y), True, (0, 0, 0))
            x_pos = ox - 25
            y_pos = (
                oy + y * self.cell_size + self.cell_size // 2 - label.get_height() // 2
            )
            surface.blit(label, (x_pos, y_pos))

        if self.app.start:
            self._draw_marker(surface, self.app.start, PALETTE["start"])
        if self.app.goal:
            self._draw_marker(surface, self.app.goal, PALETTE["goal"])

        if self.dragging and self.drag_start_cell and self.drag_end_cell:
            for x, y in self._line_cells(self.drag_start_cell, self.drag_end_cell):
                if is_valid(x, y, self.app.grid):
                    preview = pygame.Rect(
                        ox + x * self.cell_size,
                        oy + y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    )
                    pygame.draw.rect(surface, (110, 110, 110), preview, 2)

    def _draw_marker(
        self, surface: pygame.Surface, point: Point, color: tuple[int, int, int]
    ) -> None:
        ox, oy = self.grid_origin
        x, y = point
        cx = ox + x * self.cell_size + self.cell_size // 2
        cy = oy + y * self.cell_size + self.cell_size // 2
        pygame.draw.circle(surface, color, (cx, cy), max(4, self.cell_size // 2 - 2))

    def _draw_right_panel(
        self, surface: pygame.Surface, panel_x: int, panel_width: int
    ) -> None:
        font = pygame.font.Font(None, FONT_NORMAL)
        small = pygame.font.Font(None, FONT_SMALL)

        start_txt = f"Start: {self.app.start}" if self.app.start else "Start: not set"
        goal_txt = f"Goal: {self.app.goal}" if self.app.goal else "Goal: not set"
        obs_count = sum(cell for row in self.app.grid for cell in row)

        lines = [
            "Map Information",
            start_txt,
            goal_txt,
            f"Obstacles: {obs_count}",
            f"Grid: {len(self.app.grid[0])}x{len(self.app.grid)}",
            f"Status: {self.status_text}",
        ]
        y = 60  # content_top (40) + margin (20)
        x_offset = panel_x + 21  # 5px panel padding + 16px content padding
        for idx, line in enumerate(lines):
            renderer = font if idx == 0 else small
            surface.blit(renderer.render(line, True, PALETTE["ink"]), (x_offset, y))
            y += 34 if idx == 0 else 28

    def _paint_at_mouse(self, pos: tuple[int, int]) -> None:
        gx, gy = self._to_grid(pos)
        if gx is None or gy is None:
            return
        if not is_valid(gx, gy, self.app.grid):
            return

        if self.mode == "obstacle":
            self.app.grid[gy][gx] = 1
        elif self.mode == "erase":
            self.app.grid[gy][gx] = 0
        elif self.mode == "start":
            self.app.start = (gx, gy)
            self.app.grid[gy][gx] = 0
        elif self.mode == "goal":
            self.app.goal = (gx, gy)
            self.app.grid[gy][gx] = 0

    def _paint_line(
        self,
        start_cell: tuple[int | None, int | None],
        end_cell: tuple[int | None, int | None],
    ) -> None:
        sx, sy = start_cell
        ex, ey = end_cell
        if sx is None or sy is None or ex is None or ey is None:
            return

        if self.mode in ("start", "goal"):
            self._paint_cell(ex, ey)
            return

        for x, y in self._line_cells((sx, sy), (ex, ey)):
            self._paint_cell(x, y)

    def _line_cells(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        sx, sy = start
        ex, ey = end

        x0, y0 = sx, sy
        x1, y1 = ex, ey
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        err = dx - dy
        cells: list[tuple[int, int]] = []

        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += step_x
            if e2 < dx:
                err += dx
                y0 += step_y

        return cells

    def _paint_cell(self, gx: int, gy: int) -> None:
        if not is_valid(gx, gy, self.app.grid):
            return
        if self.mode == "obstacle":
            self.app.grid[gy][gx] = 1
        elif self.mode == "erase":
            self.app.grid[gy][gx] = 0
        elif self.mode == "start":
            self.app.start = (gx, gy)
            self.app.grid[gy][gx] = 0
        elif self.mode == "goal":
            self.app.goal = (gx, gy)
            self.app.grid[gy][gx] = 0

    def _to_grid(self, pos: tuple[int, int]) -> tuple[int | None, int | None]:
        ox, oy = self.grid_origin
        mx, my = pos
        x = (mx - ox) // self.cell_size
        y = (my - oy) // self.cell_size
        if x < 0 or y < 0:
            return None, None
        if y >= len(self.app.grid) or x >= len(self.app.grid[0]):
            return None, None
        return x, y

    def _clear_map(self) -> None:
        for y in range(len(self.app.grid)):
            for x in range(len(self.app.grid[0])):
                self.app.grid[y][x] = 0
        self.app.start = None
        self.app.goal = None
        self.app.path = []
        self.status_text = "Map cleared"

    def _update_layout(self) -> None:
        # For 3-4-3 layout, center panel (40%) starts at 30% of window width
        left_panel_width = int(self.app.window_width * 0.3)
        center_panel_width = int(self.app.window_width * 0.4)
        right_panel_x = left_panel_width + center_panel_width

        content_top = 40
        content_bottom = self.app.window_height
        panel_height = content_bottom - content_top

        # Calculate grid size in pixels
        grid_px = len(self.app.grid[0]) * self.cell_size
        grid_height_px = len(self.app.grid) * self.cell_size

        # Account for coordinate display: 25px left for Y-axis, 20px top for X-axis
        total_width_with_coords = grid_px + 25
        total_height_with_coords = grid_height_px + 20

        # Center grid + coordinates within the center panel
        offset_x = (center_panel_width - total_width_with_coords) // 2
        offset_y = (panel_height - total_height_with_coords) // 2

        # grid_origin should account for the 25px left margin and 20px top margin
        grid_origin_x = left_panel_width + offset_x + 25
        grid_origin_y = content_top + offset_y + 20

        self.grid_origin = (grid_origin_x, grid_origin_y)
        self.current_page = 0
        if not self.map_choices:
            self.status_text = "No saved map in data/maps"

    def _open_load_menu(self) -> None:
        """Open the load map menu and load available map choices."""
        self.map_choices = list_saved_maps()
        self.load_menu_open = True
        self.selected_map_idx = 0
        self.current_page = 0

    def _handle_load_menu_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        # Allow Q or Backspace to close menu
        if event.key == pygame.K_q or event.key == pygame.K_BACKSPACE:
            self.load_menu_open = False
            return

        if not self.map_choices:
            # No maps available, only RETURN/SPACE can close
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.load_menu_open = False
            return

        # Calculate pagination
        total_pages = (
            len(self.map_choices) + self.maps_per_page - 1
        ) // self.maps_per_page
        page_start = self.current_page * self.maps_per_page
        page_end = min(page_start + self.maps_per_page, len(self.map_choices))
        page_items = self.map_choices[page_start:page_end]

        if event.key == pygame.K_UP:
            self.selected_map_idx = (self.selected_map_idx - 1) % len(self.map_choices)
            # Adjust page if needed
            self.current_page = self.selected_map_idx // self.maps_per_page
        elif event.key == pygame.K_DOWN:
            self.selected_map_idx = (self.selected_map_idx + 1) % len(self.map_choices)
            # Adjust page if needed
            self.current_page = self.selected_map_idx // self.maps_per_page
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            selected = self.map_choices[self.selected_map_idx]
            map_name = selected.name if hasattr(selected, "name") else str(selected)
            self.app.grid, self.app.start, self.app.goal = load_map_from_dir(
                f"data/maps/{map_name}"
            )
            self.app.path = []
            self.status_text = f"Loaded: {map_name}"
            self.load_menu_open = False

    def _draw_load_menu(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(
            (self.app.window_width, self.app.window_height), pygame.SRCALPHA
        )
        overlay.fill((255, 255, 255, 210))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(280, 120, 520, 360)
        pygame.draw.rect(surface, PALETTE["panel"], panel, border_radius=12)

        title = pygame.font.Font(None, FONT_NORMAL).render(
            "Load Map", True, PALETTE["ink"]
        )
        surface.blit(title, (panel.x + 20, panel.y + 16))

        hint = pygame.font.Font(None, FONT_SMALL).render(
            "UP/DOWN to select, ENTER to load, Q or BACKSPACE to close",
            True,
            PALETTE["muted"],
        )
        surface.blit(hint, (panel.x + 20, panel.y + 48))

        if not self.map_choices:
            msg = pygame.font.Font(None, FONT_SMALL).render(
                "No saved maps found in data/maps", True, PALETTE["muted"]
            )
            surface.blit(msg, (panel.x + 20, panel.y + 100))
            return

        # Calculate pagination
        total_pages = (
            len(self.map_choices) + self.maps_per_page - 1
        ) // self.maps_per_page
        page_start = self.current_page * self.maps_per_page
        page_end = min(page_start + self.maps_per_page, len(self.map_choices))
        page_items = self.map_choices[page_start:page_end]

        y = panel.y + 90
        for idx, name in enumerate(page_items):
            global_idx = page_start + idx
            selected = global_idx == self.selected_map_idx
            if selected:
                pygame.draw.rect(
                    surface, (235, 235, 235), pygame.Rect(panel.x + 16, y - 4, 488, 28)
                )
            txt = pygame.font.Font(None, FONT_SMALL).render(
                str(name.name), True, PALETTE["ink"]
            )
            surface.blit(txt, (panel.x + 24, y))
            y += 30

        # Draw pagination info
        page_info = pygame.font.Font(None, FONT_SMALL).render(
            f"Page {self.current_page + 1}/{total_pages}",
            True,
            PALETTE["muted"],
        )
        surface.blit(page_info, (panel.x + 20, panel.y + 310))
