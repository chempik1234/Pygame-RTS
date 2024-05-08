import pygame.sprite

import factory


class Projectile:
    def __init__(self, origin_x, origin_y, all_sprites, units_group, bullets_group, target_point: tuple,
                 team_id: int, damage: int = 1, speed: int = 20, lifetime: float = 2):
        self.sprite = factory.bullet_sprite(bullets_group, all_sprites, origin_x, origin_y, max_speed=speed,
                                            parent_object=self, scale=max(1 + (damage - 100) / 300, .5))
        self.units_group = units_group
        self.team_id = team_id
        self.damage = damage
        self.target_point = target_point
        self.lifetime = lifetime
        self.total_seconds = 0
        self.past_seconds = None
        self.alive = True
        self.set_xy()

    def set_xy(self):
        x, y = self.target_point[0] - self.sprite.origin_x, self.target_point[1] - self.sprite.origin_y
        max_val = max(abs(x), abs(y))
        x, y = x / max_val, y / max_val
        self.sprite.set_acceleration_x(x)
        self.sprite.set_acceleration_y(y)
        return x, y

    def update(self, seconds):
        if not self.alive:
            return
        self.sprite.update()
        for i in self.units_group:
            if pygame.sprite.collide_mask(self.sprite, i) and i.parent is not None and i.parent.team_id != self.team_id:
                i.parent.take_damage(self.damage)
                self.destroy()
                break
        if self.past_seconds is not None:
            self.total_seconds += seconds - self.past_seconds
        self.past_seconds = seconds
        if self.total_seconds > self.lifetime:
            self.destroy()

    def set_target_point(self, target_point: tuple):
        self.target_point = target_point
        self.set_xy()

    def destroy(self):
        self.sprite.kill()
        self.alive = False
