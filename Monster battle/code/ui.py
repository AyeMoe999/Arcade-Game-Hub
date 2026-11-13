import pygame
from settings import *
from support import color


class Button:
    def __init__(self, rect, text, font, callback=None, enabled=True, element=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.enabled = enabled
        self.hovered = False
        self.element = element

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface):
        # Shadow
        shadow_rect = self.rect.move(0, 4)
        pygame.draw.rect(surface, (10, 14, 24, 180), shadow_rect, border_radius=10)

        # Base Color
        if self.enabled:
            if self.hovered:
                bg = pygame.Color('#1f4068')
                border = pygame.Color('#00d4ff')
            else:
                bg = color('panel')
                border = pygame.Color('#40536f')
        else:
            bg = pygame.Color('#222831')
            border = pygame.Color('#393e46')

        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 2 if not self.hovered else 3, border_radius=10)

        # Highlight Top Edge for 3D Bevel look
        if self.enabled:
            highlight_color = (255, 255, 255, 50 if not self.hovered else 100)
            highlight_surf = pygame.Surface((self.rect.width - 4, 3), pygame.SRCALPHA)
            highlight_surf.fill(highlight_color)
            surface.blit(highlight_surf, (self.rect.x + 2, self.rect.y + 2))

        # Text Label
        text_color = color('white') if self.enabled else color('gray')
        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def set_enabled(self, enabled):
        self.enabled = enabled


class HealthBar:
    def __init__(self, rect, max_health, label_font):
        self.rect = pygame.Rect(rect)
        self.max_health = max_health
        self.health = max_health
        self.target_health = max_health
        self.label_font = label_font

    def set_health(self, health, max_health=None):
        self.target_health = max(0, health)
        if max_health is not None:
            self.max_health = max_health

    def update(self, dt):
        # Smooth HP transition
        if self.health != self.target_health:
            diff = self.target_health - self.health
            step = diff * 8 * dt
            if abs(step) < 0.2:
                self.health = self.target_health
            else:
                self.health += step

    def draw(self, surface, name, element):
        # Header Badge
        elem_color = ELEMENT_COLORS.get(element, color('white'))
        name_surf = self.label_font.render(f"{name}", True, color('white'))
        surface.blit(name_surf, (self.rect.x, self.rect.y - 28))

        # Element Tag Badge
        badge_rect = pygame.Rect(self.rect.x + name_surf.get_width() + 10, self.rect.y - 28, 64, 22)
        pygame.draw.rect(surface, elem_color, badge_rect, border_radius=6)
        tag_surf = pygame.font.Font(None, 20).render(element.upper(), True, color('black'))
        surface.blit(tag_surf, tag_surf.get_rect(center=badge_rect.center))

        # Outer Frame
        pygame.draw.rect(surface, color('black'), self.rect.inflate(4, 4), border_radius=8)
        pygame.draw.rect(surface, pygame.Color('#2c3e50'), self.rect, border_radius=6)

        inner = self.rect.inflate(-4, -4)
        ratio = 0 if self.max_health == 0 else max(0.0, min(1.0, self.health / self.max_health))
        fill_width = max(0, int(inner.width * ratio))
        fill_rect = pygame.Rect(inner.x, inner.y, fill_width, inner.height)

        # Dynamic Health Bar Gradient Color
        if ratio > 0.5:
            bar_color = color('plant')
        elif ratio > 0.25:
            bar_color = color('yellow')
        else:
            bar_color = color('red')

        if fill_width > 0:
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=4)
            # Top Shine Line
            shine = pygame.Surface((fill_width, fill_rect.height // 2), pygame.SRCALPHA)
            shine.fill((255, 255, 255, 60))
            surface.blit(shine, fill_rect.topleft)

        # Border
        pygame.draw.rect(surface, color('white'), self.rect, 1, border_radius=6)

        # HP Numbers
        hp_text = self.label_font.render(f"{int(self.health)} / {self.max_health}", True, color('white'))
        surface.blit(hp_text, hp_text.get_rect(center=self.rect.center))


class MessageLog:
    def __init__(self, rect, font):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.lines = []

    def add(self, text):
        self.lines.append(text)
        if len(self.lines) > 4:
            self.lines.pop(0)

    def draw(self, surface):
        # Panel Background
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        panel_surf.fill((15, 25, 45, 230))
        surface.blit(panel_surf, self.rect.topleft)

        pygame.draw.rect(surface, pygame.Color('#40536f'), self.rect, 2, border_radius=10)

        for i, line in enumerate(self.lines):
            # Highlight damage or outcome text
            if "used" in line:
                c = pygame.Color('#ffea00')
            elif "effective" in line or "fainted" in line:
                c = pygame.Color('#00d4ff')
            else:
                c = color('white')

            text_surf = self.font.render(line, True, c)
            surface.blit(text_surf, (self.rect.x + 16, self.rect.y + 12 + i * 28))

