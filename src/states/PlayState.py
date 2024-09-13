"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer
from src.Projectile import Projectile

import settings
import src.powerups
class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])

        self.projectiles = params.get("projectiles", [])
        self.paddle.cannons_active = params.get("cannons_active", False)
        self.paddle.cannons_fired = params.get("cannons_fired", False)
        self.controls_inverted = params.get("controls_inverted", False)
        self.sticky_balls = params.get("sticky_balls", False)

        self.timer = Timer()
        self.curse_powerup_end_time = params.get("curse_powerup_end_time", None)

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()
        else:
            self.paddle.vx = self.paddle.vx or 0

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

    def update(self, dt: float) -> None:
        self.timer.update(dt)

        if self.curse_powerup_end_time is not None:
            self.curse_powerup_end_time -= dt
            if self.curse_powerup_end_time <= 0:
                self.curse_powerup_end_time = None
                self.invert_controls(False)

        self.paddle.update(dt)

        for ball in self.balls:
            if self.sticky_balls and ball.collides(self.paddle):
                ball.set_sticky(True)
                ball.x = self.paddle.x + self.paddle.width // 2 - ball.width // 2
                ball.y = self.paddle.y - ball.height
            else:
                # Actualización normal de la bola
                ball.update(dt)
                ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle) and not self.sticky_balls:
                settings.SOUNDS["paddle_hit"].stop()
                settings.SOUNDS["paddle_hit"].play()
                ball.rebound(self.paddle)
                ball.push(self.paddle)

            # Check collision with brickset
            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())

            if brick is None:
                continue

            brick.hit()
            self.score += brick.score()
            ball.rebound(brick)

            # Check earn life
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            # Check growing up of the paddle
            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            # Chance to generate two more balls
            if random.random() < 0.1:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("TwoMoreBall").create(
                        r.centerx - 8, r.centery - 8
                    )
                )
            # Cannons
            if random.random() < 0.05:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("CannonsPowerUp").create(
                        r.centerx - 8, r.centery - 8
                    )
                )

            # StickyBall
            if random.random() < 0.05:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("StickyBallPowerUp").create(
                        r.centerx - 8, r.centery - 8
                    )
                )

            # CursePowerUp
            if random.random() < 0.2:  # Ajusta la probabilidad según lo necesites
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("CursePowerUp").create(
                        r.centerx - 8, r.centery - 8
                    )
                )
        # Actualización de los proyectiles
        self.update_projectiles(dt)

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.in_play]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            self.sticky_balls = False  # Desactiva el estado pegajoso al perder una vida
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.paddle.deactivate_cannons()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                    cannons_active=self.paddle.cannons_active, 
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self)

        # Remove powerups that are not in play
        self.powerups = [p for p in self.powerups if p.in_play]

        # Check victory
        if self.brickset.size == 1 and next(
            (True for _, b in self.brickset.bricks.items() if b.broken), False
        ):
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                cannons_active=self.paddle.cannons_active,
                sticky_balls=self.sticky_balls,  # Restaurar estado pegajoso
            )

    def update_projectiles(self, dt: float) -> None:
        # Actualizar proyectiles y manejar colisiones
        for projectile in self.projectiles:
            projectile.update(dt)

            if projectile.is_off_screen():
                self.projectiles.remove(projectile)
                continue

            colliding_brick = self.brickset.get_colliding_brick(projectile.get_collision_rect())
            if colliding_brick and projectile.collides(colliding_brick):
                colliding_brick.hit()
                self.score += colliding_brick.score()
                self.projectiles.remove(projectile)
                # Reproducir sonido de explosión
                settings.SOUNDS["paddle_hit"].stop()
                settings.SOUNDS["explosion1"].play()

        if not self.projectiles and self.paddle.cannons_fired:
            self.paddle.deactivate_cannons()
            self.paddle.cannons_fired = False  # Reset after deactivating

    def fire_projectiles(self) -> None:
        # Dispara proyectiles desde los cañones del paddle si están activos
        if self.paddle.cannons_active and len(self.projectiles) < 2:
            settings.SOUNDS["gun_fire"].play()
            left_projectile = Projectile(self.paddle.x - 12 , self.paddle.y + self.paddle.height // 2)
            right_projectile = Projectile(self.paddle.x + self.paddle.width + 4, self.paddle.y + self.paddle.height // 2)
            self.projectiles.extend([left_projectile, right_projectile])
            self.paddle.mark_cannons_as_fired()

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )
        
        # Renderizar proyectiles
        for projectile in self.projectiles:
            projectile.render(surface)

        self.brickset.render(surface)

        self.paddle.render(surface)

        for ball in self.balls:
            ball.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

        if self.curse_powerup_end_time is not None:
            time_remaining = max(0, int(self.curse_powerup_end_time))
            render_text(
                surface,
                f"Curse Time: {time_remaining}",
                settings.FONTS["tiny"],
                settings.VIRTUAL_WIDTH - 200,
                5,
                (255, 0, 0),
            )

    def on_input(self, input_id: str, input_data: InputData) -> None:

        # Manejo de controles invertidos
        if self.controls_inverted:
            if input_id == "move_left":
                input_id = "move_right"
            elif input_id == "move_right":
                input_id = "move_left"

        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
        elif input_id == "fire_projectiles" and input_data.pressed:
            self.fire_projectiles()
        elif input_id == "enter" and input_data.pressed:
            self.reset_sticky_balls()
            for ball in self.balls:
                if ball.is_sticky():
                    ball.vx = random.randint(-80, 80)
                    ball.vy = random.randint(-170, -100)
                    ball.set_sticky(False)
            self.sticky_balls = False
        elif input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause",
                level=self.level,
                score=self.score,
                lives=self.lives,
                paddle=self.paddle,
                balls=self.balls,
                brickset=self.brickset,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                powerups=self.powerups,
                projectiles=self.projectiles,
                cannons_fired=self.paddle.cannons_fired,
                cannons_active=self.paddle.cannons_active,
                sticky_balls=self.sticky_balls,
                controls_inverted=self.controls_inverted,
                curse_powerup_end_time=self.curse_powerup_end_time,
            )

    def invert_controls(self, state: bool) -> None:
        self.controls_inverted = state

    def reset_sticky_balls(self):
        for ball in self.balls:
            if ball.is_sticky():
                ball.x = self.paddle.x + self.paddle.width // 2 - ball.width // 2
                ball.y = self.paddle.y - ball.height
