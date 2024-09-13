from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class StickyBallPowerUp(PowerUp):
    """
    Power-up to stick ball on the paddle.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 0)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.sticky_balls = True  
        self.in_play = False
        settings.SOUNDS["sticky"].stop()
        settings.SOUNDS["sticky"].play()
