"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Paddle.
"""

import pygame

import settings

from typing import Optional  # Importa Optional desde typing

class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 64
        self.height = 16

        # By default, the blue paddle
        self.skin = 0

        # By default, the 64-pixels-width paddle.
        self.size = 1

        self.texture = settings.TEXTURES["spritesheet"]
        self.frames = settings.FRAMES["paddles"]
        self.cannon_width = settings.CANNON_WIDTH
        self.cannon_height = settings.CANNON_HEIGHT

        # The paddle only move horizontally
        self.vx = 0

        self.cannons_active = False 
        self.cannons_fired = False

    def resize(self, size: int) -> None:
        self.size = size
        self.width = (self.size + 1) * 32

    def dec_size(self):
        self.resize(max(0, self.size - 1))

    def inc_size(self):
        self.resize(min(3, self.size + 1))

    def get_collision_rect(self) -> pygame.Rect:
        # Incluimos el tamaño de los cañones en el rectángulo de colisión
        if self.cannons_active:
            return pygame.Rect(
                self.x - self.cannon_width,
                self.y,
                self.width + 2 * self.cannon_width,
                self.height
            )
        else:
            return pygame.Rect(self.x, self.y, self.width, self.height)
            
    def update(self, dt: float) -> None:
        next_x = self.x + self.vx * dt

        if self.cannons_active:
            # Si los cañones están activos, considerar el ancho de los cañones
            if self.vx < 0:
                self.x = max(self.cannon_width, next_x)
            else:
                self.x = min(settings.VIRTUAL_WIDTH - self.width - self.cannon_width, next_x)
        else:
            # Si los cañones no están activos, no considerar el ancho de los cañones
            if self.vx < 0:
                self.x = max(0, next_x)
            else:
                self.x = min(settings.VIRTUAL_WIDTH - self.width, next_x)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.texture, (self.x, self.y), self.frames[self.skin][self.size])

        if self.cannons_active:
            surface.blit(settings.TEXTURES["left_cannon"], (self.x - 12, self.y))
            surface.blit(settings.TEXTURES["right_cannon"], (self.x + self.width, self.y))

    def activate_cannons(self) -> None:
        self.cannons_active = True
        self.cannons_fired = False  # Reiniciar al activar

    def deactivate_cannons(self) -> None:
        self.cannons_active = False
        self.cannons_fired = False  # Reiniciar al desactivar

    def mark_cannons_as_fired(self) -> None:
        self.cannons_fired = True  # Marca los cañones como disparados

