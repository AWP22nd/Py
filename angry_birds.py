#!/usr/bin/env python3
"""Simple Angry Birds-inspired game in Python using pygame."""
import pygame
import random
import math
from dataclasses import dataclass
from typing import List

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Birds Python - x Kay")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
PINK = (255, 180, 180)
GREEN_GRADIENT = [(34, 139, 34), (124, 252, 124)]

FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 32)
SMALL_FONT = pygame.font.SysFont("Arial", 14)


def draw_grass(surface):
    """Draw grass area at the bottom."""
    # Ground line
    pygame.draw.line(surface, GREEN, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 5)
    # Grass blades
    for i in range(0, WIDTH, 40):
        pygame.draw.polygon(surface, GREEN_GRADIENT[0], [
            (i, HEIGHT - 50),
            (i + 20, HEIGHT - 35),
            (i + 40, HEIGHT - 50),
            (i + 20, HEIGHT - 45)])


@dataclass
class Bird:
    x: float
    y: float
    radius: int
    color: tuple
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

    def update(self, gravity=0.5):
        if not self.launched or self.caught:
            return
        self.velocity[1] += gravity
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def draw(self, surface):
        color = self.color if not self.caught else GRAY
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        # Draw eye when launched
        if self.launched and not self.caught:
            eye_offset = 8
            eye_x = self.x + (self.velocity[0] * 0.1) if self.velocity[0] != 0 else self.x + eye_offset
            eye_y = self.y - self.radius + 5
            pygame.draw.circle(surface, BLACK, (int(eye_x), int(eye_y)), 3)


@dataclass
class Brick:
    x: float
    y: float
    width: int
    height: int
    health: int = 1  # 1=normal, 2=strong, 3=indestructible
    color: tuple = RED


class Structure:
    def __init__(self, bricks: List[Brick]):
        self.bricks = bricks

    def draw(self, surface):
        for brick in self.bricks:
            pygame.draw.rect(surface, brick.color, (brick.x, brick.y, brick.width, brick.height))
            pygame.draw.rect(surface, BLACK, (brick.x, brick.y, brick.width, brick.height), 2)

    def hit(self, pos):
        """Check if position hits a brick, reduce health or remove."""
        for brick in self.bricks:
            if brick.x < pos[0] < brick.x + brick.width and brick.y < pos[1] < brick.y + brick.height:
                brick.health -= 1
                # Change color based on health
                if brick.health >= 2:
                    brick.color = BROWN
                elif brick.health == 1:
                    brick.color = RED
                elif brick.health <= 0:
                    self.bricks.remove(brick)
                return True
        return False


