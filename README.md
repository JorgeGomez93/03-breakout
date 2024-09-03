
Tarea 3: Breakout

Objetivos

Leer y comprender todo el código fuente del juego Breakout de la Clase 3.
Añadir tres nuevos potenciadores al juego.

Para asegurarte de que cumples con el estándar PEP8 para el estilo de código, puedes ejecutar el comando black ..
Especificaciones

- Crea un nuevo potenciador que permita al jugador tomar la bola de nuevo. Es decir, cuando el jugador tome el potenciador y la bola colisione con la paleta, la bola debería quedar adherida a la paleta en la posición de la colisión en lugar de rebotar. Al igual que en el estado de servicio, el jugador podrá mover la paleta y lanzar la bola de nuevo presionando la tecla espacio. Este potenciador debe estar disponible por un tiempo limitado. La cantidad de tiempo queda a tu criterio.

- Crea un nuevo potenciador que genere un objeto adherido a la paleta. Es decir, un par de cañones que disparan proyectiles para destruir ladrillos. Cada cañón debería estar adherido a los extremos (izquierdo y derecho) de la paleta. Al presionar una tecla (por ejemplo, F), cada cañón debería disparar un proyectil (al mismo tiempo). Ambos proyectiles deberían viajar verticalmente y deberían impactar los ladrillos de alguna manera: a) romper cada ladrillo en su camino y destruirse al colisionar con el techo de la escena; b) romper solo un ladrillo y destruir el proyectil; o c) impactar como la bola; eso depende de ti. El usuario no debería poder disparar más proyectiles mientras haya proyectiles existentes en la escena. La duración de este potenciador depende de la implementación, es decir: a) debería eliminarse después de disparar; o b) puedes definir una duración como en el potenciador anterior.

- Crea otro potenciador de tu elección. Debe ser descrito en el README.md.

Cómo enviar

Graba un screencast, que no exceda los 5 minutos de duración (y no se suba más de dos semanas antes de tu entrega de este proyecto) en el que demuestres la funcionalidad de tu aplicación. Sube ese video a YouTube (como no listado o público, pero no privado) o a algún otro lugar.
Sube el código fuente a un repositorio de Git.
Envía este formulario.
Fecha límite Tienes que enviar esta tarea antes del 27/07/2024 - 23:59:59.


se agregan las texturas a la carpeta assets respectivamente para sonidos y graficos

left_cannon.png
right_cannon.png
shot.png

se agregan los sonidos 

gun_fire.wav
explosion1.ogg

    # Nuevos sonidos añadidos en Python.py
    "gun_fire": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "gun_fire.wav"),
    "explosion1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "explosion1.ogg"),

    # Nuevas texturas añadidas
    "left_cannon": pygame.image.load(BASE_DIR / "assets" / "graphics" / "left_cannon.png"),
    "right_cannon": pygame.image.load(BASE_DIR / "assets" / "graphics" / "right_cannon.png"),
    "shot": pygame.image.load(BASE_DIR / "assets" / "graphics" / "shot.png"),


    tengo la siguiente clase playing:

    import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

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

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        for ball in self.balls:
            ball.update(dt)
            ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle):
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

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.in_play]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
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
            )

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

        self.brickset.render(surface)

        self.paddle.render(surface)

        for ball in self.balls:
            ball.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
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
            )

quiero agregar los cañones (las imagenes que acabamos de cargar en settings) siempre a los lados de la paleta como lo puedo realizar? recuerda comentarme el codigo de los cambios que realices