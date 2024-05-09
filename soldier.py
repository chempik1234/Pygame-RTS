import math

import dasis_math
import factory
from vehicle_base import Vehicle
from waypoint import Waypoint


class Soldier:
    def __init__(self, x, y, sprite, all_sprites, ui_sprite_group,
                 speed: float = .5, rotation_speed: float = 3, acceleration_speed=.1, name="unit"):
        self.sprite = sprite
        self.sprite.origin_x = x  # - self.sprite.rect.center[0]
        self.sprite.origin_y = y  # - self.sprite.rect.center[1]
        self.origin_speed = speed
        self.current_speed = 0
        self.acceleration = 0
        self.rotation_accel = 0
        self.rotation_speed = rotation_speed
        self.selected = False

        self.ui_group = ui_sprite_group
        self.all_sprites = all_sprites
        self.selection_sprite = factory.selection_sprite(self.ui_group, self.all_sprites)
        self.waypoint = None
        self.past_waypoint_distance = None
        self.fast_rotating = False
        self.name = name

    def get_x(self):
        return self.sprite.origin_x

    def get_y(self):
        return self.sprite.origin_y

    def get_x_on_screen(self):
        return self.sprite.rect.x

    def get_y_on_screen(self):
        return self.sprite.rect.y

    def get_w(self):
        return self.sprite.rect.w

    def rotate(self, angle: float):
        self.sprite.rotate(angle)

    def get_sprite_rotation(self):
        return self.sprite.angle

    def set_speed(self, speed: float):
        self.current_speed = speed

    def set_acceleration(self, multiplier: float):
        self.acceleration = multiplier

    def set_rotation_multiplier(self, multiplier: float):
        self.rotation_accel = multiplier

    def update(self, units_list, seconds):
        self.rotate(self.rotation_speed * self.rotation_accel)
        self.current_speed = min(self.origin_speed, self.current_speed + self.acceleration)
        rotation_degrees = math.radians(self.get_sprite_rotation())
        x_offset, y_offset = dasis_math.vector_look_at(rotation_degrees, self.current_speed)
        # y_offset = self.current_speed * math.cos(math.radians(self.get_sprite_rotation()))
        # x_offset = self.current_speed * math.sin(math.radians(self.get_sprite_rotation()))
        self.sprite.origin_x -= x_offset
        self.sprite.origin_y -= y_offset
        self.selection_sprite.origin_x, self.selection_sprite.origin_y = self.sprite.origin_x, self.sprite.origin_y
        if self.selected and not self.selection_sprite.alive():
            self.selection_sprite.add(self.all_sprites, self.ui_group)
        elif not self.selected and self.selection_sprite.alive():
            self.selection_sprite.kill()
        if self.selection_sprite.alive():
            self.selection_sprite.origin_x, self.selection_sprite.origin_y = self.sprite.origin_x, self.sprite.origin_y
        if self.waypoint is not None:
            required_angle = math.degrees(math.atan2(self.sprite.origin_x - self.waypoint.get_x(),
                                                     self.sprite.origin_y - self.waypoint.get_y()))
            # self.sprite.rotate(required_angle - self.sprite.angle)
            required_angle = dasis_math.process_angle(required_angle)
            diff = dasis_math.diff_angles(required_angle, self.sprite.angle)
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
            if (isinstance(self.waypoint, Waypoint) and distance < self.sprite.rect.w) or (not isinstance(self.waypoint, Waypoint) and distance < self.waypoint.get_w() * 2):
                self.arrive_to_waypoint()
            if distance < self.sprite.rect.w or (self.past_waypoint_distance and distance > self.past_waypoint_distance):
                self.press_break()
            self.past_waypoint_distance = self.get_waypoint_distance()
        else:
            self.press_break()
        # BRAKING WHEN NEAR UNITS
        forward_x, forward_y = dasis_math.vector_look_at(self.get_sprite_rotation(), -100)
        forward_x += self.get_x_on_screen()
        forward_y += self.get_y_on_screen()
        for unit in units_list:
            if unit is self:
                continue
            if unit.get_sprite().check_click((forward_x, forward_y)):
                self.set_acceleration(0)
                self.set_speed(0)
                break

    def arrive_to_waypoint(self):
        self.set_rotation_multiplier(0)
        if isinstance(self.waypoint, Waypoint):
            self.waypoint.destroy()
            self.waypoint = None

    def get_waypoint_distance(self):
        if not self.waypoint:
            return 0
        return dasis_math.distance(self.sprite.origin_x, self.sprite.origin_y,
                                   self.waypoint.get_x(), self.waypoint.get_y())

    def select(self, mouse=None, invert=True):
        """
        :param invert: defines if .selected needs to be inverted or simply set True
        :param mouse: tuple (x, y)
        :return: True if selected was set to True during the last method call or False in every other case
        """
        if self.sprite.check_click(mouse):
            if invert:
                self.selected = not self.selected
            else:
                self.selected = True
            return self.selected
        return False

    def deselect(self):
        self.selected = False

    def set_waypoint(self, x=None, y=None, vehicle=None):
        if vehicle or issubclass(self.waypoint.__class__, Vehicle):
            self.waypoint = vehicle
        else:
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
