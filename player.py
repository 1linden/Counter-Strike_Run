# player.py

import pygame

from settings import (
    GRAVITY,
    GROUND_Y,
    JUMP_STRENGTH,
    PLAYER_CROUCH_ANIMATION_INTERVAL,
    PLAYER_CROUCH_FRAME_FILES,
    PLAYER_CROUCHING_HEIGHT,
    PLAYER_JUMP_FILE,
    PLAYER_RUN_ANIMATION_INTERVAL,
    PLAYER_RUN_FRAME_FILES,
    PLAYER_START_X,
    PLAYER_STANDING_HEIGHT,
    PLAYER_WIDTH,
)


class Player:
    def __init__(self) -> None:
        self.standing_height = PLAYER_STANDING_HEIGHT
        self.crouching_height = PLAYER_CROUCHING_HEIGHT
        self.run_frames = [
            self.load_sprite(
                frame_file,
                (PLAYER_WIDTH, PLAYER_STANDING_HEIGHT),
            )
            for frame_file in PLAYER_RUN_FRAME_FILES
        ]
        self.crouch_frames = [
            self.load_sprite(
                frame_file,
                (PLAYER_WIDTH, PLAYER_CROUCHING_HEIGHT),
            )
            for frame_file in PLAYER_CROUCH_FRAME_FILES
        ]
        self.jump_frame = self.load_sprite(
            PLAYER_JUMP_FILE,
            (PLAYER_WIDTH, PLAYER_STANDING_HEIGHT),
        )
        self.run_frame = 0
        self.run_timer = 0
        self.crouch_frame = 0
        self.crouch_timer = 0

        self.rect = pygame.Rect(
            PLAYER_START_X,
            GROUND_Y - self.standing_height,
            PLAYER_WIDTH,
            self.standing_height,
        )

        self.velocity_y = 0
        self.on_ground = True
        self.crouching = False

    @staticmethod
    def load_sprite(sprite_file, size: tuple[int, int]) -> pygame.Surface:
        """Load and scale a player sprite."""

        image = pygame.image.load(str(sprite_file)).convert_alpha()
        return pygame.transform.scale(image, size)

    def jump(self) -> bool:
        """Make the player jump if they are touching the ground."""
        if self.on_ground and not self.crouching:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
            return True

        return False

    def set_crouching(self, crouching: bool) -> None:
        """Start or stop crouching."""

        # Prevent the player from changing height in mid-air.
        if not self.on_ground:
            return

        if crouching and not self.crouching:
            bottom_position = self.rect.bottom

            self.rect.height = self.crouching_height
            self.rect.bottom = bottom_position

            self.crouching = True

        elif not crouching and self.crouching:
            bottom_position = self.rect.bottom

            self.rect.height = self.standing_height
            self.rect.bottom = bottom_position

            self.crouching = False

    def update(self) -> None:
        """Update the player's vertical movement."""

        if self.on_ground:
            if not self.crouching:
                self.run_timer += 1

                if self.run_timer >= PLAYER_RUN_ANIMATION_INTERVAL:
                    self.run_frame = (self.run_frame + 1) % len(
                        self.run_frames
                    )
                    self.run_timer = 0
            else:
                self.crouch_timer += 1

                if self.crouch_timer >= PLAYER_CROUCH_ANIMATION_INTERVAL:
                    self.crouch_frame = (self.crouch_frame + 1) % len(
                        self.crouch_frames
                    )
                    self.crouch_timer = 0

        self.velocity_y += GRAVITY
        self.rect.y += round(self.velocity_y)

        # Stop the player from falling below the ground.
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.on_ground = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player on the screen."""

        surface.blit(self.get_current_sprite(), self.rect)

    def get_current_sprite(self) -> pygame.Surface:
        """Return the current player sprite for drawing and collisions."""

        if not self.on_ground:
            return self.jump_frame

        if self.crouching:
            return self.crouch_frames[self.crouch_frame]

        return self.run_frames[self.run_frame]

    def get_mask(self) -> pygame.mask.Mask:
        """Return a collision mask for the current player sprite."""

        return pygame.mask.from_surface(self.get_current_sprite())
