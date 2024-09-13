"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the specialization of PowerUp to activate the cannons on the paddle.
"""

from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class CannonsPowerUp(PowerUp):
    """
    Power-up to activate the cannons on the paddle.
    """

    def __init__(self, x: float, y: float) -> None:
        # Usamos el frame 1 para representar los cañones
        super().__init__(x, y, 1)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        # Activar los cañones del paddle
        play_state.paddle.activate_cannons()  
        self.in_play = False  # El power-up desaparece una vez recogido
        settings.SOUNDS["load"].play()  # Reproducir el sonido de activación de los cañones
