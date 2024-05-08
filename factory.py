import os

import pygame

from basicsprite import GenericSprite
from projectile import Projectile
from sprite_movable import SpriteMovable
from unit import TurretUnit
from vehicle_base import Vehicle, TurretVehicle

IMAGE_DIR = "data/images"


def load_image(name, color_key=None):
    fullname = os.path.join(IMAGE_DIR, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image.set_colorkey(image.get_at((49, 0)))
    else:
        image = image.convert_alpha()
    return image


def bmp(x, y, sprite_group, all_sprites, ui_group, bullets_group, turret_color, team_id=0):
    hull = GenericSprite(load_image("bmp\\hull.png"), "hull", x, y, 11, 26, sprite_group,
                         all_sprites)
    turret = GenericSprite(load_image("bmp\\turret.png"), "turret", x, y, 22, 34, sprite_group,
                           all_sprites)
    turret_anchor_coords = (11, 26)
    return TurretUnit(team_id, 2000,
                      bullets_group, sprite_group,
                      x, y, hull,
                      turret, turret_anchor_coords, turret_color,
                      all_sprites, ui_group, 3, rotation_speed=1, name="БМП", damage=100, fire_seconds=0.1,
                      attack_radius=500)


def bradley(x, y, sprite_group, all_sprites, ui_group, bullets_group, turret_color, team_id=0):
    hull = GenericSprite(load_image("bradley\\hull.png"), "hull", x, y, 11, 26, sprite_group,
                         all_sprites)
    turret = GenericSprite(load_image("bradley\\turret.png"), "turret", x, y, 22, 34, sprite_group,
                           all_sprites)
    turret_anchor_coords = (11, 26)
    return TurretUnit(team_id, 3000,
                      bullets_group, sprite_group,
                      x, y, hull,
                      turret, turret_anchor_coords, turret_color,
                      all_sprites, ui_group, 3, rotation_speed=1, name="BRADLEY", damage=400, fire_seconds=0.4,
                      attack_radius=550)


def crosshair(sprite_group, all_sprites, max_speed=1):
    return SpriteMovable(load_image("crosshair.png"), "camera target", 0, 0, None,
                         None, sprite_group, all_sprites, False, max_speed=max_speed)


def selection_sprite(sprite_group, all_sprites):
    return GenericSprite(load_image("selection.png"), "selection", 0, 0, None, None,
                         sprite_group, all_sprites, False)


def waypoint_sprite(ui_group, all_sprites, x, y):
    return GenericSprite(load_image("waypoint.png"), "waypoint", x, y, 10, 10, ui_group,
                         all_sprites, appliable=False)


def bullet_sprite(bullets_group, all_sprites, x, y, max_speed, parent_object, scale=1):
    return SpriteMovable(load_image("projectile.png"), "projectile", x, y, 10, 10,
                         bullets_group, all_sprites, appliable=True, max_speed=max_speed, origin_object=parent_object,
                         scale=scale)