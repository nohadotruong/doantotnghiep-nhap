from __future__ import annotations

import pygame


FONT_SMALL = 24
FONT_NORMAL = 24
FONT_LARGE = 24


PALETTE = {
    "bg": (255, 255, 255),
    "panel": (255, 255, 255),
    "ink": (0, 0, 0),
    "muted": (0, 0, 0),
    "accent": (0, 0, 0),
    "accent_soft": (255, 255, 255),
    "grid": (185, 185, 185),
    "obstacle": (0, 0, 0),
    "start": (39, 163, 108),
    "goal": (216, 73, 60),
    "path": (53, 112, 201),
}


class Button:
    def __init__(self, rect: pygame.Rect, text: str, key_hint: str) -> None:
        self.rect = rect
        self.text = text
        self.key_hint = key_hint

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, PALETTE["accent_soft"], self.rect)
        pygame.draw.rect(surface, PALETTE["accent"], self.rect, 2)
        label = font.render(f"{self.text} [{self.key_hint}]", True, PALETTE["ink"])
        surface.blit(label, (self.rect.x + 8, self.rect.y + 8))


class TextInput:
    def __init__(self, rect: pygame.Rect, label: str, text: str) -> None:
        self.rect = rect
        self.label = label
        self.text = text
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key == pygame.K_RETURN:
                self.active = False
                return False

            if event.unicode and event.unicode in "0123456789.-":
                self.text += event.unicode
                return True

        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        label_surface = font.render(self.label, True, PALETTE["ink"])
        surface.blit(label_surface, (self.rect.x, self.rect.y - 18))

        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, PALETTE["accent"], self.rect, 2)

        value_surface = font.render(self.text, True, PALETTE["ink"])
        surface.blit(value_surface, (self.rect.x + 8, self.rect.y + 6))

    def get_int(self, fallback: int) -> int:
        try:
            return int(float(self.text))
        except ValueError:
            return fallback

    def get_float(self, fallback: float) -> float:
        try:
            return float(self.text)
        except ValueError:
            return fallback


def draw_title(
    surface: pygame.Surface, title: str, subtitle: str, start_y: int = 60
) -> None:
    title_font = pygame.font.Font(None, FONT_LARGE)
    sub_font = pygame.font.Font(None, FONT_NORMAL)
    # start_y: position for title (default 60 = content_top 40 + padding 20)
    surface.blit(title_font.render(title, True, PALETTE["ink"]), (21, start_y))
    surface.blit(sub_font.render(subtitle, True, PALETTE["muted"]), (21, start_y + 24))
