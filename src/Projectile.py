from typing import Any, Tuple, Optional
import pygame
import settings

class Projectile:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 8
        self.height = 16
        self.vy = -200  # Velocidad vertical del proyectil
        self.texture = settings.TEXTURES["shot"]
        self.in_play = True

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y + self.height < 0:  # Si el proyectil sale por la parte superior
            self.in_play = False

    def render(self, surface) -> None:
        if self.in_play:
            surface.blit(self.texture, (self.x, self.y - settings.CANNON_HEIGHT))

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def is_off_screen(self) -> bool:
        # Suponiendo que la pantalla tiene un tamaño definido en settings.VIRTUAL_WIDTH y settings.VIRTUAL_HEIGHT
        return (self.x < 0 or self.x > settings.VIRTUAL_WIDTH or
                self.y < 0 or self.y > settings.VIRTUAL_HEIGHT)