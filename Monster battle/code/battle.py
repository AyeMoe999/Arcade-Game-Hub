import random
import math
import pygame
from os import walk
from os.path import join
from settings import *
from support import color, effectiveness_text, draw_element_pedestal, draw_battleground_environment, audio_importer
from monster import Monster
from ui import Button, HealthBar, MessageLog
from timer import Timer

class AttackParticle:
    def __init__(self, start_pos, target_pos, anim_type):
        self.pos = list(start_pos)
        self.start_pos = list(start_pos)
        self.target_pos = list(target_pos)
        self.anim_type = anim_type
        self.progress = 0.0
        self.speed = 2.5
        self.alive = True

    def update(self, dt):
        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.progress = 1.0
            self.alive = False

        # Curved motion trajectory
        dx = self.target_pos[0] - self.start_pos[0]
        dy = self.target_pos[1] - self.start_pos[1]
        arc = math.sin(self.progress * math.pi) * -40.0
        self.pos[0] = self.start_pos[0] + dx * self.progress
        self.pos[1] = self.start_pos[1] + dy * self.progress + arc

    def draw(self, surface):
        px, py = int(self.pos[0]), int(self.pos[1])
        if self.anim_type == 'fire' or self.anim_type == 'explosion':
            for r, c in [(14, (255, 60, 0, 160)), (8, (255, 180, 0, 220)), (4, (255, 255, 200, 255))]:
                ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, c, (r, r), r)
                surface.blit(ps, (px - r, py - r))
        elif self.anim_type == 'splash' or self.anim_type == 'ice':
            for r, c in [(14, (0, 140, 255, 160)), (8, (0, 220, 255, 220)), (4, (220, 255, 255, 255))]:
                ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, c, (r, r), r)
                surface.blit(ps, (px - r, py - r))
        elif self.anim_type == 'green':
            for r, c in [(14, (40, 180, 70, 160)), (8, (120, 240, 80, 220)), (4, (220, 255, 140, 255))]:
                ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, c, (r, r), r)
                surface.blit(ps, (px - r, py - r))
        else:
            for r, c in [(10, (220, 220, 220, 180)), (5, (255, 255, 255, 255))]:
                ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, c, (r, r), r)
                surface.blit(ps, (px - r, py - r))


