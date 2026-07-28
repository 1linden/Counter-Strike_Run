# game.py

import random
import sys

import pygame

from decoration import Cloud
from obstacle import Obstacle
from player import Player
from settings import (
    BACKGROUND_COLOR,
    CLOUD_COUNT,
    FPS,
    FONT_FILE,
    FONT_NAME,
    GAME_OVER_SOUND_FILE,
    GROUND_COLOR,
    GROUND_LINE_COLOR,
    GROUND_Y,
    JUMP_SOUND_FILE,
    MAX_OBSTACLE_GAP_PIXELS,
    MAX_SPEED,
    MIN_OBSTACLE_GAP_PIXELS,
    NEXT_LEVEL_SOUND_FILE,
    RESTART_BUTTON_IMAGE_FILE,
    SCORE_FLASH_COUNT,
    SCORE_FLASH_INTERVAL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPEED_ACCELERATION,
    STARTING_SPEED,
    TEXT_ANTIALIAS,
    TEXT_COLOR,
    TITLE,
)


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()

        self.font = self.load_font(24)
        self.jump_sound = self.load_sound(JUMP_SOUND_FILE)
        self.next_level_sound = self.load_sound(NEXT_LEVEL_SOUND_FILE)
        self.game_over_sound = self.load_sound(GAME_OVER_SOUND_FILE)
        self.restart_button = self.load_image(
            RESTART_BUTTON_IMAGE_FILE
        )

        self.high_score = 0
        self.has_finished_game = False
        self.jump_needs_release = False

        self.reset()

    @staticmethod
    def load_font(size: int) -> pygame.font.Font:
        """Load Emulogic from assets, system fonts, or Pygame's fallback."""

        if FONT_FILE.exists():
            return pygame.font.Font(str(FONT_FILE), size)

        system_font = pygame.font.match_font(FONT_NAME)
        return pygame.font.Font(system_font, size)

    @staticmethod
    def load_sound(sound_file):
        """Load a sound effect if the mixer and file are available."""

        if not sound_file.exists():
            return None

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                return None

        try:
            return pygame.mixer.Sound(str(sound_file))
        except pygame.error:
            return None

    @staticmethod
    def play_sound(sound) -> None:
        """Play a loaded sound effect."""

        if sound is not None:
            sound.play()

    @staticmethod
    def load_image(image_file):
        """Load a UI image if the file is available."""

        if not image_file.exists():
            return None

        return pygame.image.load(str(image_file)).convert_alpha()

    def reset(self) -> None:
        """Reset all values needed for a new game."""

        self.player = Player()
        self.obstacles: list[Obstacle] = []
        self.clouds = self.create_clouds()

        self.score = 0.0
        self.distance_ran = 0.0
        self.speed = STARTING_SPEED
        self.next_level_score = 100
        self.score_flash_timer = 0
        self.flashing_score = 0

        self.spawn_timer = 0.0
        self.next_spawn_time = self.get_next_spawn_time()

        self.game_over = False

    def spawn_obstacle(self) -> None:
        """Create a new obstacle."""

        self.obstacles.append(Obstacle(int(self.score)))

        self.spawn_timer = 0.0
        self.next_spawn_time = self.get_next_spawn_time()

    def get_next_spawn_time(self) -> float:
        """Convert a random obstacle gap distance into seconds."""

        gap_pixels = random.randint(
            MIN_OBSTACLE_GAP_PIXELS,
            MAX_OBSTACLE_GAP_PIXELS,
        )
        return gap_pixels / (self.speed * FPS)

    def handle_events(self) -> None:
        """Process keyboard and window events."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button_was_clicked(event.pos):
                    self.reset()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.game_over:
                        self.reset()
                        self.jump_needs_release = True
                    else:
                        if self.player.jump():
                            self.play_sound(self.jump_sound)

                if event.key == pygame.K_r and self.game_over:
                    self.reset()

                if event.key == pygame.K_ESCAPE:
                    self.quit_game()

        keys = pygame.key.get_pressed()
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP]

        if not jump_pressed:
            self.jump_needs_release = False

        if not self.game_over:
            if jump_pressed and not self.jump_needs_release:
                if self.player.jump():
                    self.play_sound(self.jump_sound)

            self.player.set_crouching(keys[pygame.K_DOWN])

    def update(self) -> None:
        """Update all game objects."""

        if self.game_over:
            return

        self.player.update()

        self.update_obstacle_spawning()
        self.update_obstacles()
        self.update_clouds()
        self.update_speed_and_score()
        self.check_collisions()

    @staticmethod
    def create_clouds() -> list[Cloud]:
        """Create a fixed set of clouds spread across the frame."""

        spacing = SCREEN_WIDTH / CLOUD_COUNT
        return [
            Cloud(initial_x=index * spacing)
            for index in range(CLOUD_COUNT)
        ]

    def update_obstacle_spawning(self) -> None:
        """Count seconds and create obstacles at random distances."""

        self.spawn_timer += 1 / FPS

        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_obstacle()

    def update_obstacles(self) -> None:
        """Move obstacles and remove those that leave the screen."""

        for obstacle in self.obstacles:
            obstacle.update(self.speed)

        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.is_off_screen()
        ]

    def update_clouds(self) -> None:
        """Move clouds across the background."""

        for cloud in self.clouds:
            cloud.update()

    def check_collisions(self) -> None:
        """Check whether the player touches an obstacle."""

        player_mask = self.player.get_mask()

        for obstacle in self.obstacles:
            if not self.player.rect.colliderect(obstacle.rect):
                continue

            offset = (
                obstacle.rect.left - self.player.rect.left,
                obstacle.rect.top - self.player.rect.top,
            )

            if player_mask.overlap(obstacle.get_mask(), offset):
                self.end_game()
                return

    def end_game(self) -> None:
        """End the current run and update the high score."""

        self.game_over = True
        self.has_finished_game = True
        self.play_sound(self.game_over_sound)

        self.high_score = max(
            self.high_score,
            int(self.score),
        )

    def update_speed_and_score(self) -> None:
        """Update speed, distance, and score for the current frame."""

        self.speed = min(
            MAX_SPEED,
            self.speed + SPEED_ACCELERATION,
        )

        self.distance_ran += self.speed
        self.score = int(self.distance_ran * 0.025)

        while self.score >= self.next_level_score:
            self.play_sound(self.next_level_sound)
            self.start_score_flash(self.next_level_score)
            self.next_level_score += 100

        if self.score_flash_timer > 0:
            self.score_flash_timer -= 1

    def start_score_flash(self, score: int) -> None:
        """Flash a static score after each 100-point milestone."""

        self.flashing_score = score
        self.score_flash_timer = (
            SCORE_FLASH_COUNT * SCORE_FLASH_INTERVAL * 2
        )

    def draw(self) -> None:
        """Draw the current game frame."""

        self.draw_background()

        for cloud in self.clouds:
            cloud.draw(self.screen)

        self.player.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        self.draw_score()

        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_background(self) -> None:
        """Draw a simple Counter-Strike-inspired environment."""

        self.screen.fill(BACKGROUND_COLOR)

        # Ground
        pygame.draw.rect(
            self.screen,
            GROUND_COLOR,
            (
                0,
                GROUND_Y,
                SCREEN_WIDTH,
                SCREEN_HEIGHT - GROUND_Y,
            ),
        )

        pygame.draw.line(
            self.screen,
            GROUND_LINE_COLOR,
            (0, GROUND_Y),
            (SCREEN_WIDTH, GROUND_Y),
            4,
        )

    def draw_score(self) -> None:
        """Display the current score and high score."""

        display_score = self.get_display_score()
        current_score_text = f"{display_score:05d}"

        if self.current_score_is_hidden():
            current_score_text = " " * len(current_score_text)

        if self.has_finished_game:
            score_text = f"HI {self.high_score:05d} {current_score_text}"
        else:
            score_text = current_score_text

        speed_surface = self.font.render(
            f"Speed {self.speed:.1f}",
            TEXT_ANTIALIAS,
            TEXT_COLOR,
        )

        score_surface = self.font.render(
            score_text,
            TEXT_ANTIALIAS,
            TEXT_COLOR,
        )

        score_rect = score_surface.get_rect(
            topright=(SCREEN_WIDTH - 25, 20)
        )

        self.screen.blit(score_surface, score_rect)
        #self.screen.blit(speed_surface, (25, 55))

    def current_score_is_hidden(self) -> bool:
        """Return True while the current score is in a flash-off phase."""

        if self.score_flash_timer <= 0:
            return False

        return (
            self.score_flash_timer // SCORE_FLASH_INTERVAL
        ) % 2 == 1

    def get_display_score(self) -> int:
        """Return the score value that should be visible in the HUD."""

        if self.score_flash_timer > 0 and not self.game_over:
            return self.flashing_score

        return int(self.score)

    def draw_game_over_screen(self) -> None:
        """Display the game-over message."""

        game_over_surface = self.font.render(
            "G A M E  O V E R",
            TEXT_ANTIALIAS,
            TEXT_COLOR,
        )

        game_over_rect = game_over_surface.get_rect(
            center=(SCREEN_WIDTH // 2, 180)
        )

        self.screen.blit(game_over_surface, game_over_rect)

        if self.restart_button is not None:
            self.screen.blit(
                self.restart_button,
                self.get_restart_button_rect(),
            )

    def get_restart_button_rect(self) -> pygame.Rect | None:
        """Return the centered restart button rectangle."""

        if self.restart_button is None:
            return None

        return self.restart_button.get_rect(
            center=(SCREEN_WIDTH // 2, 245)
        )

    def restart_button_was_clicked(
        self,
        position: tuple[int, int],
    ) -> bool:
        """Return True when the game-over restart button is clicked."""

        if not self.game_over:
            return False

        restart_rect = self.get_restart_button_rect()
        return (
            restart_rect is not None
            and restart_rect.collidepoint(position)
        )

    def run(self) -> None:
        """Run the main game loop."""

        while True:
            self.clock.tick(FPS)

            self.handle_events()
            self.update()
            self.draw()

    @staticmethod
    def quit_game() -> None:
        """Close Pygame and terminate the program."""

        pygame.quit()
        sys.exit()
