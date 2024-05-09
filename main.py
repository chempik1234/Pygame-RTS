import math
import os
import random

import pygame, sys, json

import base_functions
import pyconfig
import dasis_math
import factory
from camera import Camera
from unit import SoldierUnit, TurretUnit
from vehicle_base import Vehicle


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
    def __init__(self, colors: dict, width, height, fps, camera_speed=30):
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
        self.obstacles_group = pygame.sprite.Group()
        self.sprite_group_list = [self.all_gameplay_sprites,
                                  self.units_group,
                                  self.ui_group]
        self.camera_speed = camera_speed
        self.player_team_id = None
        self.seconds = None

    def run_team_menu(self):
        self.screen.fill(pygame.Color("red"))
        self.screen.fill(pygame.Color("blue"), (self.screen_size[0] // 2, 0,
                                                self.screen_size[0] // 2, self.screen_size[1]))
        base_functions.draw_text(["Выбери сторону"], 20, self.screen_size[0] // 3,
                                 pyconfig.FONTS[pyconfig.BIG], pygame.Color("Black"), self.screen)
        base_functions.draw_text(["RU"], self.screen_size[1] // 2, self.screen_size[1] * 1 // 7,
                                 pyconfig.FONTS[pyconfig.BIG], pygame.Color("Black"), self.screen)
        base_functions.draw_text(["US"], self.screen_size[1] // 2, self.screen_size[1] * 6 // 7,
                                 pyconfig.FONTS[pyconfig.BIG], pygame.Color("Black"), self.screen)
        self.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                    if event.pos[0] <= self.screen_size[0] // 2:
                        self.player_team_id = 0
                    else:
                        self.player_team_id = 1
                if event.type == pygame.QUIT:
                    running = False

    def run_gameplay(self):
        if self.player_team_id is None:
            raise Exception("Сначала надо запустить .run_team_menu()")
        running = True
        # bmp = factory.bmp(10, 30, self.units_group, self.all_gameplay_sprites, self.ui_group)
        camera = Camera(self.screen_size[0], self.screen_size[1])
        camera_pos_sprite = factory.crosshair(self.units_group, self.all_gameplay_sprites, self.camera_speed)
        pressed_lr = [False, False]
        pressed_ud = [False, False]

        self.spawn_environment()
        units = self.spawn_units()

        selected_units = []
        self.seconds = 0
        while running:
            units = [i for i in units if i.alive]
            selected_units = [i for i in selected_units if i.alive]
            tick = self.clock.tick(self.fps)
            self.seconds += (tick / 1000) % 1800
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
                    if event.key == pyconfig.KEY_SELECT_ALL_ON_SCREEN:
                        for unit in units:
                            if unit.team_id == self.player_team_id and \
                                    0 < unit.get_x_on_screen() < self.screen_size[0] and \
                                    0 < unit.get_y_on_screen() < self.screen_size[1]:
                                selected = unit.select(invert=False)
                                if selected:
                                    selected_anything = True
                                    selected_units.append(unit)
                                if not unit.selected and unit in selected_units:
                                    selected_units.remove(unit)
                    if event.key == pyconfig.KEY_SELECT:
                        for unit in units:
                            if unit.team_id == self.player_team_id:
                                selected = unit.select(pygame.mouse.get_pos())
                                if selected:
                                    selected_anything = True
                                    selected_units.append(unit)
                                if not unit.selected and unit in selected_units:
                                    selected_units.remove(unit)
                    if event.key == pyconfig.KEY_ORDER and not selected_anything and selected_units:
                        length = len(selected_units)
                        mouse_pos = pygame.mouse.get_pos()
                        ordinary_order = True
                        if all(i.__class__ == SoldierUnit for i in selected_units):
                            target_vehicle = None
                            for vehicle in [i for i in units if i.team_id == self.player_team_id and
                                                                issubclass(i.__class__, Vehicle)]:
                                if vehicle.hull.check_click(mouse_pos):
                                    ordinary_order = False
                                    target_vehicle = vehicle
                                    break
                            if target_vehicle:
                                for soldier in selected_units:
                                    soldier.deselect()
                                    selected_units.remove(soldier)
                                    soldier.set_waypoint(vehicle=target_vehicle)
                        elif len(selected_units) == 1 and selected_units[0].__class__ == TurretUnit and \
                                selected_units[0].hull.check_click(mouse_pos):
                            ordinary_order = False
                            selected_units[0].disembark()
                            selected_units[0].deselect()
                            selected_units = []
                        if ordinary_order:
                            row = cur_tens = 0
                            for number, unit in list(enumerate(selected_units)):
                                unit.deselect()
                                selected_units.remove(unit)
                                r = 0
                                cur_tens += 1
                                if cur_tens >= row * 10:
                                    row += 1
                                    cur_tens = 0
                                if length > 1:
                                    r = math.sqrt(length * 50) * 1.5 + 30 * row
                                x, y = dasis_math.calculate_polygon_vertex_coordinates(row * 10,
                                                                                       r, number)
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
            self.render(camera, units, selected_units, camera_pos_sprite, tick)

    def render(self, camera, units, selected_units, camera_pos_sprite, tick):
        self.screen.fill(self.colors["GRASS"])
        self.bullets_group.draw(self.screen)
        self.units_group.draw(self.screen)
        self.obstacles_group.draw(self.screen)
        self.ui_group.draw(self.screen)
        camera.update(camera_pos_sprite)
        for sprite in self.all_gameplay_sprites:
            camera.apply(sprite)
        self.render_ui(units, selected_units, tick)
        self.display.flip()

    def render_ui(self, units, selected_units, tick):
        allied_units = [i for i in units if i.team_id == self.player_team_id]
        enemy_units = [i for i in units if i.team_id != self.player_team_id]
        """ ### HP """
        for unit in selected_units + enemy_units:
            if not unit.get_sprite().alive():
                continue
            if unit.team_id == self.player_team_id:
                color = "green"
                if isinstance(unit, TurretUnit):
                    base_functions.draw_text([f"{len(unit.soldiers)}/{unit.soldiers_max}"],
                                             unit.get_y_on_screen() - 40, unit.get_x_on_screen(),
                                             pyconfig.FONTS[pyconfig.SMALL], pygame.Color("black"), self.screen)
                    base_functions.draw_text([f"{len(unit.soldiers)}/{unit.soldiers_max}"],
                                             unit.get_y_on_screen() - 41, unit.get_x_on_screen(),
                                             pyconfig.FONTS[pyconfig.SMALL], pygame.Color("white"), self.screen)
            else:
                color = "red"
            self.screen.fill(pygame.Color("black"), (unit.get_x_on_screen(),
                                                     unit.get_y_on_screen() - 20,
                                                     unit.get_w(), 5))
            self.screen.fill(pygame.Color(color), (unit.get_x_on_screen() + 1,
                                                   unit.get_y_on_screen() - 19,
                                                   unit.hp / unit.max_hp * (unit.get_w() - 2), 3))
        """ ### RED STRIPES """
        STRIPE_WIDTH = 0.025
        for enemy in enemy_units:
            if enemy.get_y_on_screen() < 0:
                self.screen.fill(pygame.Color("red"), (0, 0,
                                                       self.screen_size[0],
                                                       int(self.screen_size[1] * STRIPE_WIDTH)))
                break
        for enemy in enemy_units:
            if enemy.get_y_on_screen() > self.screen_size[1]:
                self.screen.fill(pygame.Color("red"), (0,
                                                       int(self.screen_size[1] * (1 - STRIPE_WIDTH)),
                                                       self.screen_size[0],
                                                       int(self.screen_size[1] * STRIPE_WIDTH)))
                break
        for enemy in enemy_units:
            if enemy.get_x_on_screen() < 0:
                self.screen.fill(pygame.Color("red"), (0, 0,
                                                       int(self.screen_size[0] * STRIPE_WIDTH),
                                                       self.screen_size[1]))
                break
        for enemy in enemy_units:
            if enemy.get_x_on_screen() > self.screen_size[0]:
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
        selected_dict = {}
        for unit in selected_units:
            if selected_dict.get(unit.name):
                selected_dict[unit.name] += 1
            else:
                selected_dict[unit.name] = 1
        base_functions.draw_text(
            ["ВЫБРАНЫ:"] + [f"{i}: {j}x" for i, j in selected_dict.items()] +
            [f"{len(selected_units)} / {len(allied_units)}"],
            10,
            self.screen_size[0] * 0.05 + 10,
            pyconfig.FONTS[pyconfig.SMALL],
            self.colors["PRIMARY"], self.screen)
        #
        if not enemy_units:
            base_functions.draw_text(["МЕСТНОСТЬ ЗАЧИЩЕНА!"], self.screen_size[1] // 2, self.screen_size[0] // 3,
                                     pyconfig.FONTS[pyconfig.BIG], pygame.Color("black"), self.screen)
        base_functions.draw_text([f"FPS: {int(1000 / tick)}"],
                                 0, 0, pyconfig.FONTS[pyconfig.SMALL], pygame.Color("black"), self.screen)

    def spawn_units(self):
        res = []
        for i in range(12):
            res.append(factory.apc(40 * i, 0, self.units_group, self.all_gameplay_sprites, self.ui_group,
                                   self.obstacles_group,
                                   self.bullets_group, self.colors[pyconfig.TURRET], team_id=self.player_team_id))
        for i in range(6):
            res.append(factory.tank(80 * i, 80, self.units_group, self.all_gameplay_sprites, self.ui_group,
                                    self.obstacles_group,
                                    self.bullets_group, self.colors[pyconfig.TURRET], team_id=self.player_team_id))
        for i in range(6):
            for col in range(2):
                for row in range(6):
                    res.append(factory.soldier(80 * i + 30 + 20 * col,
                                               80 + 30 * row, self.units_group, self.all_gameplay_sprites,
                                               self.ui_group,
                                               self.obstacles_group, self.bullets_group, team_id=self.player_team_id))
        # ENEMIES
        i = 0
        while i < 12:
            enemy_bmp = factory.apc(random.randint(-1000, 1000), random.randint(-2000, -1000), self.units_group,
                                    self.all_gameplay_sprites, self.ui_group,
                                    self.obstacles_group,
                                    self.bullets_group, self.colors[pyconfig.TURRET], team_id=1 - self.player_team_id)
            i += 1
            for j in self.all_gameplay_sprites:
                if j == enemy_bmp.hull or j == enemy_bmp.turret:
                    continue
                if pygame.sprite.collide_mask(j, enemy_bmp.get_sprite()):
                    enemy_bmp.die()
                    i -= 1
                    break
            res.append(enemy_bmp)
        i = 0
        while i < 12:
            enemy_tank = factory.tank(random.randint(-1000, 1000), random.randint(-2000, -1000),
                                      self.units_group, self.all_gameplay_sprites, self.ui_group,
                                      self.obstacles_group,
                                      self.bullets_group, self.colors[pyconfig.TURRET], team_id=1 - self.player_team_id)
            i += 1
            for j in self.all_gameplay_sprites:
                if j == enemy_tank.hull or j == enemy_tank.turret:
                    continue
                if pygame.sprite.collide_mask(j, enemy_tank.get_sprite()):
                    enemy_tank.die()
                    i -= 1
                    break
            res.append(enemy_tank)
        i = 0
        while i < 72:
            enemy_soldier = factory.soldier(random.randint(-1000, 1000), random.randint(-2000, -1000), self.units_group,
                                            self.all_gameplay_sprites,
                                            self.ui_group,
                                            self.obstacles_group, self.bullets_group, team_id=1 - self.player_team_id)
            i += 1
            for j in self.all_gameplay_sprites:
                if j == enemy_soldier.sprite:
                    continue
                if pygame.sprite.collide_mask(j, enemy_soldier.get_sprite()):
                    enemy_soldier.die()
                    i -= 1
                    break
            res.append(enemy_soldier)

        # for i in range(12):
        #     res.append(factory.bradley(40 * i, -1160, self.units_group, self.all_gameplay_sprites, self.ui_group,
        #                                self.obstacles_group,
        #                                self.bullets_group, self.colors[pyconfig.TURRET], team_id=1))
        # for i in range(6):
        #     res.append(factory.abrams(80 * i, -1080, self.units_group, self.all_gameplay_sprites, self.ui_group,
        #                               self.obstacles_group,
        #                               self.bullets_group, self.colors[pyconfig.TURRET], team_id=1))
        # for i in range(6):
        #     for col in range(2):
        #         for row in range(6):
        #             res.append(factory.soldier(80 * i + 30 + 20 * col,
        #                                        -1080 + 30 * row, self.units_group, self.all_gameplay_sprites,
        #                                        self.ui_group,
        #                                        self.obstacles_group,self.bullets_group, team_id=1, color="sand"))
        return res

    def spawn_environment(self):
        i = 0
        while i < 200:
            house = factory.house(random.randint(-5000, 5000), random.randint(-2000, -100), self.bullets_group,
                                  self.obstacles_group, self.all_gameplay_sprites)
            i += 1
            for j in self.all_gameplay_sprites:
                if j == house.sprite:
                    continue
                if pygame.sprite.collide_mask(j, house.sprite):
                    house.destroy()
                    i -= 1
                    break


if __name__ == '__main__':
    game = Game(COLORS, WIDTH, HEIGHT, FPS)
    game.run_team_menu()
    game.run_gameplay()
