import math

import base_functions
import dasis_math
import factory
from basicsprite import GenericSprite
from waypoint import Waypoint


class Vehicle:
    def __init__(self, x, y, hull_generic_sprite: GenericSprite, all_sprites, ui_sprite_group,
                 speed: float = 3, rotation_speed: float = .1, acceleration_speed=.1, name="unit",
                 soldiers_max=6):
        self.hull = hull_generic_sprite
        self.hull.origin_x = x  #  - self.hull.rect.center[0]
        self.hull.origin_y = y  # - self.hull.rect.center[1]
        self.origin_speed = speed
        self.current_speed = 0
        self.acceleration = 0
        self.rotation_accel = 0
        self.rotation_speed = rotation_speed
        self.acceleration_speed = acceleration_speed
        self.selected = False

        self.ui_group = ui_sprite_group
        self.all_sprites = all_sprites
        self.selection_sprite = factory.selection_sprite(self.ui_group, self.all_sprites)
        self.waypoint = None
        self.past_waypoint_distance = None
        self.fast_rotating = False
        self.name = name
        self.soldiers_max = soldiers_max
        self.soldiers = []

    def can_get_in(self):
        return len(self.soldiers) < self.soldiers_max

    def rotate(self, angle: float):
        self.hull.rotate(angle)

    def get_hull_rotation(self):
        return self.hull.angle

    def set_speed(self, speed: float):
        self.current_speed = speed

    def set_acceleration(self, multiplier: float):
        self.acceleration = multiplier

    def set_rotation_multiplier(self, multiplier: float):
        self.rotation_accel = multiplier

    def update(self, units_list, seconds):
        self.rotate(self.rotation_speed * self.rotation_accel)
        self.current_speed = self.current_speed + self.acceleration
        rotation_degrees = math.radians(self.get_hull_rotation())
        x_offset, y_offset = dasis_math.vector_look_at(rotation_degrees, self.current_speed)
        # y_offset = self.current_speed * math.cos(math.radians(self.get_hull_rotation()))
        # x_offset = self.current_speed * math.sin(math.radians(self.get_hull_rotation()))
        self.hull.origin_x -= x_offset
        self.hull.origin_y -= y_offset
        self.selection_sprite.origin_x, self.selection_sprite.origin_y = self.hull.origin_x, self.hull.origin_y
        if self.selected and not self.selection_sprite.alive():
            self.selection_sprite.add(self.all_sprites, self.ui_group)
        elif not self.selected and self.selection_sprite.alive():
            self.selection_sprite.kill()
        if self.selection_sprite.alive():
            self.selection_sprite.origin_x, self.selection_sprite.origin_y = self.hull.origin_x, self.hull.origin_y
        if self.waypoint is not None:
            required_angle = math.degrees(math.atan2(self.hull.origin_x - self.waypoint.sprite.origin_x,
                                                     self.hull.origin_y - self.waypoint.sprite.origin_y))
            # self.hull.rotate(required_angle - self.hull.angle)
            required_angle = dasis_math.process_angle(required_angle)
            diff = dasis_math.diff_angles(required_angle, self.hull.angle)
            distance = self.get_waypoint_distance()
            if abs(diff) > 170:
                self.fast_rotate(3)
            elif diff > 90 and not self.fast_rotating:
                self.set_rotation_multiplier(2)
                self.press_break()
            elif diff > 10 and not self.fast_rotating:
                self.set_rotation_multiplier(1)
                self.press_break()
            elif diff < -90 and not self.fast_rotating:
                self.set_rotation_multiplier(-2)
                self.press_break()
            elif diff < -10 and not self.fast_rotating:
                self.set_rotation_multiplier(-1)
                self.press_break()
            elif abs(diff) <= 10:
                self.fast_rotating = False
                self.set_rotation_multiplier(0)
                self.set_acceleration(1)
            if distance < self.hull.rect.w:
                self.waypoint.destroy()
                self.waypoint = None
                self.set_rotation_multiplier(0)
            if distance < self.hull.rect.w or (self.past_waypoint_distance and distance > self.past_waypoint_distance):
                self.press_break()
            self.past_waypoint_distance = self.get_waypoint_distance()
        else:
            self.press_break()

    def get_waypoint_distance(self):
        if not self.waypoint:
            return 0
        return dasis_math.distance(self.hull.origin_x, self.hull.origin_y,
                                   self.waypoint.sprite.origin_x, self.waypoint.sprite.origin_y)

    def select(self, mouse):
        """
        :param mouse: tuple (x, y)
        :return: True if selected was set to True during the last method call or False in every other case
        """
        if self.hull.check_click(mouse):
            self.selected = not self.selected
            return self.selected
        return False

    def deselect(self):
        self.selected = False

    def set_waypoint(self, x, y):
        if self.waypoint:
            self.waypoint.move_to(x, y)
        else:
            self.waypoint = Waypoint(x, y, all_sprites=self.all_sprites,
                                     ui_group=self.ui_group)

    def fast_rotate(self, multiplier):
        if not self.fast_rotating:
            self.fast_rotating = True
            self.set_rotation_multiplier(multiplier)

    def press_break(self, multiplier=-1):
        if self.current_speed > 0:
            self.set_acceleration(multiplier)
        else:
            self.set_speed(0)
            self.set_acceleration(max(0, self.acceleration))


class TurretVehicle(Vehicle):
    def __init__(self, x, y, hull_generic_sprite: GenericSprite,
                 turret: GenericSprite, turret_anchor_coords: tuple, turret_color,
                 all_sprites, ui_sprite_group, speed: float = 3, rotation_speed: float = .1,
                 acceleration_speed=.1, name="unit"):
        super().__init__(x, y, hull_generic_sprite, all_sprites, ui_sprite_group, speed, rotation_speed,
                         acceleration_speed, name)
        self.turret = turret
        self.turret_anchor_coords = turret_anchor_coords
        self.turret_color = turret_color
        self.turret_copy_hull = True

    def update_turret_position(self):
        x, y = base_functions.find_color(self.hull.image, self.turret_color)
        new_x = self.hull.origin_x + x
        new_y = self.hull.origin_y + y

        self.turret.origin_x = new_x
        self.turret.origin_y = new_y

    def rotate_turret_as_hull(self):
        self.turret.rotate(self.hull.angle - self.turret.angle)

    def update(self, units_list, seconds):
        super().update(units_list, seconds)
        self.update_turret_position()
        if self.turret_copy_hull:
            self.rotate_turret_as_hull()
