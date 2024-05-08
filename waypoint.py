import factory


class Waypoint:
    def __init__(self, origin_x, origin_y, all_sprites, ui_group):
        self.sprite = factory.waypoint_sprite(ui_group, all_sprites, origin_x, origin_y)

    def move_to(self, x, y):
        self.sprite.move_to(x, y)  # self.sprite.origin_x, self.sprite.origin_y = x, y

    def destroy(self):
        self.sprite.kill()