def main():
    running = True
    game_over = False
    level_complete = False
    level = 1
    score = 0
    max_birds = 3

    # Create birds - different types with different abilities
    birds = [
        Bird(x=150, y=HEIGHT - 100, radius=20, color=RED, type_name="red"),
        Bird(x=150, y=HEIGHT - 130, radius=20, color=BLUE, type_name="blue"),
        Bird(x=150, y=HEIGHT - 160, radius=20, color=YELLOW, type_name="yellow"),
    ]

    current_bird_index = 0
    current_bird = birds[current_bird_index]

    # Level 1 structure
    def create_level1_structure():
        bricks = []
        # Bottom row - strong bricks
        for i in range(8):
            bricks.append(Brick(x=350 + i * 60, y=HEIGHT - 150, width=50, height=30, health=2, color=BROWN))
        # Middle row (offset) - normal bricks
        for i in range(5):
            bricks.append(Brick(x=380 + i * 60, y=HEIGHT - 220, width=50, height=30, health=1, color=RED))
        # Top row - breakable
        for i in range(3):
            bricks.append(Brick(x=400 + i * 60, y=HEIGHT - 290, width=50, height=30, health=1, color=RED))
        return bricks

    structure = Structure(create_level1_structure())

    # Physics state
    launching = False
    start_pos = (0, 0)
    angle = 0
    power = 0
    max_power = 10
    pulling = False

    # UI state
    show_trajectory = True
    trajectory_points = []

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    # Reset to level 1
                    level = 1
                    score = 0
                    max_birds = 3
                    birds = [
                        Bird(x=150, y=HEIGHT - 100, radius=20, color=RED, type_name="red"),
                        Bird(x=150, y=HEIGHT - 130, radius=20, color=BLUE, type_name="blue"),
                        Bird(x=150, y=HEIGHT - 160, radius=20, color=YELLOW, type_name="yellow"),
                    ]
                    current_bird_index = 0
                    current_bird = birds[current_bird_index]
                    structure = Structure(create_level1_structure())
                    launching = False
                    angle = 0
                    power = 0
                    level_complete = False

                if event.key == pygame.K_c and current_bird and current_bird.launched:
                    # Blue bird split ability (split into 3)
                    if current_bird.type_name == "blue" and not current_bird.caught:
                        current_bird.caught = True
                        # Create 3 smaller birds split from current position
                        for i in range(3):
                            angle_offset = i * 30 - 30  # -30, 0, +30 degrees
                            vel_power = 5
                            rad = math.radians(angle_offset)
                            vx = vel_power * math.cos(rad)
                            vy = -vel_power * math.sin(rad)
                            new_bird = Bird(
                                x=current_bird.x,
                                y=current_bird.y,
                                radius=12,
                                color=BLUE,
                                velocity=[vx, vy],
                                launched=True,
                                type_name="blue_split"
                            )
                            birds.append(new_bird)

                if event.key == pygame.K_f and current_bird and current_bird.launched:
                    # Yellow bird speed boost
                    if current_bird.type_name == "yellow" and not current_bird.caught:
                        current_bird.caught = True
                        current_bird.velocity[0] *= 3
                        current_bird.velocity[1] *= 3

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not current_bird.launched and not game_over and not level_complete:
                    pulling = True
                    start_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if pulling and not current_bird.launched:
                    end_pos = pygame.mouse.get_pos()
                    # Calculate angle from horizontal
                    dx = end_pos[0] - start_pos[0]
                    dy = start_pos[1] - end_pos[1]  # Inverted Y
                    angle = math.degrees(math.atan2(dy, dx))
                    power = min(math.hypot(dx, dy) / 20, max_power)
                    current_bird.launch(angle, power)
                    pulling = False
                    # Switch to next bird or handle game state
                    current_bird_index += 1
                    if current_bird_index < len(birds):
                        current_bird = birds[current_bird_index]
                    else:
                        current_bird = None  # All birds used

        if not current_bird.launched or (current_bird and current_bird.caught):
            # Handle dragging for launch
            if pulling and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] - start_pos[0]
                dy = start_pos[1] - mouse_pos[1]  # Inverted Y
                angle = math.degrees(math.atan2(dy, dx))
                power = min(math.hypot(dx, dy) / 20, max_power)
            else:
                angle = 0
                power = 0

        # Update all active birds
        birds_to_remove = []
        for bird in birds:
            if bird.launched and not bird.caught:
                bird.update()

                # Check collision with structure
                if structure.hit((bird.x, bird.y)):
                    bird.caught = True
                    # Award points based on bird type and structure health
                    points = 10 * (5 - bird.health) if hasattr(bird, 'health') else 10
                    score += points

        # Remove caught birds that are done
        birds = [b for b in birds if not (b.caught and b.launched and b not in birds_to_remove)]

        # Check if all bricks destroyed
        if len(structure.bricks) == 0:
            level_complete = True
            score += 100 * level  # Bonus for completing level

        # Game over if no birds left and level not complete
        active_birds = [b for b in birds if b.launched]
        if not active_birds and not level_complete and current_bird_index >= len(birds):
            game_over = True

        # Drawing
        screen.fill((135, 206, 235))  # Sky blue

        draw_grass(screen)
        structure.draw(screen)

        # Draw birds
        for bird in birds:
            bird.draw(screen)

        # Draw trajectory line when dragging or previewing
        if not current_bird.launched and not game_over and not level_complete:
            mouse_pos = pygame.mouse.get_pos()
            # Calculate trajectory
            dx = mouse_pos[0] - current_bird.x
            dy = current_bird.y - mouse_pos[1]
            angle = math.degrees(math.atan2(dy, dx))
            power = min(math.hypot(dx, dy) / 20, max_power)

            # Draw trajectory preview
            if show_trajectory:
                temp_vel = [power * math.cos(math.radians(angle)),
                            -power * math.sin(math.radians(angle))]
                traj_points = [current_bird]
                bx, by = current_bird.x, current_bird.y
                gravity = 0.5
                for _ in range(20):
                    bx += temp_vel[0] * 3
                    by += temp_vel[1] * 3 + 0.5 * gravity * _ * _
                    if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
                        traj_points.append((bx, by))
                    else:
                        break

                # Draw trajectory as thin lines
                for i in range(len(traj_points) - 1):
                    alpha = int(200 * (i / len(traj_points)))
                    color = (255, 165, 0, alpha) if alpha > 0 else (255, 165, 0)
                    # pygame doesn't support alpha well for lines, so use width variation
                    width = int(3 * (i / len(traj_points)))
                    pygame.draw.line(surface, (255, 180, 0),
                                     (int(traj_points[i][0]), int(traj_points[i][1])),
                                     (int(traj_points[i+1][0]), int(traj_points[i+1][1])), width)

            draw_power_bar(screen, angle, power, max_power)
            instruct_text = FONT.render("Drag the bird to launch", True, WHITE)
            screen.blit(instruct_text, (WIDTH // 2 - 100, HEIGHT - 40))

        # UI: Score and Level
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        level_text = FONT.render(f"Level: {level}", True, BLACK)
        birds_left = FONT.render(f"Birds: {current_bird_index + 1}/{len(birds)}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(level_text, (20, 50))
        screen.blit(birds_left, (20, 80))

        # Game over / Level complete
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            go_text = BIG_FONT.render("GAME OVER", True, RED)
            restart_text = FONT.render("Press R to restart or Q to quit", True, WHITE)
            final_score = FONT.render(f"Final Score: {score}", True, WHITE)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(final_score, (WIDTH // 2 - 80, HEIGHT // 2 + 10))
            screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 40))

        if level_complete:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(GREEN)
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            lc_text = BIG_FONT.render("LEVEL COMPLETE!", True, WHITE)
            restart_text = FONT.render("Press R to continue or Q to quit", True, BLACK)
            bonus_text = FONT.render(f"Bonus: +{100 * level} points!", True, WHITE)
            screen.blit(lc_text, (WIDTH // 2 - lc_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(bonus_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
            screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 40))

        pygame.display.flip()

    pygame.quit()


def draw_power_bar(surface, angle, power, max_power=10):
    """Draw angle and power indicators."""
    # Angle display
    angle_text = FONT.render(f"Angle: {int(angle)}°", True, WHITE)
    surface.blit(angle_text, (20, 20))

    # Power bar background
    pygame.draw.rect(surface, GRAY, (20, 50, 200, 20))
    # Power bar fill
    bar_width = int((power / max_power) * 200)
    pygame.draw.rect(surface, YELLOW, (20, 50, bar_width, 20))
    # Power text
    power_text = FONT.render(f"Power: {int(power)}/{max_power}", True, BLACK)
    surface.blit(power_text, (20, 70))


if __name__ == "__main__":
    main()
