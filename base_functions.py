import pygame


def draw_text(text, text_coord_y, text_coord_x, size_font, color, screen):
    font = pygame.font.Font(None, size_font)
    for i in range(len(text)):
        line = text[i]
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        # text_coord_y += 10
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


def find_color(image, color=(255, 255, 0)):
    pixel_array = pygame.PixelArray(image)
    width, height = image.get_size()
    for y in range(height):
        for x in range(width):
            pixel_color = pixel_array[x, y]
            r = (pixel_color & 0xFF0000) >> 16
            g = (pixel_color & 0x00FF00) >> 8
            b = (pixel_color & 0x0000FF)
            if r - color[0] < 30 and g - color[1] < 30 and b - color[2] < 30:
                del pixel_array
                return x, y
