"""
Two-player Pong with Arcade UI Redesign, Responsive Scaling, and Game Theory Stats.

Controls:
    Left Paddle: W / S
    Right Paddle: Up / Down arrows
    ESC / P: Pause match
    R: Quick Restart
"""

import math
import random
import sys
import os
import pygame

# Ensure settings and theme_manager are accessible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from settings import BASE_WIDTH, BASE_HEIGHT, FPS, POS, SIZE, SPEED, get_pong_colors

WINNING_SCORE = 7
PADDLE_MARGIN = 32


class Particle:
    """Subtle floating background particle for arcade visual depth."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, BASE_WIDTH)
        self.y = random.uniform(0, BASE_HEIGHT)
        self.speed = random.uniform(15, 45)
        self.size = random.uniform(1.5, 3.5)
        self.alpha = random.uniform(40, 140)

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -10:
            self.y = BASE_HEIGHT + 10
            self.x = random.uniform(0, BASE_WIDTH)

    def draw(self, surface, color):
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        if hasattr(color, 'r'):
            r, g, b = color.r, color.g, color.b
        else:
            r, g, b = color[0], color[1], color[2]
        c = (r, g, b, int(self.alpha))
        pygame.draw.circle(s, c, (int(self.size), int(self.size)), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class Button:
    """Interactive arcade rounded button with hover and active animation."""
    def __init__(self, rect, text, callback, primary=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.primary = primary
        self.is_hovered = False
        self.is_pressed = False

    def update(self, mouse_pos, mouse_down):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if not mouse_down and self.is_pressed and self.is_hovered:
            self.is_pressed = False
            if self.callback:
                self.callback()
        elif not mouse_down:
            self.is_pressed = False

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_pressed = True

    def draw(self, surface, font, colors):
        bg_col = colors['accent'] if (self.primary or self.is_hovered) else colors['score_bg']
        if self.is_pressed:
            draw_rect = self.rect.inflate(-4, -4)
        elif self.is_hovered:
            draw_rect = self.rect.inflate(4, 4)
        else:
            draw_rect = self.rect.copy()

        # Shadow
        shadow_rect = draw_rect.move(0, 4)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=12)

        # Button Body
        pygame.draw.rect(surface, bg_col, draw_rect, border_radius=12)
        border_col = colors['accent'] if self.is_hovered else colors['line']
        pygame.draw.rect(surface, border_col, draw_rect, 2, border_radius=12)

        # Text
        btn_txt_color = colors.get('button_text', colors['text_primary'])
        txt_col = btn_txt_color if (self.primary or self.is_hovered) else colors['text_primary']
        txt_surf = font.render(self.text, True, txt_col)
        surface.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))


def reset_ball(ball, direction=None):
    """Place ball in center and give it initial velocity."""
    ball.center = (BASE_WIDTH // 2, BASE_HEIGHT // 2)
    horizontal = direction if direction is not None else random.choice((-1, 1))
    vertical = random.choice((-0.45, -0.25, 0.25, 0.45))
    return pygame.Vector2(horizontal * SPEED["ball"], vertical * SPEED["ball"])


def move_paddle(paddle, movement, delta_time, speed):
    paddle.y += movement * speed * delta_time
    paddle.top = max(paddle.top, 20)
    paddle.bottom = min(paddle.bottom, BASE_HEIGHT - 20)


def shot_category(offset):
    if offset < -0.33:
        return "High"
    if offset > 0.33:
        return "Low"
    return "Center"


def strategy_text(shots):
    total = sum(shots.values())
    if not total:
        return "H --%  C --%  L --%"
    return "  ".join(f"{name[0]} {shots[name] / total:.0%}" for name in ("High", "Center", "Low"))


def draw_gradient_bg(surface, top_color, bottom_color):
    """Draw a smooth 2-stop vertical gradient background."""
    height = surface.get_height()
    width = surface.get_width()
    for y in range(0, height, 4):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.rect(surface, (r, g, b), (0, y, width, 4))


def main():
    pygame.init()
    # Support window resizing while maintaining internal base resolution scaling
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Arcade Pong Arena")
    clock = pygame.time.Clock()

    virtual_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    # Fonts
    font_large_score = pygame.font.Font(None, 84)
    font_title = pygame.font.Font(None, 48)
    font_sub = pygame.font.Font(None, 26)
    font_info = pygame.font.Font(None, 22)

    # Game Objects
    paddle_width, paddle_height = SIZE["paddle"]
    left_paddle = pygame.Rect(PADDLE_MARGIN, (BASE_HEIGHT - paddle_height) // 2, paddle_width, paddle_height)
    right_paddle = pygame.Rect(BASE_WIDTH - PADDLE_MARGIN - paddle_width, (BASE_HEIGHT - paddle_height) // 2, paddle_width, paddle_height)
    ball = pygame.Rect(0, 0, *SIZE["ball"])
    ball_velocity = reset_ball(ball)

    # Scores & Stats
    left_score = 0
    right_score = 0
    winner = None
    left_shots = {"High": 0, "Center": 0, "Low": 0}
    right_shots = {"High": 0, "Center": 0, "Low": 0}

    # State Machine: 'READY', 'COUNTDOWN', 'PLAYING', 'PAUSED', 'GAME_OVER'
    state = 'COUNTDOWN'
    countdown_timer = 3.0

    # Audio Initialization & BGM Setup
    sound_effects = {}
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Mixer init error: {e}")

    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
    bgm_path = os.path.join(audio_dir, "pong_bgm.wav")

    if pygame.mixer.get_init():
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"BGM playback error: {e}")

        # Load sound effects
        for sfx_name in ['hit', 'wall', 'score']:
            sfx_path = os.path.join(audio_dir, f"{sfx_name}.wav")
            if os.path.exists(sfx_path):
                try:
                    sound_effects[sfx_name] = pygame.mixer.Sound(sfx_path)
                    sound_effects[sfx_name].set_volume(0.5)
                except Exception:
                    pass

    def play_sfx(name):
        if name in sound_effects:
            try:
                sound_effects[name].play()
            except Exception:
                pass

    # Background Particles
    particles = [Particle() for _ in range(35)]

    # Dynamic Buttons for Overlays
    def resume_game():
        nonlocal state
        if state == 'PAUSED':
            state = 'PLAYING'

    def restart_game():
        nonlocal left_score, right_score, winner, ball_velocity, left_shots, right_shots, state, countdown_timer
        left_score = right_score = 0
        winner = None
        ball_velocity = reset_ball(ball)
        left_shots = {"High": 0, "Center": 0, "Low": 0}
        right_shots = {"High": 0, "Center": 0, "Low": 0}
        state = 'COUNTDOWN'
        countdown_timer = 3.0

    def return_to_main_menu():
        nonlocal running
        running = False

    pause_buttons = [
        Button((BASE_WIDTH // 2 - 140, BASE_HEIGHT // 2 - 40, 280, 50), "RESUME", resume_game, primary=True),
        Button((BASE_WIDTH // 2 - 140, BASE_HEIGHT // 2 + 25, 280, 50), "RESTART", restart_game),
        Button((BASE_WIDTH // 2 - 140, BASE_HEIGHT // 2 + 90, 280, 50), "MAIN MENU", return_to_main_menu),
    ]

    gameover_buttons = [
        Button((BASE_WIDTH // 2 - 140, BASE_HEIGHT // 2 + 30, 280, 50), "PLAY AGAIN", restart_game, primary=True),
        Button((BASE_WIDTH // 2 - 140, BASE_HEIGHT // 2 + 95, 280, 50), "MAIN MENU", return_to_main_menu),
    ]

    running = True

    while running:
        colors = get_pong_colors()
        dt = clock.tick(FPS) / 1000.0

        # Calculate logical mouse position on virtual 1280x720 surface
        win_w, win_h = screen.get_size()
        real_mouse_pos = pygame.mouse.get_pos()
        virtual_mouse = (
            int(real_mouse_pos[0] * BASE_WIDTH / max(1, win_w)),
            int(real_mouse_pos[1] * BASE_HEIGHT / max(1, win_h))
        )
        mouse_down = pygame.mouse.get_pressed()[0]

        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    if state == 'PLAYING':
                        state = 'PAUSED'
                    elif state == 'PAUSED':
                        state = 'PLAYING'
                elif event.key == pygame.K_r:
                    restart_game()

            # Pass mouse events to relevant state overlay buttons
            if state == 'PAUSED':
                for btn in pause_buttons:
                    btn.handle_event(event, virtual_mouse)
            elif state == 'GAME_OVER':
                for btn in gameover_buttons:
                    btn.handle_event(event, virtual_mouse)

        # Update Buttons
        if state == 'PAUSED':
            for btn in pause_buttons:
                btn.update(virtual_mouse, mouse_down)
        elif state == 'GAME_OVER':
            for btn in gameover_buttons:
                btn.update(virtual_mouse, mouse_down)

        # Update Countdown
        if state == 'COUNTDOWN':
            countdown_timer -= dt
            if countdown_timer <= 0:
                state = 'PLAYING'

        # Gameplay Logic
        keys = pygame.key.get_pressed()
        if state == 'PLAYING':
            move_paddle(left_paddle, keys[pygame.K_s] - keys[pygame.K_w], dt, SPEED["player"])
            move_paddle(right_paddle, keys[pygame.K_DOWN] - keys[pygame.K_UP], dt, SPEED["player"])

            ball.x += round(ball_velocity.x * dt)
            ball.y += round(ball_velocity.y * dt)

            # Top & Bottom Bounce
            if ball.top <= 10 or ball.bottom >= BASE_HEIGHT - 10:
                ball_velocity.y *= -1
                ball.top = max(ball.top, 10)
                ball.bottom = min(ball.bottom, BASE_HEIGHT - 10)
                play_sfx('wall')

            # Paddle Collision
            hit_paddle = left_paddle if ball_velocity.x < 0 else right_paddle
            if ball.colliderect(hit_paddle):
                ball_velocity.x *= -1.05  # Slight rally speed increase
                offset = (ball.centery - hit_paddle.centery) / (paddle_height / 2)
                shots = left_shots if hit_paddle == left_paddle else right_shots
                shots[shot_category(offset)] += 1
                ball_velocity.y = offset * SPEED["ball"]
                if hit_paddle == left_paddle:
                    ball.left = left_paddle.right
                else:
                    ball.right = right_paddle.left
                play_sfx('hit')

            # Scoring
            if ball.right < 0:
                right_score += 1
                play_sfx('score')
                if right_score >= WINNING_SCORE:
                    winner = "PLAYER 2 WINS!"
                    state = 'GAME_OVER'
                else:
                    ball_velocity = reset_ball(ball, direction=-1)
                    state = 'COUNTDOWN'
                    countdown_timer = 2.0
            elif ball.left > BASE_WIDTH:
                left_score += 1
                play_sfx('score')
                if left_score >= WINNING_SCORE:
                    winner = "PLAYER 1 WINS!"
                    state = 'GAME_OVER'
                else:
                    ball_velocity = reset_ball(ball, direction=1)
                    state = 'COUNTDOWN'
                    countdown_timer = 2.0

        # Update Background Particles
        for particle in particles:
            particle.update(dt)

        # ---------------- RENDER PONG ARENA TO VIRTUAL SURFACE ----------------
        # Gradient Background
        draw_gradient_bg(virtual_surface, colors['bg_top'], colors['bg_bottom'])

        # Draw Grid & Particles
        for particle in particles:
            particle.draw(virtual_surface, colors['line'])

        grid_spacing = 50
        for x in range(0, BASE_WIDTH, grid_spacing):
            pygame.draw.line(virtual_surface, colors['grid'], (x, 0), (x, BASE_HEIGHT), 1)
        for y in range(0, BASE_HEIGHT, grid_spacing):
            pygame.draw.line(virtual_surface, colors['grid'], (0, y), (BASE_WIDTH, y), 1)

        # Outer Court Arena Border
        arena_rect = pygame.Rect(16, 16, BASE_WIDTH - 32, BASE_HEIGHT - 32)
        pygame.draw.rect(virtual_surface, colors['line'], arena_rect, 2, border_radius=16)

        # Center Dashed Line & Circle Pitch
        pygame.draw.circle(virtual_surface, colors['center_circle'], (BASE_WIDTH // 2, BASE_HEIGHT // 2), 70, 2)
        pygame.draw.circle(virtual_surface, colors['line'], (BASE_WIDTH // 2, BASE_HEIGHT // 2), 6, 0)
        for y in range(24, BASE_HEIGHT - 24, 20):
            pygame.draw.line(virtual_surface, colors['line'], (BASE_WIDTH // 2, y), (BASE_WIDTH // 2, y + 10), 3)

        # Draw Paddles with Shadow & Neon Accent
        # Left Paddle
        l_shadow = left_paddle.move(4, 4)
        pygame.draw.rect(virtual_surface, colors['paddle_shadow'], l_shadow, border_radius=8)
        pygame.draw.rect(virtual_surface, colors['paddle_left'], left_paddle, border_radius=8)
        pygame.draw.rect(virtual_surface, (255, 255, 255), left_paddle.inflate(-6, -6), 1, border_radius=6)

        # Right Paddle
        r_shadow = right_paddle.move(4, 4)
        pygame.draw.rect(virtual_surface, colors['paddle_shadow'], r_shadow, border_radius=8)
        pygame.draw.rect(virtual_surface, colors['paddle_right'], right_paddle, border_radius=8)
        pygame.draw.rect(virtual_surface, (255, 255, 255), right_paddle.inflate(-6, -6), 1, border_radius=6)

        # Draw Ball & Glow
        ball_glow = pygame.Surface((SIZE["ball"][0] + 16, SIZE["ball"][1] + 16), pygame.SRCALPHA)
        pygame.draw.ellipse(ball_glow, colors['ball_glow'], ball_glow.get_rect())
        virtual_surface.blit(ball_glow, ball_glow.get_rect(center=ball.center))
        pygame.draw.ellipse(virtual_surface, colors['ball'], ball)
        pygame.draw.ellipse(virtual_surface, (255, 255, 255), ball.inflate(-6, -6), 1)

        # ---------------- SCORE & HUD DISPLAY ----------------
        # Header Score Boxes
        # Player 1 Header Card
        p1_card = pygame.Rect(BASE_WIDTH // 2 - 270, 30, 200, 70)
        pygame.draw.rect(virtual_surface, colors['score_bg'], p1_card, border_radius=14)
        pygame.draw.rect(virtual_surface, colors['paddle_left'], p1_card, 2, border_radius=14)
        p1_label = font_info.render("PLAYER 1  (W/S)", True, colors['paddle_left'])
        virtual_surface.blit(p1_label, p1_label.get_rect(center=(p1_card.centerx, p1_card.y + 18)))
        p1_score_surf = font_large_score.render(f"{left_score:02d}", True, colors['score_text'])
        virtual_surface.blit(p1_score_surf, p1_score_surf.get_rect(center=(p1_card.centerx, p1_card.y + 46)))

        # VS Divider
        vs_surf = font_title.render("VS", True, colors['line'])
        virtual_surface.blit(vs_surf, vs_surf.get_rect(center=(BASE_WIDTH // 2, 65)))

        # Player 2 Header Card
        p2_card = pygame.Rect(BASE_WIDTH // 2 + 70, 30, 200, 70)
        pygame.draw.rect(virtual_surface, colors['score_bg'], p2_card, border_radius=14)
        pygame.draw.rect(virtual_surface, colors['paddle_right'], p2_card, 2, border_radius=14)
        p2_label = font_info.render("PLAYER 2  (UP/DOWN)", True, colors['paddle_right'])
        virtual_surface.blit(p2_label, p2_label.get_rect(center=(p2_card.centerx, p2_card.y + 18)))
        p2_score_surf = font_large_score.render(f"{right_score:02d}", True, colors['score_text'])
        virtual_surface.blit(p2_score_surf, p2_score_surf.get_rect(center=(p2_card.centerx, p2_card.y + 46)))

        # Bottom Game Theory Strategy Stats HUD
        stats_rect = pygame.Rect(BASE_WIDTH // 2 - 380, BASE_HEIGHT - 55, 760, 40)
        pygame.draw.rect(virtual_surface, colors['score_bg'], stats_rect, border_radius=10)
        pygame.draw.rect(virtual_surface, colors['line'], stats_rect, 1, border_radius=10)

        p1_strat = font_info.render(f"P1 Strategy: {strategy_text(left_shots)}", True, colors['paddle_left'])
        virtual_surface.blit(p1_strat, (stats_rect.x + 20, stats_rect.centery - p1_strat.get_height() // 2))

        p2_strat = font_info.render(f"P2 Strategy: {strategy_text(right_shots)}", True, colors['paddle_right'])
        virtual_surface.blit(p2_strat, (stats_rect.right - 20 - p2_strat.get_width(), stats_rect.centery - p2_strat.get_height() // 2))

        # ---------------- GAME STATE BANNERS & OVERLAYS ----------------
        if state == 'COUNTDOWN':
            cnt_val = max(1, math.ceil(countdown_timer))
            banner_rect = pygame.Rect(BASE_WIDTH // 2 - 120, BASE_HEIGHT // 2 - 40, 240, 80)
            pygame.draw.rect(virtual_surface, colors['panel_bg'], banner_rect, border_radius=16)
            pygame.draw.rect(virtual_surface, colors['accent'], banner_rect, 2, border_radius=16)
            cnt_surf = font_large_score.render(f"{cnt_val}", True, colors['accent'])
            virtual_surface.blit(cnt_surf, cnt_surf.get_rect(center=banner_rect.center))

        elif state == 'PAUSED':
            # Darkened overlay
            overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            virtual_surface.blit(overlay, (0, 0))

            # Pause Modal
            modal_rect = pygame.Rect(BASE_WIDTH // 2 - 180, BASE_HEIGHT // 2 - 140, 360, 310)
            pygame.draw.rect(virtual_surface, colors['panel_bg'], modal_rect, border_radius=20)
            pygame.draw.rect(virtual_surface, colors['panel_border'], modal_rect, 2, border_radius=20)

            title_surf = font_title.render("GAME PAUSED", True, colors['text_primary'])
            virtual_surface.blit(title_surf, title_surf.get_rect(center=(modal_rect.centerx, modal_rect.y + 45)))

            for btn in pause_buttons:
                btn.draw(virtual_surface, font_sub, colors)

        elif state == 'GAME_OVER':
            # Darkened overlay
            overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            virtual_surface.blit(overlay, (0, 0))

            # Victory Modal
            modal_rect = pygame.Rect(BASE_WIDTH // 2 - 200, BASE_HEIGHT // 2 - 140, 400, 310)
            pygame.draw.rect(virtual_surface, colors['panel_bg'], modal_rect, border_radius=20)
            pygame.draw.rect(virtual_surface, colors['panel_border'], modal_rect, 3, border_radius=20)

            win_color = colors['paddle_left'] if "1" in winner else colors['paddle_right']
            win_surf = font_large_score.render(winner, True, win_color)
            virtual_surface.blit(win_surf, win_surf.get_rect(center=(modal_rect.centerx, modal_rect.y + 60)))

            for btn in gameover_buttons:
                btn.draw(virtual_surface, font_sub, colors)

        # ---------------- SCALING VIRTUAL SURFACE TO SCREEN ----------------
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (win_w, win_h))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    # On exit loop, cleanly stop BGM and return to launcher
    if pygame.mixer.get_init():
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    return


if __name__ == "__main__":
    main()
