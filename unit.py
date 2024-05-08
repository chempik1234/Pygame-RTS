import math

import base_functions
import dasis_math
import factory
from basicsprite import GenericSprite
from projectile import Projectile
from vehicle_base import TurretVehicle


class Unit:
    def __init__(self, team_id: int, max_hp: int, attack_radius: int = 500, fire_seconds: float = 0.5):
        self.team_id = team_id
        self.max_hp = self.hp = max_hp
        self.attack_radius = attack_radius
        self.fire_seconds = fire_seconds
        self.alive = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()

    def get_xy(self):
        pass

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
        self.target = None
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
        self.target = target
        self.turret_copy_hull = target is None
        self.past_seconds = self.lasted_seconds = 0

    def rotate_turret_to_target(self):
        x, y = self.target.get_xy()
        required_angle = math.degrees(math.atan2(self.turret.origin_x - x,
                                                 self.turret.origin_y - y))
        self.turret.rotate(required_angle - self.turret.angle)
        # required_angle = dasis_math.process_angle(required_angle)
        # diff = dasis_math.diff_angles(required_angle, self.hull.angle)
        # distance = self.get_waypoint_distance()
        # if abs(diff) > 170:
        #     self.fast_rotate(3)
        # elif diff > 90 and not self.fast_rotating:
        #     self.set_rotation_multiplier(2)
        #     self.press_break()
        # elif diff > 10 and not self.fast_rotating:
        #     self.set_rotation_multiplier(1)
        #     self.press_break()
        # elif diff < -90 and not self.fast_rotating:
        #     self.set_rotation_multiplier(-2)
        #     self.press_break()
        # elif diff < -10 and not self.fast_rotating:
        #     self.set_rotation_multiplier(-1)
        #     self.press_break()
        # elif abs(diff) <= 10:
        #     self.fast_rotating = False
        #     self.set_rotation_multiplier(0)
        #     self.set_acceleration(1)
        # if distance < self.hull.rect.w:
        #     self.waypoint.destroy()
        #     self.waypoint = None
        #     self.set_rotation_multiplier(0)

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
