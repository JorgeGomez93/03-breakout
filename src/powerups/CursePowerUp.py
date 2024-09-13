from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class CursePowerUp(PowerUp):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 3)
        self.duration = 10
        self.start_time = None

    def take(self, play_state: TypeVar("PlayState")) -> None:

        if play_state.curse_powerup_end_time is not None:
            self.in_play = False
            return

        play_state.invert_controls(True)

        settings.SOUNDS["negative"].stop()
        settings.SOUNDS["negative"].play()

        play_state.paddle.dec_size()

        play_state.curse_powerup_end_time = self.duration
        self.in_play = False
        play_state.paddle.vx = 0