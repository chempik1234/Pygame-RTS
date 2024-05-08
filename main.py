import os

import pygame, sys, json

import base_functions
import pyconfig
import dasis_math
import factory
from camera import Camera
from basicsprite import GenericSprite
from vehicle_base import Vehicle
from waypoint import Waypoint


def load_settings(path):
    with open(path, "r") as f:
        dict_ = json.load(f)
        global COLORS, WIDTH, HEIGHT, FPS
        COLORS, WIDTH, HEIGHT, FPS = dict_["COLORS"], dict_["WIDTH"], dict_["HEIGHT"], dict_["FPS"]


WORLD_WIDTH, WORLD_HEIGHT = 0, 0
COLORS = {}
WIDTH = 1000
HEIGHT = 1000
FPS = 50
load_settings("settings.json")


class Game:
    def __init__(self, colors: dict, width, height, fps, camera_speed=30, player_team_id=0):
        self.screen_size = (width, height)
        # tile_width = tile_height = 50
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('RTS')
        self.clock = pygame.time.Clock()

        self.colors = {i: pygame.Color(*j) for i, j in colors.items()}
        self.fps = fps
        self.display = pygame.display

        self.all_gameplay_sprites = pygame.sprite.Group()
        self.units_group = pygame.sprite.Group()
        self.ui_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.sprite_group_list = [self.all_gameplay_sprites,
                                  self.units_group,
                                  self.ui_group]
        self.camera_speed = camera_speed
        self.player_team_id = player_team_id
        self.seconds = None

    def run(self):
        running = True
        # bmp = factory.bmp(10, 30, self.units_group, self.all_gameplay_sprites, self.ui_group)
        camera = Camera(self.screen_size[0], self.screen_size[1])
        camera_pos_sprite = factory.crosshair(self.units_group, self.all_gameplay_sprites, self.camera_speed)
        pressed_lr = [False, False]
        pressed_ud = [False, False]
        units = self.spawn_units()
        selected_units = []
        self.seconds = 0
        while running:
            units = [i for i in units if i.alive]
            selected_units = [i for i in selected_units if i.alive]
            self.seconds += (self.clock.tick(self.fps) / 1000) % 1800
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pyconfig.KEY_UP:
                        pressed_ud[0] = True
                    if event.key == pyconfig.KEY_DOWN:
                        pressed_ud[1] = True
                    if event.key == pyconfig.KEY_LEFT:
                        pressed_lr[0] = True
                    if event.key == pyconfig.KEY_RIGHT:
                        pressed_lr[1] = True

                    selected_anything = False
                    if event.key == pyconfig.KEY_SELECT:
                        for unit in units:
                            if unit.team_id == self.player_team_id:
                                selected = unit.select(pygame.mouse.get_pos())
                                if selected:
                                    selected_anything = True
                                    selected_units.append(unit)
                                if not unit.selected and unit in selected_units:
                                    selected_units.remove(unit)
                    if event.key == pyconfig.KEY_ORDER and not selected_anything:
                        length = len(selected_units)
                        mouse_pos = pygame.mouse.get_pos()
                        for number, unit in list(enumerate(selected_units)):
                            unit.deselect()
                            selected_units.remove(unit)
                            r = 0
                            if length > 1:
                                r = length * 17
                            x, y = dasis_math.calculate_polygon_vertex_coordinates(length, r, number)
                            x += mouse_pos[0] - self.screen_size[0] / 2
                            y += mouse_pos[1] - self.screen_size[1] / 2
                            unit.set_waypoint(x, y)
                if event.type == pygame.KEYUP:
                    if event.key == pyconfig.KEY_LEFT:
                        pressed_lr[0] = False
                    if event.key == pyconfig.KEY_RIGHT:
                        pressed_lr[1] = False
                    if event.key == pyconfig.KEY_UP:
                        pressed_ud[0] = False
                    if event.key == pyconfig.KEY_DOWN:
                        pressed_ud[1] = False
            camera_pos_sprite.set_acceleration_y((-.05) * pressed_ud[0] + .05 * pressed_ud[1])
            camera_pos_sprite.set_acceleration_x((-.05) * pressed_lr[0] + .05 * pressed_lr[1])
            for unit in units:
                unit.update(units, self.seconds)
            for bullet_sprite in self.bullets_group:
                if bullet_sprite.parent:
                    bullet_sprite.parent.update(self.seconds)
            camera_pos_sprite.update()
            self.render(camera, units, selected_units, camera_pos_sprite)

    def render(self, camera, units, selected_units, camera_pos_sprite):
        self.screen.fill(self.colors["GRASS"])
        self.bullets_group.draw(self.screen)
        self.units_group.draw(self.screen)
        self.ui_group.draw(self.screen)
        camera.update(camera_pos_sprite)
        for sprite in self.all_gameplay_sprites:
            camera.apply(sprite)
        self.render_ui(units, selected_units)
        self.display.flip()

    def render_ui(self, units, selected_units):
        allied_units = [i for i in units if i.team_id == self.player_team_id]
        enemy_units = [i for i in units if i.team_id != self.player_team_id]
        """ ### RED STRIPES """
        STRIPE_WIDTH = 0.025
        for enemy in enemy_units:
            if enemy.hull.rect.y < 0:
                self.screen.fill(pygame.Color("red"), (0, 0,
                                                       self.screen_size[0],
                                                       int(self.screen_size[1] * STRIPE_WIDTH)))
                break
        for enemy in enemy_units:
            if enemy.hull.rect.y > self.screen_size[1]:
                self.screen.fill(pygame.Color("red"), (0,
                                                       int(self.screen_size[1] * (1 - STRIPE_WIDTH)),
                                                       self.screen_size[0],
                                                       int(self.screen_size[1] * STRIPE_WIDTH)))
                break
        for enemy in enemy_units:
            if enemy.hull.rect.x < 0:
                self.screen.fill(pygame.Color("red"), (0, 0,
                                                       int(self.screen_size[0] * STRIPE_WIDTH),
                                                       self.screen_size[1]))
                break
        for enemy in enemy_units:
            if enemy.hull.rect.x > self.screen_size[0]:
                self.screen.fill(pygame.Color("red"), (int(self.screen_size[0] * (1 - STRIPE_WIDTH)),
                                                       0,
                                                       int(self.screen_size[0] * STRIPE_WIDTH),
                                                       self.screen_size[1]))
                break
        """ ### UI """
        self.screen.fill(self.colors["SECONDARY"],
                         (int(self.screen_size[0] * 0.05),
                          int(self.screen_size[1] * 0.01),
                          int(self.screen_size[0] * 0.2),
                          int(self.screen_size[1] * 0.3)))
        base_functions.draw_text(
            ["ВЫБРАНЫ:"] + [i.name for i in selected_units] +
            [f"{len(selected_units)} / {len(allied_units)}"],
            10,
            self.screen_size[0] * 0.05 + 10,
            pyconfig.FONTS[pyconfig.SMALL],
            self.colors["PRIMARY"], self.screen)

    def spawn_units(self):
        return [
            factory.bmp(10, 30, self.units_group, self.all_gameplay_sprites, self.ui_group, self.bullets_group,
                        self.colors[pyconfig.TURRET]),
            factory.bmp(240, 80, self.units_group, self.all_gameplay_sprites, self.ui_group, self.bullets_group,
                        self.colors[pyconfig.TURRET]),
            factory.bradley(70, 630, self.units_group, self.all_gameplay_sprites, self.ui_group, self.bullets_group,
                            self.colors[pyconfig.TURRET], 1)
        ]


if __name__ == '__main__':
    game = Game(COLORS, WIDTH, HEIGHT, FPS)
    game.run()
