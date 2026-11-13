import os
import sys
import pygame

# Ensure root dir is in sys.path for importing theme_manager
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from theme_manager import theme_manager

BASE_WIDTH, BASE_HEIGHT = 1280, 720
WINDOW_WIDTH, WINDOW_HEIGHT = BASE_WIDTH, BASE_HEIGHT
FPS = 60

SIZE = {'paddle': (30, 110), 'ball': (26, 26)}
POS = {'player': (WINDOW_WIDTH - 50, WINDOW_HEIGHT / 2), 'opponent': (50, WINDOW_HEIGHT / 2)}
SPEED = {'player': 560, 'opponent': 250, 'ball': 480}

def get_pong_colors():
    theme = theme_manager.get_theme()
    return {
        'bg_top': theme['pong_bg_top'],
        'bg_bottom': theme['pong_bg_bottom'],
        'grid': theme['pong_grid'],
        'line': theme['pong_line'],
        'center_circle': theme['pong_center_circle'],
        'paddle_left': theme['pong_paddle_left'],
        'paddle_right': theme['pong_paddle_right'],
        'paddle_shadow': theme['pong_paddle_shadow'],
        'ball': theme['pong_ball'],
        'ball_glow': theme['pong_ball_glow'],
        'score_bg': theme['pong_score_bg'],
        'score_text': theme['pong_score_text'],
        'panel_bg': theme['pong_panel_bg'],
        'panel_border': theme['pong_panel_border'],
        'accent': theme['accent'],
        'accent_secondary': theme['accent_secondary'],
        'button_bg': theme.get('button_bg', theme['accent']),
        'button_text': theme.get('button_text', (10, 15, 25)),
        'button_hover': theme.get('button_hover', theme['accent']),
        'text_primary': theme['text_primary'],
        'text_secondary': theme['text_secondary'],
        'text_muted': theme['text_muted'],
    }