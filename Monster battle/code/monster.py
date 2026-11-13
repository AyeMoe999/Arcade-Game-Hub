import pygame
from settings import *
from support import create_monster_surface, calc_damage


class Monster(pygame.sprite.Sprite):
    def __init__(self, name, side, pos):
        super().__init__()
        data = MONSTER_DATA[name]
        self.name = name
        self.element = data['element']
        self.max_health = data['health']
        self.health = data['health']
        self.side = side
        self.abilities = ELEMENT_ABILITIES[self.element]
        self.image = create_monster_surface(name, self.element)
        self.rect = self.image.get_rect(center=pos)
        self.shake_timer = 0
        self.alpha = 255

    @property
    def fainted(self):
        return self.health <= 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.shake_timer = 0.25

    def heal_full(self):
        self.health = self.max_health

    def use_ability(self, ability_name, target):
        ability = ABILITIES_DATA[ability_name]
        multiplier = ELEMENT_DATA[ability['element']][target.element]
        damage = calc_damage(ability_name, self.element, target.element)
        target.take_damage(damage)
        return damage, multiplier, ability['animation']

    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            offset = 8 if int(self.shake_timer * 40) % 2 else -8
            self.rect.centerx = self.base_center[0] + offset
        else:
            self.rect.center = self.base_center

    def set_base_pos(self, pos):
        self.base_center = pos
        self.rect.center = pos
