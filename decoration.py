# decoration.py

import random

import pygame

from settings import (
    CLOUD_IMAGE_FILE,
    CLOUD_MAX_WIDTH,
    CLOUD_MAX_Y,
    CLOUD_MIN_WIDTH,
    CLOUD_MIN_Y,
    CLOUD_SPEED,
    SCREEN_WIDTH,
)


class Cloud:
    def __init__(self, initial_x: float | None = None) -> None:
        width = random.randint(CLOUD_MIN_WIDTH, CLOUD_MAX_WIDTH)
        height = round(width * 0.6)
        y_position = random.randint(CLOUD_MIN_Y, CLOUD_MAX_Y)
        x_position = self.get_random_x_position(width, initial_x)

        self.sprite = self.load_sprite((width, height))
        self.rect = pygame.Rect(
            x_position,
            y_position,
            width,
            height,
        )
        self.position_x = float(self.rect.x)

    @staticmethod
    def get_random_x_position(
        width: int,
        initial_x: float | None,
    ) -> int:
        """Return either an initial in-frame x or a right-edge reset x."""

        if initial_x is not None:
            return round(initial_x)

        return SCREEN_WIDTH - width

    @staticmethod
    def load_sprite(size: tuple[int, int]) -> pygame.Surface:
        """Load and scale the cloud sprite."""

        image = pygame.image.load(str(CLOUD_IMAGE_FILE)).convert_alpha()
        return pygame.transform.scale(image, size)

    def update(self) -> None:
        """Move the cloud across the background."""

        self.position_x -= CLOUD_SPEED
        self.rect.x = round(self.position_x)

        if self.is_off_screen():
            self.reset_position()

    def is_off_screen(self) -> bool:
        """Return True after the cloud leaves the screen."""

        return self.rect.right < 0

    def reset_position(self) -> None:
        """Move the cloud back inside the right side of the frame."""

        self.position_x = float(SCREEN_WIDTH - self.rect.width)
        self.rect.x = round(self.position_x)
        self.rect.y = random.randint(CLOUD_MIN_Y, CLOUD_MAX_Y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the cloud."""

        surface.blit(self.sprite, self.rect)
