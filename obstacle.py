from projectile import Projectile


class Obstacle:
    def __init__(self, sprite, bullets_group, obstacles_group, health=100):
        self.sprite = sprite
        self.sprite.parent = self
        self.bullets_group = bullets_group
        self.obstacles_group = obstacles_group
        self.health = health

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        self.sprite.kill()
