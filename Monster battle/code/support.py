from settings import *
import math

# Simple surface cache for high performance
_SURFACE_CACHE = {}


def folder_importer(*path):
    surfs = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            surfs[file_name.split('.')[0]] = pygame.image.load(full_path).convert_alpha()
    return surfs


def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            audio_dict[file_name.split('.')[0]] = pygame.mixer.Sound(join(folder_path, file_name))
    return audio_dict


def color(name):
    value = COLORS[name]
    if value.startswith('#'):
        return pygame.Color(value)
    return pygame.Color(value)


def _pt(size, x, y):
    """Convert 0-100 illustration coordinates to the requested sprite size."""
    return (round(size * x / 100), round(size * y / 100))


def _polygon(surf, points, fill, outline=None, width=0):
    pts = [_pt(surf.get_width(), x, y) for x, y in points]
    pygame.draw.polygon(surf, fill, pts)
    if outline:
        pygame.draw.polygon(surf, outline, pts, width)


def _circle(surf, fill, x, y, radius, outline=None, width=0):
    size = surf.get_width()
    pygame.draw.circle(surf, fill, _pt(size, x, y), max(1, round(size * radius / 100)))
    if outline:
        pygame.draw.circle(surf, outline, _pt(size, x, y), max(1, round(size * radius / 100)), width)


def _line(surf, fill, points, width=1):
    size = surf.get_width()
    pts = [_pt(size, x, y) for x, y in points]
    pygame.draw.lines(surf, fill, False, pts, max(1, round(size * width / 100)))


def _draw_glow(surf, center_xy, radius_pct, color_rgba):
    """Draw a smooth radial glow aura behind combatants."""
    size = surf.get_width()
    cx, cy = _pt(size, center_xy[0], center_xy[1])
    r_max = round(size * radius_pct / 100)
    glow_surf = pygame.Surface((r_max * 2, r_max * 2), pygame.SRCALPHA)
    cr, cg, cb, ca = color_rgba
    for r in range(r_max, 0, -2):
        alpha = int(ca * (r / r_max) ** 1.8)
        pygame.draw.circle(glow_surf, (cr, cg, cb, alpha), (r_max, r_max), r)
    surf.blit(glow_surf, (cx - r_max, cy - r_max))


def _draw_war_eye(surf, x, y, eye_color='#ffea00', glow_color='#ff4500'):
    """Fierce battle eye with inner glow and outer light highlight."""
    # Outer socket shadow
    _circle(surf, '#0a0d14', x, y, 7)
    # Glowing eye core
    _circle(surf, glow_color, x, y, 5)
    _circle(surf, eye_color, x, y, 3)
    # Bright center slit/spot
    _circle(surf, '#ffffff', x - 0.8, y - 0.8, 1.3)


