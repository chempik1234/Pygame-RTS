import math


def calculate_polygon_vertex_coordinates(n, r, i):
    angle = (2 * math.pi / n) * i
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    return x, y


def process_angle(angle):
    if angle > 180:
        return -360 + angle
    elif angle < -180:
        return 360 + angle
    return angle


def diff_angles(angle_to, angle_from):
    angle_to, angle_from = process_angle(angle_to), process_angle(angle_from)
    if angle_to >= 0 and angle_from >= 0:
        return process_angle(angle_to - angle_from)
    elif angle_from >= 0 >= angle_to:
        return process_angle(360 + angle_to - angle_from)
    elif angle_to >= 0 >= angle_from:
        return process_angle(360 - angle_to + angle_from)
    elif angle_from <= 0 and angle_to <= 0:
        return process_angle(-angle_from + angle_to)


def distance(x, y, x1, y1):
    return math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)


def vector_look_at(angle, multiplier: int = 1):
    return multiplier * math.sin(angle), multiplier * math.cos(angle)
