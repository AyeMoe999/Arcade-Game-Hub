"""
Central Theme Configuration System for Arcade Game Hub & Suite.
Supports extensible themes: Dark (Neon Arcade), Light (Clean Modern), and Retro (80s Synthwave).
"""

import pygame

THEMES = {
    "dark": {
        "name": "Dark Neon",
        "icon": "🌙",
        # Hub colors
        "bg_gradient_top": (15, 22, 36),
        "bg_gradient_bottom": (8, 11, 20),
        "grid_line": (24, 34, 52),
        "card_bg": (22, 30, 46, 235),
        "card_bg_hover": (30, 42, 65, 245),
        "card_border": (45, 62, 92),
        "card_border_hover": (0, 240, 255),
        "accent": (0, 240, 255),          # Neon Cyan
        "accent_secondary": (255, 0, 128),# Neon Pink
        "text_primary": (255, 255, 255),
        "text_secondary": (150, 175, 205),
        "text_muted": (100, 120, 145),
        "button_bg": (0, 240, 255),
        "button_text": (10, 15, 25),
        "button_hover": (60, 245, 255),
        # Pong UI colors
        "pong_bg_top": (12, 18, 30),
        "pong_bg_bottom": (6, 9, 16),
        "pong_grid": (20, 30, 48),
        "pong_line": (40, 60, 95),
        "pong_center_circle": (35, 55, 85),
        "pong_paddle_left": (0, 240, 255),    # Cyan
        "pong_paddle_right": (255, 0, 128),   # Pink
        "pong_paddle_shadow": (0, 120, 130),
        "pong_ball": (255, 235, 50),          # Bright yellow/gold
        "pong_ball_glow": (255, 235, 50, 60),
        "pong_score_bg": (18, 26, 42, 220),
        "pong_score_text": (255, 255, 255),
        "pong_panel_bg": (15, 22, 36, 240),
        "pong_panel_border": (0, 240, 255),
        # Ludo theme
        "ludo_bg": "#121826",
    },
    "light": {
        "name": "Clean Light",
        "icon": "☀️",
        # Hub colors
        "bg_gradient_top": (242, 246, 252),
        "bg_gradient_bottom": (218, 226, 240),
        "grid_line": (210, 220, 235),
        "card_bg": (255, 255, 255, 240),
        "card_bg_hover": (255, 255, 255, 255),
        "card_border": (195, 208, 228),
        "card_border_hover": (35, 110, 235),
        "accent": (35, 110, 235),          # Vibrant Blue
        "accent_secondary": (235, 85, 45),  # Coral Red
        "text_primary": (25, 35, 55),
        "text_secondary": (90, 108, 132),
        "text_muted": (140, 155, 175),
        "button_bg": (35, 110, 235),
        "button_text": (255, 255, 255),
        "button_hover": (60, 130, 250),
        # Pong UI colors
        "pong_bg_top": (238, 243, 250),
        "pong_bg_bottom": (215, 225, 240),
        "pong_grid": (205, 218, 235),
        "pong_line": (175, 192, 215),
        "pong_center_circle": (185, 200, 222),
        "pong_paddle_left": (35, 110, 235),   # Blue
        "pong_paddle_right": (235, 85, 45),   # Coral
        "pong_paddle_shadow": (20, 70, 160),
        "pong_ball": (255, 140, 0),           # Dark Orange
        "pong_ball_glow": (255, 140, 0, 60),
        "pong_score_bg": (255, 255, 255, 230),
        "pong_score_text": (25, 35, 55),
        "pong_panel_bg": (255, 255, 255, 245),
        "pong_panel_border": (35, 110, 235),
        # Ludo theme
        "ludo_bg": "#eef3fa",
    },
    "retro": {
        "name": "80s Retro",
        "icon": "🕹️",
        # Hub colors
        "bg_gradient_top": (28, 6, 38),
        "bg_gradient_bottom": (12, 2, 18),
        "grid_line": (65, 15, 85),
        "card_bg": (42, 12, 54, 235),
        "card_bg_hover": (56, 16, 72, 245),
        "card_border": (180, 20, 150),
        "card_border_hover": (255, 230, 0),
        "accent": (255, 230, 0),           # Arcade Gold / Yellow
        "accent_secondary": (255, 0, 130), # Magenta
        "text_primary": (255, 255, 255),
        "text_secondary": (225, 160, 255),
        "text_muted": (155, 100, 185),
        "button_bg": (255, 230, 0),
        "button_text": (20, 0, 30),
        "button_hover": (255, 245, 100),
        # Pong UI colors
        "pong_bg_top": (24, 5, 32),
        "pong_bg_bottom": (10, 1, 16),
        "pong_grid": (60, 12, 75),
        "pong_line": (120, 25, 140),
        "pong_center_circle": (100, 20, 120),
        "pong_paddle_left": (255, 230, 0),    # Arcade Gold
        "pong_paddle_right": (255, 0, 130),   # Neon Magenta
        "pong_paddle_shadow": (140, 110, 0),
        "pong_ball": (0, 255, 200),           # Neon Cyan / Mint
        "pong_ball_glow": (0, 255, 200, 60),
        "pong_score_bg": (45, 10, 58, 230),
        "pong_score_text": (255, 255, 255),
        "pong_panel_bg": (38, 8, 48, 245),
        "pong_panel_border": (255, 230, 0),
        # Ludo theme
        "ludo_bg": "#1f062a",
    }
}


class ThemeManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.current_theme_key = "dark"
        return cls._instance

    def set_theme(self, theme_key):
        if theme_key in THEMES:
            self.current_theme_key = theme_key

    def get_current_key(self):
        return self.current_theme_key

    def get_theme(self):
        return THEMES[self.current_theme_key]

    def cycle_theme(self):
        keys = list(THEMES.keys())
        idx = keys.index(self.current_theme_key)
        self.current_theme_key = keys[(idx + 1) % len(keys)]
        return self.current_theme_key

    def get_color(self, color_key):
        theme = self.get_theme()
        val = theme.get(color_key, (255, 255, 255))
        if isinstance(val, tuple):
            return pygame.Color(*val)
        return val


theme_manager = ThemeManager()
