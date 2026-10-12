#!/usr/bin/env python3
"""Simple Angry Birds-inspired game in Python using pygame."""
import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Optional

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
ORANGE = (255, 165, 0)

FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 32)
SMALL_FONT = pygame.font.SysFont("Arial", 14)


def draw_grass(surface):
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

    def is_off_screen(self, margin=100) -> bool:
        return (self.y > HEIGHT + margin or
                self.x < -margin or
                self.x > WIDTH + margin)

    def draw(self, surface):
        color = self.color if not self.caught else GRAY
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
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
    health: int = 1
    color: tuple = RED
    original_health: int = 1

    def __post_init__(self):
        self.original_health = self.health


class Structure:
    def __init__(self, bricks: List[Brick]):
        self.bricks = bricks

    def draw(self, surface):
        for brick in self.bricks:
            pygame.draw.rect(surface, brick.color, (brick.x, brick.y, brick.width, brick.height))
            pygame.draw.rect(surface, BLACK, (brick.x, brick.y, brick.width, brick.height), 2)

    def hit(self, pos) -> tuple[bool, int]:
        for brick in self.bricks:
            if brick.x < pos[0] < brick.x + brick.width and brick.y < pos[1] < brick.y + brick.height:
                original_health = brick.original_health
                brick.health -= 1
                if brick.health >= 2:
                    brick.color = BROWN
                elif brick.health == 1:
                    brick.color = RED
                elif brick.health <= 0:
                    self.bricks.remove(brick)
                points = 10 * original_health
                return True, points
        return False, 0


def create_level1_structure():
    bricks = []
    for i in range(8):
        bricks.append(Brick(x=350 + i * 60, y=HEIGHT - 150, width=50, height=30, health=2, color=BROWN))
    for i in range(5):
        bricks.append(Brick(x=380 + i * 60, y=HEIGHT - 220, width=50, height=30, health=1, color=RED))
    for i in range(3):
        bricks.append(Brick(x=400 + i * 60, y=HEIGHT - 290, width=50, height=30, health=1, color=RED))
    return bricks


def main():
    running = True
    game_over = False
    level_complete = False
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

    start_pos = (0, 0)
    angle = 0
    power = 0
    max_power = 10
    pulling = False

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_r:
                level = 1
                score = 0
                birds = [
                    Bird(x=150, y=HEIGHT - 100, radius=20, color=RED, type_name="red"),
                    Bird(x=150, y=HEIGHT - 130, radius=20, color=BLUE, type_name="blue"),
                    Bird(x=150, y=HEIGHT - 160, radius=20, color=YELLOW, type_name="yellow"),
                ]
                current_bird_index = 0
                current_bird = birds[current_bird_index]
                structure = Structure(create_level1_structure())
                angle = 0
                power = 0
                level_complete = False
                game_over = False
                pulling = False
            if event.key == pygame.K_c and current_bird and current_bird.launched:
                if current_bird.type_name == "blue" and not current_bird.caught:
                    current_bird.caught = True
                    for i in range(3):
                        angle_offset = i * 30 - 30
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
                if current_bird.type_name == "yellow" and not current_bird.caught:
                    current_bird.caught = True
                    current_bird.velocity[0] *= 3
                    current_bird.velocity[1] *= 3
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_bird and not current_bird.launched and not game_over and not level_complete:
                    pulling = True
                    start_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                if pulling and current_bird and not current_bird.launched:
                    end_pos = pygame.mouse.get_pos()
                    dx = end_pos[0] - start_pos[0]
                    dy = start_pos[1] - end_pos[1]
                    angle = math.degrees(math.atan2(dy, dx))
                    power = min(math.hypot(dx, dy) / 20, max_power)
                    current_bird.launch(angle, power)
                    pulling = False
                    current_bird_index += 1
                    if current_bird_index < len(birds):
                        current_bird = birds[current_bird_index]
                    else:
                        current_bird = None

        if current_bird and not current_bird.launched and not game_over and not level_complete:
            if pulling and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] - start_pos[0]
                dy = start_pos[1] - mouse_pos[1]
                angle = math.degrees(math.atan2(dy, dx))
                power = min(math.hypot(dx, dy) / 20, max_power)
            else:
                angle = 0
                power = 0

        for bird in birds:
            if bird.launched and not bird.caught:
                bird.update()
                hit, points = structure.hit((bird.x, bird.y))
                if hit:
                    bird.caught = True
                    score += points

        birds = [b for b in birds if not (b.caught and b.launched and b.is_off_screen())]

        if len(structure.bricks) == 0:
            level_complete = True
            score += 100 * level

        birds_not_yet_launched = [b for b in birds if not b.launched]
        active_birds = [b for b in birds if b.launched and not b.caught]
        if len(birds_not_yet_launched) == 0 and len(active_birds) == 0 and not level_complete and not game_over:
            game_over = True

        screen.fill((135, 206, 235))

        draw_grass(screen)
        structure.draw(screen)

        for bird in birds:
            bird.draw(screen)

        if current_bird and not current_bird.launched and not game_over and not level_complete:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - current_bird.x
            dy = current_bird.y - mouse_pos[1]
            angle = math.degrees(math.atan2(dy, dx))
            power = min(math.hypot(dx, dy) / 20, max_power)

            temp_vel = [power * math.cos(math.radians(angle)),
                        -power * math.sin(math.radians(angle))]
            traj_points = [(current_bird.x, current_bird.y)]
            bx, by = current_bird.x, current_bird.y
            gravity = 0.5
            for i in range(20):
                bx += temp_vel[0] * 3
                by += temp_vel[1] * 3 + 0.5 * gravity * (i + 1)
                if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
                    traj_points.append((bx, by))
                else:
                    break

            for i in range(len(traj_points) - 1):
                width = max(1, int(3 * (1 - i / len(traj_points))))
                pygame.draw.line(screen, ORANGE,
                                 (int(traj_points[i][0]), int(traj_points[i][1])),
                                 (int(traj_points[i+1][0]), int(traj_points[i+1][1])), width)

            draw_power_bar(screen, angle, power, max_power)
            instruct_text = FONT.render("Drag the bird to launch", True, WHITE)
            screen.blit(instruct_text, (WIDTH // 2 - 100, HEIGHT - 40))

        score_text = FONT.render(f"Score: {score}", True, BLACK)
        level_text = FONT.render(f"Level: {level}", True, BLACK)
        birds_launched_count = current_bird_index + 1
        birds_left = FONT.render(f"Birds: {birds_launched_count}/{len(birds)}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(level_text, (20, 50))
        screen.blit(birds_left, (20, 80))

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
    angle_text = FONT.render(f"Angle: {int(angle)}°", True, WHITE)
    surface.blit(angle_text, (20, 20))
    pygame.draw.rect(surface, GRAY, (20, 50, 200, 20))
    bar_width = int((power / max_power) * 200)
    pygame.draw.rect(surface, YELLOW, (20, 50, bar_width, 20))
    power_text = FONT.render(f"Power: {int(power)}/{max_power}", True, BLACK)
    surface.blit(power_text, (20, 70))


if __name__ == "__main__":
    main()
