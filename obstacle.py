# obstacle.py

import random

import pygame

from settings import (
    AIRBORNE_OBSTACLE_SCORE,
    AIRBORNE_HIGH_CLEARANCE,
    AIRBORNE_LOW_CLEARANCE,
    AIRBORNE_MID_CLEARANCE,
    CHICKEN_IMAGE_FILE,
    CRATE_IMAGE_FILE,
    ENEMY_IMAGE_FILE,
    GRENADE_IMAGE_FILE,
    GROUND_Y,
    MOLOTOV_IMAGE_FILE,
    SCREEN_WIDTH,
)


class Obstacle:
    AIRBORNE_LEVEL_CLEARANCES = (
        AIRBORNE_LOW_CLEARANCE,
        AIRBORNE_MID_CLEARANCE,
        AIRBORNE_HIGH_CLEARANCE,
    )
    GROUNDED_OBSTACLES = {
        "chicken": {
            "file": CHICKEN_IMAGE_FILE,
            "size": (30, 40),
        },
        "crate": {
            "file": CRATE_IMAGE_FILE,
            "size": (60, 60),
        },
        "enemy": {
            "file": ENEMY_IMAGE_FILE,
            "size": (70, 80),
        },
    }
    AIRBORNE_OBSTACLES = {
        "grenade": {
            "file": GRENADE_IMAGE_FILE,
            "size": (20, 30),
        },
        "molotov": {
            "file": MOLOTOV_IMAGE_FILE,
            "size": (30, 20),
        },
    }

    def __init__(self, score: int) -> None:
        self.obstacle_type = self.choose_obstacle_type(score)
        obstacle = self.get_obstacle_settings(self.obstacle_type)
        width, height = obstacle["size"]

        if self.obstacle_type in self.GROUNDED_OBSTACLES:
            y_position = GROUND_Y - height
        else:
            y_position = self.get_airborne_y_position(height)

        self.sprite = self.load_sprite(
            obstacle["file"],
            (width, height),
        )

        self.rect = pygame.Rect(
            SCREEN_WIDTH + 20,
            y_position,
            width,
            height,
        )
        self.position_x = float(self.rect.x)

    @classmethod
    def choose_obstacle_type(cls, score: int) -> str:
        """Choose from grounded obstacles until airborne obstacles unlock."""

        obstacle_types = list(cls.GROUNDED_OBSTACLES)

        if score >= AIRBORNE_OBSTACLE_SCORE:
            obstacle_types.extend(cls.AIRBORNE_OBSTACLES)

        return random.choice(obstacle_types)

    @classmethod
    def get_obstacle_settings(cls, obstacle_type: str) -> dict:
        """Return sprite settings for an obstacle type."""

        return {
            **cls.GROUNDED_OBSTACLES,
            **cls.AIRBORNE_OBSTACLES,
        }[obstacle_type]

    @classmethod
    def get_airborne_y_position(cls, height: int) -> int:
        """Choose one of three airborne height levels."""

        clearance = random.choice(cls.AIRBORNE_LEVEL_CLEARANCES)
        return GROUND_Y - clearance - height

    @staticmethod
    def load_sprite(sprite_file, size: tuple[int, int]) -> pygame.Surface:
        """Load and scale an obstacle sprite."""

        image = pygame.image.load(str(sprite_file)).convert_alpha()
        return pygame.transform.scale(image, size)

    def update(self, speed: float) -> None:
        """Move the obstacle toward the left side of the screen."""
        self.position_x -= speed
        self.rect.x = round(self.position_x)

    def is_off_screen(self) -> bool:
        """Return True after the obstacle leaves the screen."""
        return self.rect.right < 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the obstacle."""
        surface.blit(self.sprite, self.rect)

    def get_mask(self) -> pygame.mask.Mask:
        """Return a collision mask for the obstacle sprite."""

        return pygame.mask.from_surface(self.sprite)
