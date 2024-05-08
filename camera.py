class Camera:
    def __init__(self, screen_width, screen_height):
        self.dx = 0
        self.dy = 0
        self.width, self.height = screen_width, screen_height

    def apply(self, obj):
        if obj.appliable:
            obj.rect.x = obj.origin_x + self.dx - obj.rect.w // 2
            obj.rect.y = obj.origin_y + self.dy - obj.rect.h // 2
        else:
            obj.origin_x = obj.rect.x - self.dx + self.width // 2
            obj.origin_y = obj.rect.y - self.dy + self.height // 2
            obj.appliable = True

    def update(self, target):
        self.dx = -(target.origin_x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.origin_y + target.rect.h // 2 - self.height // 2)
