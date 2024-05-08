from basicsprite import GenericSprite


class SpriteMovable(GenericSprite):
    def __init__(self, tile_image, tile_name, x, y, center_x, center_y, sprite_group, all_sprites, has_collisions=True,
                 max_speed=1, appliable=True, origin_object=None, scale=1):
        super().__init__(tile_image, tile_name, x, y, center_x, center_y, sprite_group, all_sprites, has_collisions,
                         scale=scale)
        self.acceleration_x = self.acceleration_y = 0
        self.max_speed = max_speed
        self.speed_x = self.speed_y = 0
        self.appliable = appliable
        self.parent = origin_object

    def set_acceleration_y(self, multiplier: float):
        self.acceleration_y = multiplier

    def set_acceleration_x(self, multiplier: float):
        self.acceleration_x = multiplier

    def update(self):
        self.speed_x += self.max_speed * self.acceleration_x
        self.speed_y += self.max_speed * self.acceleration_y
        if self.acceleration_x == 0:
            self.speed_x = 0
        if self.acceleration_y == 0:
            self.speed_y = 0
        speed = self.speed_x ** 2 + self.speed_y ** 2
        if speed > self.max_speed ** 2:
            delim = speed / self.max_speed ** 2
            self.speed_x /= delim
            self.speed_y /= delim
        self.origin_x += self.speed_x
        self.origin_y += self.speed_y
