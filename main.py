import os
import sys
import math
import random
import pygame

# Root directory path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from theme_manager import theme_manager

BASE_WIDTH, BASE_HEIGHT = 1280, 720
FPS = 60


def unload_game_modules():
    """
    Unloads game-specific modules from sys.modules so each game can load
    its own settings/support modules without namespace collisions.
    """
    modules_to_unload = ['settings', 'support', 'battle', 'monster', 'ui', 'timer', 'main', 'Ludo_game']
    for mod_name in list(sys.modules.keys()):
        for target in modules_to_unload:
            if mod_name == target or mod_name.startswith(target + '.'):
                del sys.modules[mod_name]


def launch_pong():
    pong_dir = os.path.join(ROOT_DIR, "code")
    os.chdir(pong_dir)
    unload_game_modules()
    if pong_dir not in sys.path:
        sys.path.insert(0, pong_dir)
    else:
        sys.path.remove(pong_dir)
        sys.path.insert(0, pong_dir)

    import main as pong_main
    pong_main.main()

    if pong_dir in sys.path:
        sys.path.remove(pong_dir)
    os.chdir(ROOT_DIR)
    unload_game_modules()


def launch_monster_battle():
    mb_dir = os.path.join(ROOT_DIR, "Monster battle", "code")
    os.chdir(mb_dir)
    unload_game_modules()
    if mb_dir not in sys.path:
        sys.path.insert(0, mb_dir)
    else:
        sys.path.remove(mb_dir)
        sys.path.insert(0, mb_dir)

    import main as mb_main
    game_instance = mb_main.Game()
    game_instance.run()

    if mb_dir in sys.path:
        sys.path.remove(mb_dir)
    os.chdir(ROOT_DIR)
    unload_game_modules()


def launch_ludo():
    ludo_dir = os.path.join(ROOT_DIR, "Ludo")
    os.chdir(ludo_dir)
    unload_game_modules()
    if ludo_dir not in sys.path:
        sys.path.insert(0, ludo_dir)
    else:
        sys.path.remove(ludo_dir)
        sys.path.insert(0, ludo_dir)

    pygame.display.quit()

    import Ludo_game
    theme_bg = theme_manager.get_theme()["ludo_bg"]
    Ludo_game.play_ludo(bg_color=theme_bg)

    if ludo_dir in sys.path:
        sys.path.remove(ludo_dir)
    os.chdir(ROOT_DIR)
    unload_game_modules()

    pygame.display.init()


