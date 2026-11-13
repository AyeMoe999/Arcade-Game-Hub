import random
import pygame
from settings import *
from support import color, create_monster_surface, draw_element_pedestal
from battle import Battle


class TeamSelect:
    def __init__(self, display_surface, fonts):
        self.display_surface = display_surface
        self.title_font, self.ui_font, self.small_font = fonts
        self.monster_names = list(MONSTER_DATA.keys())
        self.index = 0
        self.preview_size = 260

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.index = (self.index + 1) % len(self.monster_names)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.index = (self.index - 1) % len(self.monster_names)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.monster_names[self.index]
        return None

    def draw(self):
        self.display_surface.fill(color('black'))

        # Background grid overlay for real game feel
        for x in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(self.display_surface, (18, 24, 38), (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(self.display_surface, (18, 24, 38), (0, y), (WINDOW_WIDTH, y), 1)

        name = self.monster_names[self.index]
        data = MONSTER_DATA[name]

        title = self.title_font.render("CHOOSE YOUR MONSTER", True, color('yellow'))
        self.display_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))

        # Keep the three elemental fighters visible during selection
        for i, element in enumerate(('water', 'fire', 'plant')):
            x = WINDOW_WIDTH // 2 - 170 + i * 170
            selected = element == data['element']
            card = pygame.Rect(x - 70, 90, 140, 100)
            card_fill = pygame.Color('#1b2838') if selected else pygame.Color('#101726')
            pygame.draw.rect(self.display_surface, card_fill, card, border_radius=14)

            border_col = color(element) if selected else pygame.Color('#32435e')
            pygame.draw.rect(
                self.display_surface,
                border_col,
                card,
                3 if selected else 1,
                border_radius=14,
            )
            icon = create_monster_surface(element, element, 68)
            self.display_surface.blit(icon, icon.get_rect(center=(x, 128)))
            label = self.small_font.render(element.upper(), True, color('white') if selected else color('gray'))
            self.display_surface.blit(label, label.get_rect(center=(x, 172)))

        # Preview Pedestal & Monster
        preview_pos = (WINDOW_WIDTH // 2, 350)
        draw_element_pedestal(self.display_surface, (preview_pos[0], preview_pos[1] + 80), data['element'], 130, 40)

        preview = create_monster_surface(name, data['element'], self.preview_size)
        preview_rect = preview.get_rect(center=preview_pos)
        self.display_surface.blit(preview, preview_rect)

        # Info Box
        info_lines = [
            f"--- {name} ---",
            f"Element: {data['element'].title()}",
            f"Health: {data['health']}",
            f"Abilities: {', '.join(a.title() for a in ELEMENT_ABILITIES[data['element']])}",
        ]
        for i, line in enumerate(info_lines):
            c = color('yellow') if i == 0 else color('white')
            surf = self.ui_font.render(line, True, c)
            self.display_surface.blit(surf, surf.get_rect(center=(WINDOW_WIDTH // 2, 500 + i * 36)))

        hint = self.small_font.render("← → to browse  |  ENTER to battle  |  ESC to quit", True, color('gray'))
        self.display_surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 684)))


def play_bg_music():
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception:
            return
    try:
        if not pygame.mixer.music.get_busy():
            music_path = join('..', 'audio', 'music.mp3') if walk(join('..', 'audio')) else join('audio', 'music.mp3')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Music error: {e}")


def stop_bg_music():
    if pygame.mixer.get_init():
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        except Exception:
            pass


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'
        self.battle = None
        self.player_monster = None

        self.title_font = pygame.font.Font(None, 72)
        self.ui_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.fonts = (self.title_font, self.ui_font, self.small_font)
        self.team_select = TeamSelect(self.display_surface, self.fonts)

    def _random_enemy(self, exclude):
        choices = [name for name in MONSTER_DATA if name != exclude]
        return random.choice(choices)

    def _start_battle(self, player_name):
        self.player_monster = player_name
        enemy_name = self._random_enemy(player_name)
        self.battle = Battle(self.display_surface, self.fonts, player_name, enemy_name)
        self.state = 'battle'

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = 'select'
                play_bg_music()
            elif event.key == pygame.K_ESCAPE:
                self.running = False
                stop_bg_music()

    def _handle_battle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = 'select'
                self.battle = None
                play_bg_music()
            elif event.key == pygame.K_r and self.battle and self.battle.result:
                self._start_battle(self.player_monster)
        if self.battle:
            self.battle.handle_event(event)

    def run(self):
        if self.state == 'select':
            play_bg_music()

        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    stop_bg_music()
                elif self.state == 'menu':
                    self._handle_menu_event(event)
                elif self.state == 'select':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        stop_bg_music()
                    else:
                        chosen = self.team_select.handle_event(event)
                        if chosen:
                            self._start_battle(chosen)
                elif self.state == 'battle':
                    self._handle_battle_event(event)

            if self.state == 'battle' and self.battle:
                self.battle.update(dt)
                self.battle.draw()
            elif self.state == 'select':
                self.team_select.draw()
            else:
                self.display_surface.fill(color('black'))
                title = self.title_font.render("Monster Battle", True, color('yellow'))
                self.display_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 220)))
                subtitle = self.ui_font.render("Turn-based elemental combat", True, color('white'))
                self.display_surface.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 300)))
                hint = self.small_font.render("Press ENTER to start  |  ESC to quit", True, color('gray'))
                self.display_surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 400)))

            pygame.display.update()

        stop_bg_music()


if __name__ == '__main__':
    game = Game()
    game.run()

