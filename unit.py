import math

import pygame.sprite

import base_functions
import dasis_math
import factory
from basicsprite import GenericSprite
from projectile import Projectile
from soldier import Soldier
from vehicle_base import TurretVehicle


class Unit:
    def __init__(self, team_id: int, max_hp: int, attack_radius: int = 500, fire_seconds: float = 0.5):
        self.team_id = team_id
        self.max_hp = self.hp = max_hp
        self.attack_radius = attack_radius
        self.fire_seconds = fire_seconds
        self.target = None
        self.alive = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()

    def get_xy(self):
        pass

    def set_target(self, target):
        self.target = target

    def get_distance_to_target(self):
        return None

    def die(self):
        self.alive = False


class TurretUnit(TurretVehicle, Unit):
    def __init__(self, team_id, max_hp,
                 bullets_group, units_group,
                 x, y, hull_generic_sprite: GenericSprite,
                 turret: GenericSprite, turret_anchor_coords: tuple, turret_color,
                 all_sprites, ui_sprite_group, speed: float = 3, rotation_speed: float = .1,
                 acceleration_speed=.1, name="unit", damage=1, fire_seconds=0.1, attack_radius=500
                 ):
        TurretVehicle.__init__(self, x, y, hull_generic_sprite,
                               turret, turret_anchor_coords, turret_color,
                               all_sprites, ui_sprite_group, speed, rotation_speed,
                               acceleration_speed, name)
        Unit.__init__(self, team_id, max_hp, fire_seconds=fire_seconds, attack_radius=attack_radius)
        self.hull.parent = self
        self.turret.parent = self
        self.bullets_group = bullets_group
        self.past_seconds = self.lasted_seconds = 0
        self.damage = damage
        self.units_group = units_group

    def update(self, units_list, seconds):
        if not self.alive:
            return
        # if self.team_id == 1:
        #     print(self.target, self.lasted_seconds, self.fire_seconds)
        TurretVehicle.update(self, units_list, seconds)
        self.update_targets(units_list)
        self.lasted_seconds += seconds - self.past_seconds
        self.past_seconds = seconds
        if self.target:
            if not self.target.alive:
                self.set_target(None)
            else:
                if self.lasted_seconds > self.fire_seconds:
                    Projectile(self.turret.origin_x, self.turret.origin_y, self.all_sprites, self.units_group,
                               self.bullets_group, self.target.get_xy(), self.team_id, self.damage)
                    self.lasted_seconds %= self.fire_seconds
                # factory.bullet_sprite(self.bullets_group, self.all_sprites,
                #                       *base_functions.find_color(self.turret.image))
                self.rotate_turret_to_target()

    def get_xy(self):
        return self.hull.origin_x, self.hull.origin_y

    def die(self):
        super().die()
        if self.waypoint:
            self.waypoint.destroy()
        self.turret.kill()
        self.hull.kill()
        self.selection_sprite.kill()

    def set_target(self, target):
        super().set_target(target)
        self.turret_copy_hull = target is None
        self.past_seconds = self.lasted_seconds = 0

    def rotate_turret_to_target(self):
        x, y = self.target.get_xy()
        required_angle = math.degrees(math.atan2(self.turret.origin_x - x,
                                                 self.turret.origin_y - y))
        self.turret.rotate(required_angle - self.turret.angle)

    def get_distance_to_target(self):
        if not self.target:
            return 0
        return dasis_math.distance(self.hull.origin_x, self.hull.origin_y, *self.target.get_xy())

    def update_targets(self, units_list):
        if not self.target or self.get_distance_to_target() > self.attack_radius:
            for unit in units_list:
                if unit.team_id != self.team_id and dasis_math.distance(self.hull.origin_x,
                                                                        self.hull.origin_y,
                                                                        *unit.get_xy()) <= self.attack_radius:
                    self.set_target(unit)
                    break
        if self.get_distance_to_target() > self.attack_radius:
            self.set_target(None)

    def get_in(self, soldier):
        if self.can_get_in():
            self.soldiers.append(soldier)
            soldier.sprite.kill()
            soldier.vehicle = self

    def disembark(self):
        for number, soldier in list(enumerate(self.soldiers)):
            self.all_sprites.add(soldier.sprite)
            self.units_group.add(soldier.sprite)
            soldier.vehicle = None
            x, y = dasis_math.calculate_polygon_vertex_coordinates(len(self.soldiers), self.hull.rect.w * 1.5, number)
            x += self.get_x()
            y += self.get_y()
            soldier.sprite.move_to(x, y)
        self.soldiers = []


