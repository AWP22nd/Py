#!/usr/bin/env python3
"""Text-based Angry Birds game for headless environments."""
import sys
import time
import math
import random
from dataclasses import dataclass
from typing import List

# Game constants
WIDTH = 70
HEIGHT = 20
GRAVITY = 0.5
MAX_POWER = 10

# Colors (ASCII representations)
BIRD_RED = "O"
BIRD_BLUE = "o"
BIRD_YELLOW = "0"
BRICK = "#"
GROUND = "="
SKY = "."

@dataclass
class Bird:
    x: int
    y: int
    radius: int
    symbol: str
    velocity: List[float] = None
    launched: bool = False
    caught: bool = False
    type_name: str = "red"

    def __post_init__(self):
        if self.velocity is None:
            self.velocity = [0, 0]

    def launch(self, angle, power):
        self.launched = True
        rad = math.radians(angle)
        self.velocity = [power * math.cos(rad), -power * math.sin(rad)]

    def update(self):
        if not self.launched or self.caught:
            return
        self.velocity[1] += GRAVITY
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def draw(self, screen):
        if 0 <= self.x < WIDTH and 0 <= self.y < HEIGHT:
            screen[int(self.y)][int(self.x)] = self.symbol


@dataclass
class Brick:
    x: int
    y: int
    width: int
    height: int
    health: int = 1


class Structure:
    def __init__(self, bricks: List[Brick]):
        self.bricks = bricks

    def draw(self, screen):
        for brick in self.bricks:
            for dy in range(brick.height):
                for dx in range(brick.width):
                    if 0 <= brick.x + dx < WIDTH and 0 <= brick.y + dy < HEIGHT:
                        screen[brick.y + dy][brick.x + dx] = BRICK

    def hit(self, pos):
        """Check if position hits a brick."""
        bx, by = pos
        for brick in self.bricks:
            if brick.x <= bx < brick.x + brick.width and brick.y <= by < brick.y + brick.height:
                brick.health -= 1
                if brick.health <= 0:
                    self.bricks.remove(brick)
                return True
        return False


def clear_screen():
    """Clear terminal screen."""
    print("\033[H\033[J", end="")


def draw_game(screen, birds, structure, score, level, bird_index):
    """Draw the game state to terminal."""
    # Clear screen
    clear_screen()

    # Draw sky
    for y in range(5):
        for x in range(WIDTH):
            screen[y][x] = SKY

    # Draw ground
    for x in range(WIDTH):
        if 0 <= HEIGHT - 1 < HEIGHT:
            screen[HEIGHT - 1][x] = GROUND

    # Draw structure
    structure.draw(screen)

    # Draw birds
    for bird in birds:
        bird.draw(screen)

    # Draw UI
    print(f"=== Angry Birds Text v2 ===")
    print(f"Level: {level}  Score: {score}  Bird: {bird_index + 1}/{len(birds)}")
    print("=" * WIDTH)

    # Draw each row
    for row in screen:
        print("".join(row))


def main():
    running = True
    game_over = False
    level_complete = False
    level = 1
    score = 0

    # Initialize birds
    birds = [
        Bird(x=5, y=HEIGHT - 3, radius=2, symbol=BIRD_RED, type_name="red"),
        Bird(x=5, y=HEIGHT - 4, radius=2, symbol=BIRD_BLUE, type_name="blue"),
        Bird(x=5, y=HEIGHT - 5, radius=2, symbol=BIRD_YELLOW, type_name="yellow"),
    ]

    current_bird_index = 0
    current_bird = birds[current_bird_index]

    # Level 1 structure
    def create_level1():
        bricks = []
        # Bottom row
        for i in range(10):
            bricks.append(Brick(x=5 + i * 6, y=HEIGHT - 3, width=5, height=2, health=2))
        # Middle row (offset)
        for i in range(6):
            bricks.append(Brick(x=8 + i * 6, y=HEIGHT - 6, width=5, height=2, health=1))
        # Top row
        for i in range(3):
            bricks.append(Brick(x=10 + i * 6, y=HEIGHT - 9, width=5, height=2, health=1))
        return bricks

    structure = Structure(create_level1())

    # UI state
    pulling = False
    start_pos = (0, 0)
    angle = 0
    power = 0

    while running:
        clock_start = time.time()

        for event in __import__('sys').stdin.read(1) if False else []:
            pass  # Simplified - no real event handling in text version

        # In text version, we'll use key input
        try:
            key = sys.stdin.read(1)
        except:
            key = ""

        if key == 'q':
            running = False
        elif key == 'r':
            # Reset level
            level = 1
            score = 0
            birds = [
                Bird(x=5, y=HEIGHT - 3, radius=2, symbol=BIRD_RED, type_name="red"),
                Bird(x=5, y=HEIGHT - 4, radius=2, symbol=BIRD_BLUE, type_name="blue"),
                Bird(x=5, y=HEIGHT - 5, radius=2, symbol=BIRD_YELLOW, type_name="yellow"),
            ]
            current_bird_index = 0
            current_bird = birds[current_bird_index]
            structure = Structure(create_level1())
        elif key == ' ' and not current_bird.launched and not game_over and not level_complete:
            # Launch bird (space bar)
            # Calculate angle based on imagined drag
            # For text version, use fixed angle or calculate from mouse-like input
            angle = 45  # Default angle
            power = 8   # Default power
            current_bird.launch(angle, power)
            current_bird_index += 1
            if current_bird_index < len(birds):
                current_bird = birds[current_bird_index]
            else:
                current_bird = None

        # Update birds
        for bird in birds:
            if bird.launched and not bird.caught:
                bird.update()

                # Check collision with structure
                if structure.hit((int(bird.x), int(bird.y))):
                    bird.caught = True
                    score += 10

        # Check if all bricks destroyed
        if len(structure.bricks) == 0:
            level_complete = True
            score += 100 * level

        # Game over condition
        active_birds = [b for b in birds if b.launched and not b.caught]
        if not active_birds and not level_complete and current_bird_index >= len(birds):
            game_over = True

        # Draw game state
        screen = [['.' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        draw_game(screen, birds, structure, score, level, current_bird_index)

        # Small delay
        time.sleep(0.1)

    print("Terima kasih sudah bermain!")
    print(f"Skor akhir: {score}")


if __name__ == "__main__":
    main()