class Battle:
    PLAYER_POS = (320, 420)
    ENEMY_POS = (960, 220)

    def __init__(self, display_surface, fonts, player_name, enemy_name):
        self.display_surface = display_surface
        self.title_font, self.ui_font, self.small_font = fonts
        self.state = 'intro'
        self.player_monster = Monster(player_name, 'player', self.PLAYER_POS)
        self.enemy_monster = Monster(enemy_name, 'enemy', self.ENEMY_POS)
        self.player_monster.set_base_pos(self.PLAYER_POS)
        self.enemy_monster.set_base_pos(self.ENEMY_POS)

        self.all_sprites = pygame.sprite.Group(self.player_monster, self.enemy_monster)
        self.player_bar = HealthBar((80, 580, 320, 28), self.player_monster.max_health, self.small_font)
        self.enemy_bar = HealthBar((880, 80, 320, 28), self.enemy_monster.max_health, self.small_font)
        self.log = MessageLog((80, 640, 720, 60), self.small_font)

        self.ability_buttons = []
        self._build_ability_buttons()
        self.intro_timer = Timer(1200, func=self._start_player_turn)
        self.intro_timer.activate()
        self.enemy_timer = Timer(1400, func=self._finish_enemy_turn)
        self.result = None
        self.flash_timer = 0
        self.flash_color = None
        self.particles = []

        # Audio setup
        self.sounds = {}
        self._setup_audio()

        self.log.add(f"A wild {enemy_name} appeared!")
        self.log.add(f"Go, {player_name}!")

    def _setup_audio(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass

        if pygame.mixer.get_init():
            # Background Music
            music_path = join('..', 'audio', 'music.mp3') if walk(join('..', 'audio')) else join('audio', 'music.mp3')
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

            # Sound Effects
            audio_dir = join('..', 'audio') if walk(join('..', 'audio')) else 'audio'
            try:
                self.sounds = audio_importer(audio_dir)
            except Exception:
                self.sounds = {}

    def _play_sound(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].set_volume(0.65)
                self.sounds[sound_name].play()
            except Exception:
                pass

    def _build_ability_buttons(self):
        self.ability_buttons.clear()
        abilities = self.player_monster.abilities
        start_x, start_y = 840, 520
        for i, ability in enumerate(abilities):
            col = i % 2
            row = i // 2
            rect = (start_x + col * 210, start_y + row * 70, 200, 58)
            ab_data = ABILITIES_DATA.get(ability, {})
            ab_elem = ab_data.get('element', 'normal')
            btn = Button(rect, ability.title(), self.ui_font, callback=lambda a=ability: self._player_attack(a), element=ab_elem)
            self.ability_buttons.append(btn)

    def _set_buttons_enabled(self, enabled):
        for btn in self.ability_buttons:
            btn.set_enabled(enabled)

    def _start_player_turn(self):
        if self.result:
            return
        self.state = 'player_turn'
        self._set_buttons_enabled(True)
        self.log.add("Choose an ability.")

    def _player_attack(self, ability_name):
        if self.state != 'player_turn':
            return
        self._set_buttons_enabled(False)
        self.state = 'animating'

        attacker = self.player_monster
        defender = self.enemy_monster
        damage, multiplier, animation = attacker.use_ability(ability_name, defender)
        self.player_bar.set_health(attacker.health)
        self.enemy_bar.set_health(defender.health)
        self._trigger_flash(animation)
        self.particles.append(AttackParticle(self.PLAYER_POS, self.ENEMY_POS, animation))
        self._play_sound(animation)

        self.log.add(f"{attacker.name} used {ability_name.title()}!")
        self.log.add(f"Dealt {damage} damage. {effectiveness_text(multiplier)}")

        if defender.fainted:
            self.state = 'finished'
            self.result = 'win'
            self._play_sound('explosion')
            self.log.add(f"{defender.name} fainted! You win!")
            return

        self.state = 'enemy_turn'
        self.enemy_timer.activate()

    def _finish_enemy_turn(self):
        if self.result:
            return
        abilities = self.enemy_monster.abilities
        ability_name = random.choice(abilities)
        attacker = self.enemy_monster
        defender = self.player_monster
        damage, multiplier, animation = attacker.use_ability(ability_name, defender)
        self.player_bar.set_health(defender.health)
        self.enemy_bar.set_health(attacker.health)
        self._trigger_flash(animation)
        self.particles.append(AttackParticle(self.ENEMY_POS, self.PLAYER_POS, animation))
        self._play_sound(animation)

        self.log.add(f"Enemy {attacker.name} used {ability_name.title()}!")
        self.log.add(f"Dealt {damage} damage. {effectiveness_text(multiplier)}")

        if defender.fainted:
            self.state = 'finished'
            self.result = 'lose'
            self._play_sound('scratch')
            self.log.add(f"{defender.name} fainted! You lose...")
            return

        self._start_player_turn()

    def _trigger_flash(self, animation):
        flash_map = {
            'fire': color('fire'),
            'splash': color('water'),
            'ice': color('water'),
            'green': color('plant'),
            'explosion': color('red'),
            'scratch': color('normal'),
        }
        self.flash_color = flash_map.get(animation, color('white'))
        self.flash_timer = 0.15

    def handle_event(self, event):
        if self.state == 'player_turn':
            for btn in self.ability_buttons:
                btn.handle_event(event)

    def update(self, dt):
        self.intro_timer.update()
        self.enemy_timer.update()
        self.all_sprites.update(dt)
        self.player_bar.update(dt)
        self.enemy_bar.update(dt)

        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self._play_sound('scratch')
                self.particles.remove(p)

        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self):
        # 1. Playful Fantasy Forest & Mountain Environment Background
        self.display_surface.fill(color('black'))
        draw_battleground_environment(self.display_surface, WINDOW_WIDTH, WINDOW_HEIGHT - 140)

        # Header Title Banner Overlay for crystal clear readability
        header_banner = pygame.Surface((380, 48), pygame.SRCALPHA)
        header_banner.fill((10, 18, 34, 210))
        pygame.draw.rect(header_banner, pygame.Color('#40536f'), header_banner.get_rect(), 2, border_radius=10)
        self.display_surface.blit(header_banner, (WINDOW_WIDTH // 2 - 190, 8))

        title = self.title_font.render("Monster Battle", True, color('yellow'))
        self.display_surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 12))

        # Bottom Command Console Surface
        pygame.draw.rect(self.display_surface, color('panel'), (0, WINDOW_HEIGHT - 140, WINDOW_WIDTH, 140))
        pygame.draw.line(self.display_surface, pygame.Color('#40536f'), (0, WINDOW_HEIGHT - 140), (WINDOW_WIDTH, WINDOW_HEIGHT - 140), 3)

        # 2. Draw 3D Battle Rings / Pedestals under monsters
        draw_element_pedestal(self.display_surface, (self.PLAYER_POS[0], self.PLAYER_POS[1] + 60), self.player_monster.element, 100, 32)
        draw_element_pedestal(self.display_surface, (self.ENEMY_POS[0], self.ENEMY_POS[1] + 60), self.enemy_monster.element, 100, 32)

        # 3. Draw Monsters & Particles
        self.all_sprites.draw(self.display_surface)

        for p in self.particles:
            p.draw(self.display_surface)

        # 4. Draw UI Bars & Log
        self.player_bar.draw(self.display_surface, self.player_monster.name, self.player_monster.element)
        self.enemy_bar.draw(self.display_surface, self.enemy_monster.name, self.enemy_monster.element)
        self.log.draw(self.display_surface)

        for btn in self.ability_buttons:
            btn.draw(self.display_surface)

        # 5. Screen Flash on Attack Hit
        if self.flash_timer > 0 and self.flash_color:
            flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.flash_color[:3], 60))
            self.display_surface.blit(flash, (0, 0))

        # 6. Victory / Defeat Overlay
        if self.result:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.display_surface.blit(overlay, (0, 0))
            msg = "Victory! Press R to rematch or ESC for menu." if self.result == 'win' else "Defeat! Press R to rematch or ESC for menu."
            text = self.ui_font.render(msg, True, color('yellow') if self.result == 'win' else color('red'))
            self.display_surface.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