class SoldierUnit(Unit, Soldier):
    def __init__(self,
                 team_id: int, max_hp: int,
                 units_group, bullets_group,
                 x, y, sprite, all_sprites, ui_sprite_group,
                 speed: float = 2, rotation_speed: float = 3, acceleration_speed=.1, name="unit", damage=2,
                 attack_radius: int = 100, fire_seconds: float = 0.1,
                 ):
        Soldier.__init__(self, x, y, sprite, all_sprites, ui_sprite_group, speed, rotation_speed, acceleration_speed,
                         name)
        Unit.__init__(self, team_id, max_hp, fire_seconds=fire_seconds, attack_radius=attack_radius)
        self.sprite.parent = self
        self.bullets_group = bullets_group
        self.past_seconds = self.lasted_seconds = 0
        self.damage = damage
        self.units_group = units_group
        self.rotating_to_target = True
        self.vehicle = None

    def update(self, units_list, seconds):
        if not self.alive:
            return
        # if self.team_id == 1:
        #     print(self.target, self.lasted_seconds, self.fire_seconds)
        Soldier.update(self, units_list, seconds)
        self.update_targets(units_list)
        self.lasted_seconds += seconds - self.past_seconds
        self.past_seconds = seconds
        if self.target:
            if not self.target.alive:
                self.set_target(None)
            else:
                if self.lasted_seconds > self.fire_seconds:
                    Projectile(self.sprite.origin_x, self.sprite.origin_y, self.all_sprites, self.units_group,
                               self.bullets_group, self.target.get_xy(), self.team_id, self.damage)
                    self.lasted_seconds %= self.fire_seconds
                # factory.bullet_sprite(self.bullets_group, self.all_sprites,
                #                       *base_functions.find_color(self.turret.image))
                self.rotate_to_target()
        if self.vehicle:
            self.sprite.move_to(self.vehicle.get_x(), self.vehicle.get_y())

    def arrive_to_waypoint(self):
        super().arrive_to_waypoint()
        if isinstance(self.waypoint, TurretUnit) and self.waypoint.can_get_in():
            self.waypoint.get_in(self)
            self.waypoint = None

    def get_xy(self):
        return self.sprite.origin_x, self.sprite.origin_y

    def die(self):
        super().die()
        if self.waypoint:
            self.waypoint.destroy()
        self.sprite.kill()
        self.selection_sprite.kill()

    def set_target(self, target):
        super().set_target(target)
        self.rotating_to_target = target is not None
        self.past_seconds = self.lasted_seconds = 0

    def rotate_to_target(self):
        x, y = self.target.get_xy()
        required_angle = math.degrees(math.atan2(self.sprite.origin_x - x,
                                                 self.sprite.origin_y - y))
        self.sprite.rotate(required_angle - self.sprite.angle)

    def get_distance_to_target(self):
        if not self.target:
            return 0
        return dasis_math.distance(self.sprite.origin_x, self.sprite.origin_y, *self.target.get_xy())

    def update_targets(self, units_list):
        if not self.target or self.get_distance_to_target() > self.attack_radius:
            for unit in units_list:
                if unit.team_id != self.team_id and dasis_math.distance(self.sprite.origin_x,
                                                                        self.sprite.origin_y,
                                                                        *unit.get_xy()) <= self.attack_radius:
                    self.set_target(unit)
                    break
        if self.get_distance_to_target() > self.attack_radius:
            self.set_target(None)