def _draw_fire_fighter(surf, name=""):
    """
    Fire War Elemental: Molten obsidian berserker with custom horns, wings, drill,
    or armor variations for each specific monster.
    """
    # 1. Burning Flame Aura
    _draw_glow(surf, (50, 50), 45, (255, 80, 0, 90))
    _draw_glow(surf, (50, 45), 30, (255, 200, 0, 110))

    # Colors
    obsidian = '#1a0b0b'
    dark_magma = '#5e0b04'
    bright_red = '#dc2f02'
    orange_fire = '#ff6d00'
    gold_flame = '#ffb703'
    white_core = '#fff7d6'

    # Monster-specific Horn & Crest Variations
    if name == 'Cindrill':
        # Massive central drill horn
        _polygon(surf, [(43, 26), (50, -4), (57, 26)], gold_flame, obsidian, 2)
        _polygon(surf, [(46, 22), (50, 2), (54, 22)], white_core)
    elif name == 'Sparchu':
        # Twin curved lightning flame horns
        _polygon(surf, [(30, 28), (12, 8), (34, 18)], bright_red, obsidian, 2)
        _polygon(surf, [(70, 28), (88, 8), (66, 18)], bright_red, obsidian, 2)
        _polygon(surf, [(30, 24), (16, 12), (32, 18)], gold_flame)
        _polygon(surf, [(70, 24), (84, 12), (68, 18)], gold_flame)
    elif name == 'Atrox' or name == 'Jacana':
        # Sweeping flame wings
        _polygon(surf, [(22, 38), (-2, 16), (26, 48)], bright_red, obsidian, 2)
        _polygon(surf, [(78, 38), (102, 16), (74, 48)], bright_red, obsidian, 2)
        _polygon(surf, [(20, 36), (2, 20), (24, 44)], gold_flame)
        _polygon(surf, [(80, 36), (98, 20), (76, 44)], gold_flame)
    else:
        # Standard Flame Horns
        for horn in [
            [(24, 38), (14, 18), (32, 28)],
            [(32, 28), (28, 6), (44, 20)],
            [(44, 20), (50, 2), (56, 20)],
            [(56, 20), (72, 6), (68, 28)],
            [(68, 28), (86, 18), (76, 38)],
        ]:
            _polygon(surf, horn, bright_red, obsidian, max(1, surf.get_width() // 70))
            scaled_horn = [(p[0] * 0.9 + 5, p[1] * 0.9 + 4) for p in horn]
            _polygon(surf, scaled_horn, gold_flame)

    # 3. Muscular Molten Legs & Lower Body
    _polygon(surf, [(30, 65), (18, 86), (28, 95), (42, 88), (44, 72)], dark_magma, obsidian, 2)
    _polygon(surf, [(70, 65), (82, 86), (72, 95), (58, 88), (56, 72)], dark_magma, obsidian, 2)

    # Charmadillo Shell Carapace overlay
    if name == 'Charmadillo':
        _circle(surf, dark_magma, 50, 62, 26, obsidian, 2)
        _line(surf, orange_fire, [(30, 62), (50, 52), (70, 62)], 4)
        _line(surf, gold_flame, [(34, 68), (50, 58), (66, 68)], 3)

    # Feet Claws
    _polygon(surf, [(18, 86), (10, 96), (24, 98), (28, 92)], obsidian)
    _polygon(surf, [(82, 86), (90, 96), (76, 98), (72, 92)], obsidian)
    _line(surf, orange_fire, [(12, 94), (16, 88)], 3)
    _line(surf, orange_fire, [(88, 94), (84, 88)], 3)

    # 4. Heavy Molten Torso & Shoulder Armor
    _circle(surf, dark_magma, 50, 52, 28, obsidian, max(1, surf.get_width() // 55))
    _circle(surf, bright_red, 50, 50, 24)
    # Magma Chest Veins
    _line(surf, gold_flame, [(50, 36), (44, 48), (56, 56), (50, 66)], 4)
    _line(surf, white_core, [(50, 38), (45, 46), (54, 54)], 2)

    # Shoulder Pads (Jagged Obsidian Rocks)
    sh_w = 4 if name == 'Cindrill' else 2
    _polygon(surf, [(22, 42), (8 if name == 'Cindrill' else 10, 30), (18, 52), (32, 54)], obsidian, dark_magma, sh_w)
    _polygon(surf, [(78, 42), (92 if name == 'Cindrill' else 90, 30), (82, 52), (68, 54)], obsidian, dark_magma, sh_w)

    # 5. Flaming Battle Claws & Arm Stance
    # Left Arm
    _line(surf, dark_magma, [(28, 48), (14, 58), (10, 72)], 9)
    _line(surf, orange_fire, [(28, 48), (14, 58), (10, 72)], 4)
    _circle(surf, obsidian, 10, 74, 9, bright_red, 2)
    _polygon(surf, [(10, 74), (2, 70), (4, 82)], gold_flame)
    _polygon(surf, [(10, 74), (6, 84), (14, 86)], gold_flame)

    # Right Arm
    _line(surf, dark_magma, [(72, 48), (86, 58), (90, 72)], 9)
    _line(surf, orange_fire, [(72, 48), (86, 58), (90, 72)], 4)
    _circle(surf, obsidian, 90, 74, 9, bright_red, 2)
    _polygon(surf, [(90, 74), (98, 70), (96, 82)], gold_flame)
    _polygon(surf, [(90, 74), (94, 84), (86, 86)], gold_flame)

    # 6. Fiery Head Mask & Helmet Crest
    _polygon(surf, [(34, 38), (50, 18), (66, 38), (58, 48), (42, 48)], obsidian, dark_magma, 2)
    _polygon(surf, [(40, 28), (50, 20), (60, 28), (54, 38), (46, 38)], bright_red)
    _polygon(surf, [(44, 25), (50, 21), (56, 25)], gold_flame)

    # 7. Glowing Battle Eyes & Mouth Vent
    _draw_war_eye(surf, 43, 34, '#ffffff', '#ffea00')
    _draw_war_eye(surf, 57, 34, '#ffffff', '#ffea00')

    # Jagged mouth vent
    _polygon(surf, [(42, 42), (46, 46), (50, 43), (54, 46), (58, 42), (50, 48)], obsidian)
    _polygon(surf, [(44, 43), (47, 45), (50, 44), (53, 45), (56, 43)], gold_flame)

    # 8. Floating Ember Particles
    for px, py, pr in [(20, 25, 2.5), (82, 22, 2.0), (14, 45, 1.8), (88, 50, 2.2), (48, 10, 2.0)]:
        _circle(surf, gold_flame, px, py, pr)
        _circle(surf, white_core, px, py, pr * 0.5)


def _draw_water_fighter(surf, name=""):
    """
    Water War Elemental: Translucent ocean leviathan with custom crowns, fins,
    icicles, and wave blade variations for each specific monster.
    """
    # 1. Oceanic Water Glow
    _draw_glow(surf, (50, 50), 45, (0, 140, 255, 85))
    _draw_glow(surf, (50, 45), 30, (100, 240, 255, 110))

    # Colors
    abyssal_navy = '#041738'
    deep_blue = '#083c82'
    ocean_cyan = '#0088e3'
    bright_aqua = '#00d4ff'
    ice_white = '#e0fbff'

    # Monster-specific Head & Crown Spikes
    if name == 'Finiette':
        # Royal Icicle Crown
        for cx in [32, 41, 50, 59, 68]:
            h_top = 2 if cx == 50 else 8
            _polygon(surf, [(cx - 4, 24), (cx, h_top), (cx + 4, 24)], ice_white, abyssal_navy, 1)
    elif name == 'Finsta':
        # Dual glowing antennae fins
        _line(surf, bright_aqua, [(44, 24), (32, 4)], 4)
        _line(surf, bright_aqua, [(56, 24), (68, 4)], 4)
        _circle(surf, bright_aqua, 32, 4, 5, ice_white, 2)
        _circle(surf, bright_aqua, 68, 4, 5, ice_white, 2)
    elif name == 'Friolera':
        # Sharp Icicle Horns extending outwards
        _polygon(surf, [(30, 28), (10, 12), (34, 24)], bright_aqua, abyssal_navy, 2)
        _polygon(surf, [(70, 28), (90, 12), (66, 24)], bright_aqua, abyssal_navy, 2)
        _polygon(surf, [(30, 26), (14, 14), (32, 24)], ice_white)
        _polygon(surf, [(70, 26), (86, 14), (68, 24)], ice_white)
    elif name == 'Gulfin':
        # Aerodynamic Wave Crest Helmet
        _polygon(surf, [(34, 28), (50, 0), (66, 28)], ocean_cyan, abyssal_navy, 2)
        _polygon(surf, [(40, 24), (50, 6), (60, 24)], bright_aqua)
    else:
        for spike in [
            [(28, 42), (12, 24), (32, 34)],
            [(36, 30), (24, 10), (46, 22)],
            [(46, 20), (50, 4), (54, 20)],
            [(54, 22), (76, 10), (64, 30)],
            [(68, 34), (88, 24), (72, 42)],
        ]:
            _polygon(surf, spike, ocean_cyan, abyssal_navy, max(1, surf.get_width() // 70))
            scaled = [(p[0] * 0.9 + 5, p[1] * 0.9 + 4) for p in spike]
            _polygon(surf, scaled, bright_aqua)

    # 3. Flowing Fluid Lower Body / Tentacle Tail
    _polygon(surf, [(30, 62), (16, 78), (22, 94), (38, 88), (44, 70)], deep_blue, abyssal_navy, 2)
    _polygon(surf, [(70, 62), (84, 78), (78, 94), (62, 88), (56, 70)], deep_blue, abyssal_navy, 2)
    _polygon(surf, [(42, 68), (34, 96), (50, 98), (66, 96), (58, 68)], ocean_cyan, deep_blue, 2)

    # Flowing wave highlights
    _line(surf, bright_aqua, [(20, 80), (32, 90), (48, 94), (68, 90), (80, 80)], 4)
    _line(surf, ice_white, [(28, 84), (48, 90), (68, 84)], 2)

    # 4. Translucent Ice-Plated Torso
    _circle(surf, deep_blue, 50, 50, 28, abyssal_navy, max(1, surf.get_width() // 55))
    _circle(surf, ocean_cyan, 50, 48, 24)
    # Diamond Ice Core
    _polygon(surf, [(50, 34), (62, 48), (50, 62), (38, 48)], bright_aqua, deep_blue, 2)
    _polygon(surf, [(50, 38), (58, 48), (50, 58), (42, 48)], ice_white)

    # Ice Shoulder Armor
    _polygon(surf, [(24, 40), (12, 34), (20, 52), (34, 52)], bright_aqua, abyssal_navy, 2)
    _polygon(surf, [(76, 40), (88, 34), (80, 52), (66, 52)], bright_aqua, abyssal_navy, 2)

    # 5. Fluid Wave Claws / Gulfin Wave Blades
    # Left Arm
    _line(surf, deep_blue, [(28, 46), (14, 56), (8, 70)], 9)
    _line(surf, bright_aqua, [(28, 46), (14, 56), (8, 70)], 4)
    _circle(surf, abyssal_navy, 8, 72, 8, bright_aqua, 2)
    if name == 'Gulfin':
        _polygon(surf, [(8, 72), (-6, 76), (4, 88)], ice_white)
    else:
        _polygon(surf, [(8, 72), (2, 64), (0, 78)], ice_white)
        _polygon(surf, [(8, 72), (4, 82), (12, 82)], ice_white)

    # Right Arm
    _line(surf, deep_blue, [(72, 46), (86, 56), (92, 70)], 9)
    _line(surf, bright_aqua, [(72, 46), (86, 56), (92, 70)], 4)
    _circle(surf, abyssal_navy, 92, 72, 8, bright_aqua, 2)
    if name == 'Gulfin':
        _polygon(surf, [(92, 72), (106, 76), (96, 88)], ice_white)
    else:
        _polygon(surf, [(92, 72), (98, 64), (100, 78)], ice_white)
        _polygon(surf, [(92, 72), (96, 82), (88, 82)], ice_white)

    # 6. Oceanic Visor Head
    _polygon(surf, [(36, 36), (50, 18), (64, 36), (56, 46), (44, 46)], deep_blue, abyssal_navy, 2)
    _polygon(surf, [(40, 28), (50, 22), (60, 28), (54, 38), (46, 38)], ocean_cyan)

    # 7. Glowing Cyan Eyes
    eye_r = 5 if name == 'Finsta' else 3
    _draw_war_eye(surf, 43, 33, '#ffffff', '#00f0ff')
    _draw_war_eye(surf, 57, 33, '#ffffff', '#00f0ff')

    # Water mouth crest
    _line(surf, bright_aqua, [(44, 42), (50, 45), (56, 42)], 2)

    # 8. Floating Water Droplets
    for wx, wy, wr in [(18, 28, 3.0), (84, 26, 2.5), (12, 48, 2.2), (90, 52, 2.8), (50, 10, 2.5)]:
        _circle(surf, bright_aqua, wx, wy, wr, ice_white, 1)


def _draw_plant_fighter(surf, name=""):
    """
    Plant War Elemental: Ancient oak bark guardian with custom sprout horns,
    wings, arm-blades, shield, and crown variations for each specific monster.
    """
    # 1. Forest Emerald Glow
    _draw_glow(surf, (50, 50), 45, (30, 180, 70, 85))
    _draw_glow(surf, (50, 45), 30, (150, 255, 120, 110))

    # Colors
    dark_bark = '#122c15'
    rich_bark = '#254e2a'
    deep_emerald = '#1d7338'
    bright_leaf = '#38b000'
    lime_sap = '#70e000'
    luminous_gold = '#ccff33'

    # Monster-specific Crown & Back Wings
    if name == 'Larvea':
        # Twin leaf sprout antennae
        _line(surf, lime_sap, [(44, 24), (36, 4)], 4)
        _line(surf, lime_sap, [(56, 24), (64, 4)], 4)
        _polygon(surf, [(36, 4), (28, 0), (34, 12)], bright_leaf)
        _polygon(surf, [(64, 4), (72, 0), (66, 12)], bright_leaf)
    elif name == 'Plumette' or name == 'Pluma':
        # Dual Petal Leaf Wings
        _polygon(surf, [(24, 38), (-2, 18), (28, 48)], bright_leaf, dark_bark, 2)
        _polygon(surf, [(76, 38), (102, 18), (72, 48)], bright_leaf, dark_bark, 2)
        _polygon(surf, [(22, 36), (4, 22), (26, 44)], lime_sap)
        _polygon(surf, [(78, 36), (96, 22), (74, 44)], lime_sap)
    elif name == 'Draem':
        # Massive Gnarled Branch Horns
        _line(surf, rich_bark, [(36, 26), (18, 4), (10, 14)], 6)
        _line(surf, rich_bark, [(64, 26), (82, 4), (90, 14)], 6)
        _line(surf, lime_sap, [(36, 26), (18, 4)], 2)
        _line(surf, lime_sap, [(64, 26), (82, 4)], 2)
    else:
        for leaf in [
            [(26, 38), (10, 20), (30, 28)],
            [(32, 28), (22, 8), (42, 18)],
            [(44, 18), (50, 2), (56, 18)],
            [(56, 18), (78, 8), (68, 28)],
            [(68, 28), (90, 20), (74, 38)],
        ]:
            _polygon(surf, leaf, deep_emerald, dark_bark, max(1, surf.get_width() // 70))
            scaled = [(p[0] * 0.9 + 5, p[1] * 0.9 + 4) for p in leaf]
            _polygon(surf, scaled, bright_leaf)

    # 3. Armored Bark Legs & Root Base
    _polygon(surf, [(28, 64), (14, 82), (24, 96), (40, 88), (44, 70)], rich_bark, dark_bark, 2)
    _polygon(surf, [(72, 64), (86, 82), (76, 96), (60, 88), (56, 70)], rich_bark, dark_bark, 2)
    _line(surf, lime_sap, [(18, 84), (26, 94)], 3)
    _line(surf, lime_sap, [(82, 84), (74, 94)], 3)

    # 4. Ancient Wood Torso & Rune Core
    _circle(surf, rich_bark, 50, 50, 28, dark_bark, max(1, surf.get_width() // 55))
    _circle(surf, deep_emerald, 50, 48, 24)

    # Emerald Sap Core Rune
    _polygon(surf, [(50, 36), (60, 48), (50, 60), (40, 48)], bright_leaf, dark_bark, 2)
    _polygon(surf, [(50, 40), (56, 48), (50, 56), (44, 48)], lime_sap)

    # Wooden Shoulder Armor
    _polygon(surf, [(24, 40), (10, 32), (18, 52), (32, 54)], rich_bark, dark_bark, 2)
    _polygon(surf, [(76, 40), (90, 32), (82, 52), (68, 54)], rich_bark, dark_bark, 2)

    # Ivieron Bark Shield on Left Arm
    if name == 'Ivieron':
        _polygon(surf, [(14, 52), (0, 68), (14, 84), (26, 68)], rich_bark, dark_bark, 2)
        _polygon(surf, [(14, 56), (4, 68), (14, 80), (22, 68)], lime_sap)

    # 5. Thorn Vine Whip Arms / Cleaf Arm Blades
    # Left Arm
    _line(surf, rich_bark, [(28, 46), (14, 56), (8, 70)], 9)
    _line(surf, lime_sap, [(28, 46), (14, 56), (8, 70)], 3)
    _circle(surf, dark_bark, 8, 72, 8, bright_leaf, 2)
    if name == 'Cleaf':
        _polygon(surf, [(8, 72), (-8, 86), (10, 84)], bright_leaf, dark_bark, 2)
    else:
        _polygon(surf, [(8, 72), (2, 66), (0, 78)], luminous_gold)
        _polygon(surf, [(8, 72), (6, 82), (14, 82)], luminous_gold)

    # Right Arm
    _line(surf, rich_bark, [(72, 46), (86, 56), (92, 70)], 9)
    _line(surf, lime_sap, [(72, 46), (86, 56), (92, 70)], 3)
    _circle(surf, dark_bark, 92, 72, 8, bright_leaf, 2)
    if name == 'Cleaf':
        _polygon(surf, [(92, 72), (108, 86), (90, 84)], bright_leaf, dark_bark, 2)
    else:
        _polygon(surf, [(92, 72), (98, 66), (100, 78)], luminous_gold)
        _polygon(surf, [(92, 72), (94, 82), (86, 82)], luminous_gold)

    # 6. Forest Guardian Bark Head
    _polygon(surf, [(34, 36), (50, 18), (66, 36), (58, 46), (42, 46)], rich_bark, dark_bark, 2)
    _polygon(surf, [(40, 28), (50, 22), (60, 28), (54, 38), (46, 38)], deep_emerald)

    # 7. Glowing Emerald Eyes
    _draw_war_eye(surf, 43, 33, '#ffffff', '#70e000')
    _draw_war_eye(surf, 57, 33, '#ffffff', '#70e000')

    # Mouth line
    _line(surf, lime_sap, [(42, 42), (50, 45), (58, 42)], 2)

    # 8. Floating Luminous Spores
    for sx, sy, sr in [(22, 26, 2.5), (80, 24, 2.2), (14, 46, 2.0), (86, 50, 2.4), (50, 10, 2.0)]:
        _circle(surf, lime_sap, sx, sy, sr, luminous_gold, 1)


def create_monster_surface(name, element, size=180):
    """
    Create a highly polished, stylized elemental war creature surface.
    Passes individual monster name to draw distinct shapes for each monster!
    Uses caching to guarantee zero performance overhead during battle.
    """
    key = (name, element, size)
    if key in _SURFACE_CACHE:
        return _SURFACE_CACHE[key]

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    if element == 'water':
        _draw_water_fighter(surf, name)
    elif element == 'fire':
        _draw_fire_fighter(surf, name)
    elif element == 'plant':
        _draw_plant_fighter(surf, name)
    else:
        _circle(surf, color('normal'), 50, 50, 33, color('white'), max(1, size // 60))

    _SURFACE_CACHE[key] = surf
    return surf



def draw_element_pedestal(surface, center_pos, element, radius_x=110, radius_y=35):
    """
    Renders a 3D perspective battle podium ring under the monster
    matching its elemental power (Magma for Fire, Whirlpool for Water, Moss/Roots for Plant).
    """
    x, y = center_pos
    ped_surf = pygame.Surface((radius_x * 2 + 20, radius_y * 2 + 20), pygame.SRCALPHA)
    cx, cy = radius_x + 10, radius_y + 10

    if element == 'fire':
        # Magma Ring
        pygame.draw.ellipse(ped_surf, (200, 40, 0, 90), (cx - radius_x, cy - radius_y, radius_x * 2, radius_y * 2))
        pygame.draw.ellipse(ped_surf, (255, 140, 0, 160), (cx - radius_x + 10, cy - radius_y + 5, (radius_x - 10) * 2, (radius_y - 5) * 2), 3)
        pygame.draw.ellipse(ped_surf, (255, 220, 0, 210), (cx - radius_x + 22, cy - radius_y + 10, (radius_x - 22) * 2, (radius_y - 10) * 2), 2)
    elif element == 'water':
        # Ocean Whirlpool
        pygame.draw.ellipse(ped_surf, (0, 120, 220, 90), (cx - radius_x, cy - radius_y, radius_x * 2, radius_y * 2))
        pygame.draw.ellipse(ped_surf, (0, 210, 255, 160), (cx - radius_x + 10, cy - radius_y + 5, (radius_x - 10) * 2, (radius_y - 5) * 2), 3)
        pygame.draw.ellipse(ped_surf, (220, 250, 255, 210), (cx - radius_x + 22, cy - radius_y + 10, (radius_x - 22) * 2, (radius_y - 10) * 2), 2)
    elif element == 'plant':
        # Forest Vine Platform
        pygame.draw.ellipse(ped_surf, (20, 120, 40, 90), (cx - radius_x, cy - radius_y, radius_x * 2, radius_y * 2))
        pygame.draw.ellipse(ped_surf, (60, 200, 80, 160), (cx - radius_x + 10, cy - radius_y + 5, (radius_x - 10) * 2, (radius_y - 5) * 2), 3)
        pygame.draw.ellipse(ped_surf, (180, 255, 100, 210), (cx - radius_x + 22, cy - radius_y + 10, (radius_x - 22) * 2, (radius_y - 10) * 2), 2)
    else:
        pygame.draw.ellipse(ped_surf, (100, 100, 100, 80), (cx - radius_x, cy - radius_y, radius_x * 2, radius_y * 2))

    surface.blit(ped_surf, (x - cx, y - cy))


def draw_battleground_environment(surface, width=1280, height=580):
    """
    Renders a playful, realistic fantasy battle landscape background
    with gradient sky, soft clouds, distant mountain peaks, rolling green hills,
    pine forest ridges, and a rich meadow floor with ambient lighting.
    """
    key = ('battle_bg', width, height)
    if key in _SURFACE_CACHE:
        surface.blit(_SURFACE_CACHE[key], (0, 0))
        return

    bg = pygame.Surface((width, height))

    # 1. Sky Gradient (Deep Sapphire Blue -> Sunset Cyan -> Horizon Gold)
    sky_top = (18, 32, 64)
    sky_bottom = (42, 115, 155)
    for y in range(int(height * 0.55)):
        t = y / (height * 0.55)
        r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * t)
        g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * t)
        b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * t)
        pygame.draw.line(bg, (r, g, b), (0, y), (width, y))

    # Golden Sunset Horizon glow
    horizon_glow = pygame.Surface((width, 90), pygame.SRCALPHA)
    for y in range(90):
        alpha = int(70 * (1.0 - y / 90.0))
        pygame.draw.line(horizon_glow, (245, 190, 110, alpha), (0, y), (width, y))
    bg.blit(horizon_glow, (0, int(height * 0.40)))

    # Soft Fluffy Clouds
    for cx, cy, cr in [(200, 70, 45), (250, 65, 38), (300, 75, 42),
                       (850, 90, 50), (910, 80, 40), (970, 95, 46)]:
        cloud_surf = pygame.Surface((cr * 2, cr * 2), pygame.SRCALPHA)
        pygame.draw.circle(cloud_surf, (255, 255, 255, 65), (cr, cr), cr)
        bg.blit(cloud_surf, (cx - cr, cy - cr))

    # 2. Distant Hazy Mountain Peaks (Layer 1)
    mountain_color = (38, 48, 82)
    snow_color = (150, 168, 205)
    peaks = [
        [(0, int(height * 0.52)), (120, int(height * 0.28)), (260, int(height * 0.52))],
        [(200, int(height * 0.52)), (380, int(height * 0.22)), (540, int(height * 0.52))],
        [(480, int(height * 0.52)), (640, int(height * 0.32)), (800, int(height * 0.52))],
        [(720, int(height * 0.52)), (920, int(height * 0.20)), (1100, int(height * 0.52))],
        [(1020, int(height * 0.52)), (1180, int(height * 0.30)), (width, int(height * 0.52))],
    ]
    for pts in peaks:
        pygame.draw.polygon(bg, mountain_color, pts)
        peak_top = pts[1]
        snow_cap = [peak_top, (peak_top[0] - 25, peak_top[1] + 35), (peak_top[0] + 25, peak_top[1] + 35)]
        pygame.draw.polygon(bg, snow_color, snow_cap)

    # 3. Midground Forest Ridges & Rolling Hills (Layer 2)
    forest_teal = (22, 65, 75)
    pine_green = (16, 82, 44)
    hill_green1 = (28, 98, 52)

    pygame.draw.polygon(bg, forest_teal, [
        (0, int(height * 0.50)),
        (180, int(height * 0.44)),
        (420, int(height * 0.48)),
        (700, int(height * 0.42)),
        (980, int(height * 0.46)),
        (width, int(height * 0.43)),
        (width, height),
        (0, height),
    ])

    for tx in range(10, width, 25):
        ty = int(height * (0.42 + 0.04 * math.sin(tx * 0.02)))
        th = 28
        pygame.draw.polygon(bg, pine_green, [(tx - 8, ty), (tx, ty - th), (tx + 8, ty)])

    pygame.draw.polygon(bg, hill_green1, [
        (0, int(height * 0.55)),
        (320, int(height * 0.48)),
        (720, int(height * 0.54)),
        (1100, int(height * 0.49)),
        (width, int(height * 0.52)),
        (width, height),
        (0, height),
    ])

    # 4. Foreground Battle Meadow Field (Layer 3)
    meadow_green = (35, 122, 58)
    meadow_rect = pygame.Rect(0, int(height * 0.52), width, int(height * 0.48))
    pygame.draw.rect(bg, meadow_green, meadow_rect)

    # Soft ambient battle ground glow
    glow_center = pygame.Surface((width, int(height * 0.48)), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_center, (255, 245, 180, 45), (int(width * 0.1), 10, int(width * 0.8), int(height * 0.42)))
    bg.blit(glow_center, (0, int(height * 0.52)))

    # Grass blade tufts & wildflower spots
    grass_highlight = (65, 168, 85)
    for gx in range(20, width, 35):
        gy = int(height * 0.58 + 30 * math.sin(gx * 0.1))
        if gy < height - 10:
            pygame.draw.line(bg, grass_highlight, (gx, gy), (gx - 3, gy - 8), 2)
            pygame.draw.line(bg, grass_highlight, (gx, gy), (gx + 3, gy - 10), 2)

    flower_colors = [(255, 220, 80), (255, 110, 130), (140, 210, 255)]
    for idx, fx in enumerate(range(45, width - 40, 75)):
        fy = int(height * 0.64 + 40 * math.sin(fx * 0.07))
        if fy < height - 10:
            fc = flower_colors[idx % len(flower_colors)]
            pygame.draw.circle(bg, fc, (fx, fy), 2)

    _SURFACE_CACHE[key] = bg
    surface.blit(bg, (0, 0))


def calc_damage(ability_name, attacker_element, defender_element):
    ability = ABILITIES_DATA[ability_name]
    attack_element = ability['element']
    multiplier = ELEMENT_DATA[attack_element][defender_element]
    return max(1, int(ability['damage'] * multiplier))


def effectiveness_text(multiplier):
    if multiplier >= 2:
        return "It's super effective!"
    if multiplier <= 0.5:
        return "It's not very effective..."
    return ""

