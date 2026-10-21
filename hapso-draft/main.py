from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from ui.compare_result_screen import CompareResultScreen
from ui.compare_weight_screen import CompareWeightScreen
from ui.map_editor_screen import MapEditorScreen
from ui.simulation_screen import SimulationScreen


def create_empty_grid(width: int, height: int) -> list[list[int]]:
    return [[0 for _ in range(width)] for _ in range(height)]


@dataclass
class AppState:
    window_width: int = 1100
    window_height: int = 600
    grid_width: int = 20
    grid_height: int = 20
    cell_size: int = 20
    grid: list[list[int]] = field(default_factory=lambda: create_empty_grid(20, 20))
    start: tuple[int, int] | None = None
    goal: tuple[int, int] | None = None
    path: list[tuple[int, int]] = field(default_factory=list)


class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("HAPSO Path Planning Studio")

        self.state = AppState()
        self.screen = pygame.display.set_mode(
            (self.state.window_width, self.state.window_height)
        )
        self.clock = pygame.time.Clock()

        self.screens = {
            "editor": MapEditorScreen(self.state),
            "sim": SimulationScreen(self.state),
            "weight": CompareWeightScreen(self.state),
            "result": CompareResultScreen(self.state),
        }
        self.current_key = "editor"
        self.running = True

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    self.current_key = "editor"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                    self.current_key = "sim"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.current_key = "weight"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                    self.current_key = "result"

                self.screens[self.current_key].handle_event(event)

            self.screens[self.current_key].update()
            self.screens[self.current_key].draw(self.screen)
            self._draw_nav()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _draw_nav(self) -> None:
        font = pygame.font.Font(None, 24)
        nav_text = "F1: Map | F2: Simulation | F3: Weight Compare | F4: Result Compare | ESC: Quit"
        label = font.render(nav_text, True, (0, 0, 0))
        x = (self.screen.get_width() - label.get_width()) // 2
        self.screen.blit(label, (x, 10))
        # Draw border-bottom for nav
        pygame.draw.line(
            self.screen, (0, 0, 0), (0, 40), (self.screen.get_width(), 40), 2
        )


if __name__ == "__main__":
    App().run()
