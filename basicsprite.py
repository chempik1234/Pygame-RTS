import pygame

import dasis_math


class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, group, parent=None):
        super().__init__(group)
        self.rect = None
        self.appliable = False
        self.origin_x = self.origin_y = None
        self.parent = parent

    def get_event(self, event):
        pass


class GenericSprite(BasicSprite):
    def __init__(self, tile_image, tile_name, x, y, center_x, center_y, sprite_group, all_sprites, has_collisions=True,
                 appliable=True, parent=None, scale=1):
        super().__init__((sprite_group, all_sprites))
        self.image = pygame.transform.scale(tile_image, (int(tile_image.get_width() * scale),
                                                         int(tile_image.get_height() * scale)))  # tile_image
        self.tile_type = tile_name
        self.appliable = appliable
        if center_x is not None and center_y is not None:
            self.rect = self.image.get_rect(center=(center_x, center_y)).move(x, y)
        else:
            self.rect = self.image.get_rect().move(x, y)
        self.original_image = self.image
        self.origin_x = x
        self.origin_y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.has_collisions = has_collisions
        self.angle = 0
        self.parent = parent

    def check_click(self, mouse) -> bool:
        return self.rect.collidepoint(mouse)

    def move_to(self, x, y):
        self.origin_x, self.origin_y = x, y
        self.rect.move(x, y)

    def rotate(self, angle: float):
        self.angle += angle
        # print("было: ", self.angle)
        self.angle = dasis_math.process_angle(self.angle)
        # print("стало: ", self.angle)
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