# Custom Artwork Generators for Cards
def draw_pong_art(surface, rect, accent):
    """Draw a mini arcade Pong court visual preview."""
    art_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(art_surf, (10, 15, 25, 200), art_surf.get_rect(), border_radius=12)
    pygame.draw.rect(art_surf, (30, 45, 70), art_surf.get_rect(), 1, border_radius=12)

    # Center dashed line
    for y in range(8, rect.height - 8, 12):
        pygame.draw.line(art_surf, (50, 75, 110), (rect.width // 2, y), (rect.width // 2, y + 6), 2)

    # Left & Right Paddles
    pygame.draw.rect(art_surf, (0, 240, 255), (14, rect.height // 2 - 25, 8, 50), border_radius=4)
    pygame.draw.rect(art_surf, (255, 0, 128), (rect.width - 22, rect.height // 2 - 15, 8, 50), border_radius=4)

    # Ball & Motion trail
    for i in range(3):
        alpha = 60 + i * 50
        trail_pos = (rect.width // 2 - 20 + i * 12, rect.height // 2 - 10 + i * 6)
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 235, 50, alpha), (6, 6), 5)
        art_surf.blit(s, trail_pos)

    surface.blit(art_surf, rect.topleft)


def draw_ludo_art(surface, rect, accent):
    """Draw a mini Ludo board & dice visual preview."""
    art_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(art_surf, (12, 18, 28, 200), art_surf.get_rect(), border_radius=12)
    pygame.draw.rect(art_surf, (30, 45, 70), art_surf.get_rect(), 1, border_radius=12)

    # 4 Quadrants
    w, h = rect.width, rect.height
    qw, qh = w // 2 - 12, h // 2 - 12
    pygame.draw.rect(art_surf, (220, 50, 50), (10, 10, qw, qh), border_radius=6)
    pygame.draw.rect(art_surf, (50, 200, 80), (w // 2 + 2, 10, qw, qh), border_radius=6)
    pygame.draw.rect(art_surf, (0, 180, 255), (10, h // 2 + 2, qw, qh), border_radius=6)
    pygame.draw.rect(art_surf, (240, 200, 40), (w // 2 + 2, h // 2 + 2, qw, qh), border_radius=6)

    # Center Dice box
    dice_rect = pygame.Rect(w // 2 - 18, h // 2 - 18, 36, 36)
    pygame.draw.rect(art_surf, (255, 255, 255), dice_rect, border_radius=8)
    pygame.draw.rect(art_surf, (20, 30, 45), dice_rect, 2, border_radius=8)
    # Dice dots (5 pattern)
    dots = [dice_rect.center, (dice_rect.x + 8, dice_rect.y + 8), (dice_rect.right - 8, dice_rect.bottom - 8),
            (dice_rect.right - 8, dice_rect.y + 8), (dice_rect.x + 8, dice_rect.bottom - 8)]
    for dot in dots:
        pygame.draw.circle(art_surf, (20, 30, 45), dot, 3)

    surface.blit(art_surf, rect.topleft)


def draw_monster_art(surface, rect, accent):
    """Draw a mini Monster Battle arena visual preview."""
    art_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(art_surf, (15, 12, 28, 200), art_surf.get_rect(), border_radius=12)
    pygame.draw.rect(art_surf, (45, 30, 70), art_surf.get_rect(), 1, border_radius=12)

    # Pedestal
    w, h = rect.width, rect.height
    pygame.draw.ellipse(art_surf, (80, 40, 140), (w // 2 - 50, h - 35, 100, 24))
    pygame.draw.ellipse(art_surf, (140, 60, 220), (w // 2 - 40, h - 32, 80, 18), 2)

    # Creature Flame / Energy Aura
    cx, cy = w // 2, h // 2 - 5
    pygame.draw.circle(art_surf, (255, 140, 0, 140), (cx, cy), 28)
    pygame.draw.circle(art_surf, (255, 220, 0, 200), (cx, cy), 18)
    pygame.draw.circle(art_surf, (255, 255, 255), (cx, cy), 8)

    # Crossed Swords visual
    pygame.draw.line(art_surf, (220, 230, 245), (cx - 22, cy - 22), (cx + 22, cy + 22), 3)
    pygame.draw.line(art_surf, (220, 230, 245), (cx + 22, cy - 22), (cx - 22, cy + 22), 3)

    surface.blit(art_surf, rect.topleft)


# Game Instructions Data
PONG_INSTRUCTIONS = {
    "how_to_play": [
        "Classic high-speed table tennis arcade duel.",
        "Deflect the ball past your opponent's paddle to score points.",
        "First player to reach 7 points wins the match!"
    ],
    "controls": [
        ("Player 1 (Left)", "W / S keys"),
        ("Player 2 (Right)", "Up / Down Arrow keys"),
        ("Pause Game", "P or ESC key"),
        ("Quick Restart", "R key")
    ],
    "tip": "Hit the ball near paddle edges to strike steep angle shots!"
}

LUDO_INSTRUCTIONS = {
    "how_to_play": [
        "Traditional 1-4 player turn-based board game.",
        "Roll the dice and navigate all 4 tokens around the board.",
        "First player to bring all 4 tokens to the home center wins!"
    ],
    "controls": [
        ("Roll Dice", "Click Dice / Spacebar"),
        ("Move Token", "Click active Token"),
        ("Player Count", "Configure in Setup Screen")
    ],
    "tip": "Roll a 6 to bring a new token out of your home base into play!"
}

MONSTER_INSTRUCTIONS = {
    "how_to_play": [
        "Turn-based creature duel with elemental strategy.",
        "Choose your monster and exploit elemental weaknesses.",
        "Deplete the opponent's HP to achieve victory!"
    ],
    "controls": [
        ("Browse / Select", "Left / Right Arrow keys"),
        ("Confirm Attack", "ENTER key or Mouse Click"),
        ("Rematch / Exit", "R key / ESC key")
    ],
    "tip": "Fire 🔥 beats Grass 🌱, Water 💧 beats Fire 🔥, and Grass 🌱 beats Water 💧!"
}


class GameCard:
    def __init__(self, rect, icon_str, title, subtitle, desc, tags, instructions, art_fn, launch_fn):
        self.rect = pygame.Rect(rect)
        self.icon_str = icon_str
        self.title = title
        self.subtitle = subtitle
        self.desc = desc
        self.tags = tags
        self.instructions = instructions
        self.art_fn = art_fn
        self.launch_fn = launch_fn
        self.is_hovered = False
        self.is_focused = False
        self.is_pressed = False
        self.instr_btn_rect = pygame.Rect(self.rect.x + 20, self.rect.bottom - 96, self.rect.width - 40, 36)
        self.play_btn_rect = pygame.Rect(self.rect.x + 20, self.rect.bottom - 52, self.rect.width - 40, 40)

    def update(self, mouse_pos, mouse_down):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if not mouse_down:
            self.is_pressed = False

    def handle_click(self):
        self.launch_fn()

    def draw(self, surface, fonts, theme, virtual_mouse=(0, 0)):
        font_title, font_sub, font_body, font_tag = fonts
        active = self.is_hovered or self.is_focused

        # Dynamic Rect for hover lift & press down
        draw_rect = self.rect.copy()
        if self.is_pressed:
            draw_rect = draw_rect.inflate(-6, -6)
        elif active:
            draw_rect = draw_rect.move(0, -6)

        # Update absolute button rects based on draw_rect
        self.instr_btn_rect = pygame.Rect(draw_rect.x + 20, draw_rect.bottom - 96, draw_rect.width - 40, 36)
        self.play_btn_rect = pygame.Rect(draw_rect.x + 20, draw_rect.bottom - 52, draw_rect.width - 40, 40)

        # Card Shadow
        shadow_rect = draw_rect.move(0, 8 if active else 4)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90 if active else 50), shadow_surf.get_rect(), border_radius=20)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Card Background
        card_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        bg_col = theme['card_bg_hover'] if active else theme['card_bg']
        pygame.draw.rect(card_surf, bg_col, card_surf.get_rect(), border_radius=20)

        # Card Border & Top Accent Bar
        border_col = theme['card_border_hover'] if active else theme['card_border']
        border_w = 3 if active else 1
        pygame.draw.rect(card_surf, border_col, card_surf.get_rect(), border_w, border_radius=20)

        accent_bar_h = 6 if active else 4
        pygame.draw.rect(card_surf, theme['accent'], (0, 0, draw_rect.width, accent_bar_h),
                         border_top_left_radius=20, border_top_right_radius=20)

        surface.blit(card_surf, draw_rect.topleft)

        # Card Header: Icon + Title
        title_text = f"{self.icon_str} {self.title}"
        title_surf = font_title.render(title_text, True, theme['text_primary'])
        surface.blit(title_surf, (draw_rect.x + 20, draw_rect.y + 22))

        sub_surf = font_sub.render(self.subtitle, True, theme['accent'])
        surface.blit(sub_surf, (draw_rect.x + 20, draw_rect.y + 56))

        # Artwork Preview Area
        art_rect = pygame.Rect(draw_rect.x + 20, draw_rect.y + 88, draw_rect.width - 40, 130)
        self.art_fn(surface, art_rect, theme['accent'])

        # Description
        words = self.desc.split()
        lines = []
        curr_line = ""
        for word in words:
            test_line = f"{curr_line} {word}".strip()
            if font_body.size(test_line)[0] < (draw_rect.width - 40):
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = word
        if curr_line:
            lines.append(curr_line)

        for i, line in enumerate(lines[:3]):
            line_surf = font_body.render(line, True, theme['text_secondary'])
            surface.blit(line_surf, (draw_rect.x + 20, draw_rect.y + 226 + i * 18))

        # Tags
        tag_x = draw_rect.x + 20
        tag_y = draw_rect.y + 284
        for tag in self.tags:
            t_surf = font_tag.render(tag, True, theme['text_primary'])
            t_w = t_surf.get_width() + 14
            t_rect = pygame.Rect(tag_x, tag_y, t_w, 22)
            pygame.draw.rect(surface, theme['grid_line'], t_rect, border_radius=6)
            pygame.draw.rect(surface, theme['accent'] if active else theme['card_border'], t_rect, 1, border_radius=6)
            surface.blit(t_surf, (tag_x + 7, tag_y + 4))
            tag_x += t_w + 6

        # --- Instructions Button (Positioned above Play Game Button) ---
        instr_hover = self.instr_btn_rect.collidepoint(virtual_mouse)
        instr_bg = theme['card_bg_hover'] if instr_hover else theme['card_bg']
        pygame.draw.rect(surface, instr_bg, self.instr_btn_rect, border_radius=10)
        instr_border = theme['accent'] if instr_hover else theme['card_border']
        pygame.draw.rect(surface, instr_border, self.instr_btn_rect, 2 if instr_hover else 1, border_radius=10)
        
        instr_txt_col = theme['accent'] if instr_hover else theme['text_primary']
        instr_surf = font_sub.render("📖 Instructions", True, instr_txt_col)
        surface.blit(instr_surf, instr_surf.get_rect(center=self.instr_btn_rect.center))

        # --- Play Game Button Area ---
        play_hover = self.play_btn_rect.collidepoint(virtual_mouse)
        btn_bg = theme['button_bg'] if (active or play_hover) else theme['card_border']
        pygame.draw.rect(surface, btn_bg, self.play_btn_rect, border_radius=10)
        btn_txt = "▶ PLAY GAME" if (active or play_hover) else "SELECT GAME"
        btn_txt_col = theme['button_text'] if (active or play_hover) else theme['text_secondary']
        btn_surf = font_sub.render(btn_txt, True, btn_txt_col)
        surface.blit(btn_surf, btn_surf.get_rect(center=self.play_btn_rect.center))


def draw_instructions_modal(surface, card, fonts, theme, virtual_mouse):
    """Render semi-transparent overlay and interactive Instructions Modal for a game."""
    font_title, font_sub, font_body, font_tag = fonts

    # Dark backdrop overlay
    overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    surface.blit(overlay, (0, 0))

    # Modal Rect
    modal_w, modal_h = 600, 480
    modal_rect = pygame.Rect((BASE_WIDTH - modal_w) // 2, (BASE_HEIGHT - modal_h) // 2, modal_w, modal_h)

    # Modal Body & Border
    modal_bg = theme.get('pong_panel_bg', (18, 26, 42, 245))
    if isinstance(modal_bg, tuple) and len(modal_bg) == 4:
        s = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        pygame.draw.rect(s, modal_bg, s.get_rect(), border_radius=20)
        surface.blit(s, modal_rect.topleft)
    else:
        pygame.draw.rect(surface, modal_bg, modal_rect, border_radius=20)

    pygame.draw.rect(surface, theme['accent'], modal_rect, 2, border_radius=20)

    # Header Accent Bar
    pygame.draw.rect(surface, theme['accent'], (modal_rect.x, modal_rect.y, modal_w, 6),
                     border_top_left_radius=20, border_top_right_radius=20)

    # Header Text
    header_str = f"{card.icon_str}  {card.title} - Instructions"
    header_surf = font_title.render(header_str, True, theme['text_primary'])
    surface.blit(header_surf, (modal_rect.x + 24, modal_rect.y + 22))

    # Divider line
    pygame.draw.line(surface, theme['grid_line'], (modal_rect.x + 24, modal_rect.y + 60), (modal_rect.right - 24, modal_rect.y + 60), 1)

    info = card.instructions
    curr_y = modal_rect.y + 72

    # Section 1: How To Play
    sec1_title = font_sub.render("🎯 HOW TO PLAY", True, theme['accent'])
    surface.blit(sec1_title, (modal_rect.x + 24, curr_y))
    curr_y += 26

    for line in info.get("how_to_play", []):
        bullet_surf = font_body.render(f"•  {line}", True, theme['text_secondary'])
        surface.blit(bullet_surf, (modal_rect.x + 32, curr_y))
        curr_y += 20

    curr_y += 12

    # Section 2: Controls
    sec2_title = font_sub.render("🎮 CONTROLS & KEY BINDINGS", True, theme['accent'])
    surface.blit(sec2_title, (modal_rect.x + 24, curr_y))
    curr_y += 26

    for ctrl_label, ctrl_key in info.get("controls", []):
        ctrl_rect = pygame.Rect(modal_rect.x + 32, curr_y, modal_w - 64, 28)
        c_bg = (30, 42, 65, 200) if isinstance(theme['card_bg'], tuple) else theme['card_bg']
        pygame.draw.rect(surface, c_bg, ctrl_rect, border_radius=6)
        pygame.draw.rect(surface, theme['grid_line'], ctrl_rect, 1, border_radius=6)

        lbl_surf = font_body.render(ctrl_label, True, theme['text_primary'])
        surface.blit(lbl_surf, (ctrl_rect.x + 12, ctrl_rect.centery - lbl_surf.get_height() // 2))

        key_surf = font_body.render(ctrl_key, True, theme['accent_secondary'])
        surface.blit(key_surf, (ctrl_rect.right - 12 - key_surf.get_width(), ctrl_rect.centery - key_surf.get_height() // 2))

        curr_y += 32

    # Section 3: Pro Tip
    if "tip" in info:
        curr_y += 8
        tip_surf = font_body.render(f"💡 {info['tip']}", True, theme['text_muted'])
        surface.blit(tip_surf, (modal_rect.x + 24, curr_y))

    # Close Button
    close_btn_rect = pygame.Rect(modal_rect.centerx - 90, modal_rect.bottom - 54, 180, 40)
    close_hover = close_btn_rect.collidepoint(virtual_mouse)

    close_bg = theme['button_bg'] if close_hover else theme['card_border']
    pygame.draw.rect(surface, close_bg, close_btn_rect, border_radius=10)
    close_txt_col = theme['button_text'] if close_hover else theme['text_primary']
    close_surf = font_sub.render("Got It! Close", True, close_txt_col)
    surface.blit(close_surf, close_surf.get_rect(center=close_btn_rect.center))

    return close_btn_rect, modal_rect


def restore_launcher():
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Arcade Game Hub")
    pygame.event.clear()
    pygame.time.wait(100)
    pygame.event.clear()
    return screen


def run_launcher():
    screen = restore_launcher()
    clock = pygame.time.Clock()

    virtual_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    # Fonts
    font_header = pygame.font.Font(None, 56)
    font_subhead = pygame.font.Font(None, 24)
    font_title = pygame.font.Font(None, 32)
    font_sub = pygame.font.Font(None, 22)
    font_body = pygame.font.Font(None, 20)
    font_tag = pygame.font.Font(None, 16)
    fonts = (font_title, font_sub, font_body, font_tag)

    cards = [
        GameCard((60, 160, 360, 480), "🏓", "Pong", "Classic two-player arcade",
                 "Classic high-speed Pong arena with game theory stats, zero-sum rally tracking, and state controls.",
                 ["2 Players", "Arcade", "Strategy"], PONG_INSTRUCTIONS, draw_pong_art, launch_pong),
        GameCard((460, 160, 360, 480), "🎲", "Ludo", "Classic board game",
                 "Traditional multi-player Ludo board game featuring animated dice rolls and turn management.",
                 ["1-4 Players", "Board Game", "Classic"], LUDO_INSTRUCTIONS, draw_ludo_art, launch_ludo),
        GameCard((860, 160, 360, 480), "⚔️", "Monster Battle", "Battle powerful monsters",
                 "Turn-based creature duel with elemental strengths, damage multipliers, and unique abilities.",
                 ["1 Player", "RPG Duel", "Turn-Based"], MONSTER_INSTRUCTIONS, draw_monster_art, launch_monster_battle),
    ]

    focused_index = 0
    active_instructions_card = None
    running = True

    while running:
        if not pygame.display.get_init():
            screen = restore_launcher()

        theme = theme_manager.get_theme()
        dt = clock.tick(FPS) / 1000.0

        # Calculate virtual mouse coordinates (scaled to 1280x720)
        win_w, win_h = screen.get_size()
        real_mouse_pos = pygame.mouse.get_pos()
        virtual_mouse = (
            int(real_mouse_pos[0] * BASE_WIDTH / max(1, win_w)),
            int(real_mouse_pos[1] * BASE_HEIGHT / max(1, win_h))
        )
        mouse_down = pygame.mouse.get_pressed()[0]

        # Theme Switcher Button Rect (Top Right)
        theme_btn_rect = pygame.Rect(BASE_WIDTH - 240, 35, 180, 40)
        theme_btn_hover = theme_btn_rect.collidepoint(virtual_mouse)

        # Update hover & focus states
        for i, card in enumerate(cards):
            card.is_hovered = card.rect.collidepoint(virtual_mouse)
            card.is_focused = (i == focused_index)
            card.update(virtual_mouse, mouse_down)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if active_instructions_card is not None:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_q):
                        active_instructions_card = None
                else:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        focused_index = (focused_index + 1) % len(cards)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        focused_index = (focused_index - 1) % len(cards)
                    elif event.key == pygame.K_t:
                        theme_manager.cycle_theme()
                    elif event.key == pygame.K_i:
                        active_instructions_card = cards[focused_index]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_fn = cards[focused_index].launch_fn
                        game_fn()
                        screen = restore_launcher()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if active_instructions_card is not None:
                    # Close modal if clicking close button or outside modal
                    close_btn_rect, modal_rect = draw_instructions_modal(virtual_surface, active_instructions_card, fonts, theme, virtual_mouse)
                    if close_btn_rect.collidepoint(virtual_mouse) or not modal_rect.collidepoint(virtual_mouse):
                        active_instructions_card = None
                else:
                    # Theme button click
                    if theme_btn_rect.collidepoint(virtual_mouse):
                        theme_manager.cycle_theme()
                    else:
                        for i, card in enumerate(cards):
                            if card.instr_btn_rect.collidepoint(virtual_mouse):
                                focused_index = i
                                active_instructions_card = card
                                break
                            elif card.play_btn_rect.collidepoint(virtual_mouse) or card.rect.collidepoint(virtual_mouse):
                                focused_index = i
                                card.is_pressed = True
                                card.handle_click()
                                screen = restore_launcher()
                                break

        # ---------------- RENDER ARCADE HUB TO VIRTUAL SURFACE ----------------
        # Background Gradient
        top_c, bot_c = theme['bg_gradient_top'], theme['bg_gradient_bottom']
        for y in range(0, BASE_HEIGHT, 4):
            r = int(top_c[0] * (1 - y / BASE_HEIGHT) + bot_c[0] * (y / BASE_HEIGHT))
            g = int(top_c[1] * (1 - y / BASE_HEIGHT) + bot_c[1] * (y / BASE_HEIGHT))
            b = int(top_c[2] * (1 - y / BASE_HEIGHT) + bot_c[2] * (y / BASE_HEIGHT))
            pygame.draw.rect(virtual_surface, (r, g, b), (0, y, BASE_WIDTH, 4))

        # Ambient Grid Lines
        for x in range(0, BASE_WIDTH, 40):
            pygame.draw.line(virtual_surface, theme['grid_line'], (x, 0), (x, BASE_HEIGHT), 1)
        for y in range(0, BASE_HEIGHT, 40):
            pygame.draw.line(virtual_surface, theme['grid_line'], (0, y), (BASE_WIDTH, y), 1)

        # Header Title & Subtitle
        title_surf = font_header.render("ARCADE GAME HUB", True, theme['text_primary'])
        virtual_surface.blit(title_surf, (60, 30))

        sub_surf = font_subhead.render("Choose your game to play  |  Use Mouse or Arrows + Enter", True, theme['text_secondary'])
        virtual_surface.blit(sub_surf, (60, 85))

        # Theme Switcher Pill Button
        theme_bg = theme['card_bg_hover'] if theme_btn_hover else theme['card_bg']
        pygame.draw.rect(virtual_surface, theme_bg, theme_btn_rect, border_radius=12)
        theme_border = theme['accent'] if theme_btn_hover else theme['card_border']
        pygame.draw.rect(virtual_surface, theme_border, theme_btn_rect, 2 if theme_btn_hover else 1, border_radius=12)

        theme_txt = f"{theme['icon']} {theme['name']}"
        t_surf = font_subhead.render(theme_txt, True, theme['text_primary'])
        virtual_surface.blit(t_surf, t_surf.get_rect(center=theme_btn_rect.center))

        # Render 3 Game Cards
        for card in cards:
            card.draw(virtual_surface, fonts, theme, virtual_mouse)

        # Render Instructions Modal if active
        if active_instructions_card is not None:
            draw_instructions_modal(virtual_surface, active_instructions_card, fonts, theme, virtual_mouse)

        # Footer
        footer_surf = font_subhead.render("Press T to Switch Theme  |  Press I for Instructions  |  Press ESC to Exit", True, theme['text_muted'])
        virtual_surface.blit(footer_surf, footer_surf.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 25)))

        # ---------------- SCALING VIRTUAL SURFACE TO SCREEN ----------------
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (win_w, win_h))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    run_launcher()
