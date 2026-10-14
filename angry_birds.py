#!/usr/bin/env python3
"""Angry Birds game in Python using pygame - authentic visual style."""
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

# ===== ANGRY BIRDS COLOR PALETTE =====
# Authentic Angry Birds colors
SKY_BLUE = (135, 206, 235)
DARK_SKY_BLUE = (95, 165, 182)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 52, 52)       # Red bird
BLUE_BIRD = (52, 96, 255) # Blue bird
YELLOW_BIRD = (255, 238, 52) # Yellow bird
BROWN = (139, 69, 19)     # Wood
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
PINK = (255, 180, 180)
ORANGE = (255, 165, 0)
GREEN = (50, 200, 50)
LIGHT_GREEN = (144, 238, 144)
YELLOW_ACCENT = (255, 255, 0)

# Fonts
FONT = pygame.font.SysFont("Arial", 20)
BIG_FONT = pygame.font.SysFont("Arial", 36)
SMALL_FONT = pygame.font.SysFont("Arial", 16)

# Game constants
GRAVITY = 0.8
MAX_POWER = 12
FPS = 60


@dataclass
class Bird:
    x: float
    y: float
    radius: int
    color: tuple
    type_name: str  # "red", "blue", "yellow"
    velocity: List[float] = None
    launched: bool = False
    caught: bool = False
    split_angles: List[float] = None  # For blue bird split

    def __post_init__(self):
        if self.velocity is None:
            self.velocity = [0, 0]
        if self.split_angles is None:
            self.split_angles = []

    def launch(self, angle: float, power: float):
        """Launch the bird with given angle (degrees) and power."""
        self.launched = True
        rad = math.radians(angle)
        self.velocity = [power * math.cos(rad), -power * math.sin(rad)]
        self.caught = False
        self.split_angles = []

    def update(self, structure: 'Structure'):
        """Update bird position with gravity."""
        if not self.launched or self.caught:
            return

        self.velocity[1] += GRAVITY
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Check collision with structure
        hit, points = structure.hit((self.x, self.y))
        if hit:
            self.caught = True
            # Award points based on bird type
            type_multiplier = {"red": 1, "blue": 1.5, "yellow": 1.2}
            self.score += int(10 * type_multiplier.get(self.type_name, 1))

    def is_off_screen(self, margin: int = 150) -> bool:
        """Check if bird is off screen."""
        return (self.y > HEIGHT + margin or
                self.x < -margin or
                self.x > WIDTH + margin)

    def draw(self, surface: pygame.Surface):
        """Draw the bird with authentic Angry Birds style."""
        # Determine color based on type
        if self.type_name == "red":
            bird_color = RED
            beak_color = (255, 85, 85)
        elif self.type_name == "blue":
            bird_color = BLUE_BIRD
            beak_color = (100, 150, 255)
        elif self.type_name == "yellow":
            bird_color = YELLOW_BIRD
            beak_color = (255, 215, 0)
        else:
            bird_color = RED
            beak_color = (255, 85, 85)

        # Draw bird body (circle with authentic Angry Birds round shape)
        pygame.draw.circle(surface, bird_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)  # Outline

        # Draw eyes - authentic Angry Birds style
        eye_offset = self.radius * 0.35
        eye_size = self.radius * 0.18

        # Left eye
        left_eye_x = int(self.x - eye_offset)
        left_eye_y = int(self.y - self.radius * 0.15)
        pygame.draw.circle(surface, WHITE, (left_eye_x, left_eye_y), eye_size)
        pygame.draw.circle(surface, BLACK, (left_eye_x, left_eye_y), int(eye_size * 0.6))
        # Pupil direction based on velocity
        if self.velocity[0] != 0:
            pupil_offset = int(self.velocity[0] * 0.15)
            pygame.draw.circle(surface, BLACK, (left_eye_x + pupil_offset, left_eye_y), int(eye_size * 0.4))
        else:
            pygame.draw.circle(surface, BLACK, (left_eye_x, left_eye_y), int(eye_size * 0.4))

        # Right eye
        right_eye_x = int(self.x + eye_offset)
        right_eye_y = int(self.y - self.radius * 0.15)
        pygame.draw.circle(surface, WHITE, (right_eye_x, right_eye_y), eye_size)
        pygame.draw.circle(surface, BLACK, (right_eye_x, right_eye_y), int(eye_size * 0.6))
        if self.velocity[0] != 0:
            pupil_offset = int(self.velocity[0] * 0.15)
            pygame.draw.circle(surface, BLACK, (right_eye_x + pupil_offset, right_eye_y), int(eye_size * 0.4))
        else:
            pygame.draw.circle(surface, BLACK, (right_eye_x, right_eye_y), int(eye_size * 0.4))

        # Beak (only for red bird)
        if self.type_name == "red":
            beak_size = self.radius * 0.25
            beak_x = int(self.x + self.radius * 0.5)
            beak_y = int(self.y + self.radius * 0.1)
            pygame.draw.polygon(surface, beak_color, [
                (beak_x, beak_y),
                (beak_x - beak_size, beak_y + beak_size * 2),
                (beak_x + beak_size, beak_y + beak_size * 2)
            ])

        # Speed lines when moving fast
        speed = math.hypot(self.velocity[0], self.velocity[1])
        if speed > 5 and self.launched and not self.caught:
            num_lines = int(min(speed / 3, 5))
            for i in range(num_lines):
                offset = i * 3
                angle = math.atan2(self.velocity[1], self.velocity[0])
                line_end_x = int(self.x + math.cos(angle) * (self.radius + offset))
                line_end_y = int(self.y + math.sin(angle) * (self.radius + offset))
                pygame.draw.line(surface, ORANGE,
                                 (int(self.x), int(self.y)),
                                 (line_end_line_x, line_end_y), 2)

    @property
    def score(self):
        """Get score contribution - stored in parent scope."""
        return 0


@dataclass
class Brick:
    x: float
    y: float
    width: int
    height: int
    health: int  # 1=normal, 2=strong, 3=indestructible
    brick_type: str  # "wood", "stone", "ice"
    color: tuple

    def __post_init__(self):
        # Set default colors based on type if not specified
        if self.color == (0, 0, 0):
            self.color = self._get_default_color()

    def _get_default_color(self) -> tuple:
        """Get default color based on brick type."""
        if self.brick_type == "wood":
            return BROWN
        elif self.brick_type == "stone":
            return GRAY
        elif self.brick_type == "ice":
            return (173, 216, 230)  # Light blue
        return GRAY

    def hit(self) -> Optional[int]:
        """Reduce health and return points if destroyed. Returns points or None."""
        self.health -= 1
        if self.health <= 0:
            # Return points based on type
            if self.brick_type == "wood":
                return 10
            elif self.brick_type == "stone":
                return 30
            elif self.brick_type == "ice":
                return 20
            return 10
        return None


class Structure:
    def __init__(self, bricks: List[Brick]):
        self.bricks = bricks

    def draw(self, surface: pygame.Surface):
        """Draw all bricks in the structure."""
        for brick in self.bricks:
            # Draw brick with slight drop shadow
            pygame.draw.rect(surface, brick.color, (brick.x + 2, brick.y + 2,
                                                      brick.width, brick.height))
            pygame.draw.rect(surface, BLACK, (brick.x, brick.y,
                                               brick.width, brick.height), 2)
            # Draw cracks if damaged
            if brick.health < 3:
                # Small crack lines
                crack_color = (255, 255, 255) if brick.health >= 1 else BLACK
                crack_width = max(1, 3 - brick.health)
                # Horizontal crack
                if brick.health <= 1:
                    pygame.draw.line(surface, crack_color,
                                     (brick.x + 5, brick.y + brick.height - 5),
                                     (brick.x + brick.width - 5, brick.y + brick.height - 5),
                                     crack_width)
                # Vertical crack
                if brick.health <= 1:
                    pygame.draw.line(surface, crack_color,
                                     (brick.x + brick.width - 5, brick.y + 5),
                                     (brick.x + brick.width - 5, brick.y + brick.height - 5),
                                     crack_width)

    def hit(self, pos: tuple) -> tuple[bool, int]:
        """Check if position hits a brick. Returns (hit, points)."""
        for brick in self.bricks:
            if (brick.x < pos[0] < brick.x + brick.width and
                    brick.y < pos[1] < brick.y + brick.height):
                points = brick.hit()
                return True, points if points is not None else 0
        return False, 0


def create_level1_structure() -> Structure:
    """Create Level 1 structure - classic Angry Birds setup."""
    bricks = []

    # Row 1: Wood boxes (bottom) - strong
    for i in range(8):
        bricks.append(Brick(
            x=350 + i * 60, y=HEIGHT - 150, width=50, height=30,
            health=2, brick_type="wood", color=BROWN
        ))

    # Row 2: Stone bricks (middle) - offset
    for i in range(5):
        bricks.append(Brick(
            x=380 + i * 60, y=HEIGHT - 220, width=50, height=30,
            health=1, brick_type="stone", color=GRAY
        ))

    # Row 3: Ice blocks (top) - breakable
    for i in range(3):
        bricks.append(Brick(
            x=400 + i * 60, y=HEIGHT - 290, width=50, height=30,
            health=1, brick_type="ice", color=(173, 216, 230)
        ))

    return Structure(bricks)


def draw_sky(surface: pygame.Surface):
    """Draw authentic Angry Birds sky with gradient."""
    # Fill background
    surface.fill(SKY_BLUE)

    # Draw clouds
    cloud_colors = [(255, 255, 255), (220, 220, 220), (240, 240, 245)]
    for i in range(5):
        cloud_x = 100 + i * 180 + random.randint(-20, 20)
        cloud_y = 80 + random.randint(-10, 10)
        cloud_size = random.randint(30, 60)
        # Cloud body
        pygame.draw.ellipse(surface, random.choice(cloud_colors),
                            (cloud_x, cloud_y, cloud_size, cloud_size // 2))
        # Cloud details
        pygame.draw.ellipse(surface, (230, 230, 230),
                            (cloud_x + 10, cloud_y + 10, cloud_size // 3, cloud_size // 4))
        pygame.draw.ellipse(surface, (230, 230, 230),
                            (cloud_x + 25, cloud_y + 15, cloud_size // 4, cloud_size // 3))


def draw_ground(surface: pygame.Surface):
    """Draw authentic Angry Birds ground."""
    # Ground line
    pygame.draw.line(surface, (60, 140, 60), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 6)

    # Grass area
    pygame.draw.polygon(surface, (34, 139, 34), [
        (0, HEIGHT - 50),
        (WIDTH // 2 - 100, HEIGHT - 100),
        (WIDTH // 2 + 100, HEIGHT - 100),
        (WIDTH, HEIGHT - 50)])

    # Grass blades
    for i in range(0, WIDTH, 50):
        pygame.draw.polygon(surface, (124, 252, 124), [
            (i, HEIGHT - 50),
            (i + 25, HEIGHT - 70),
            (i + 50, HEIGHT - 50),
            (i + 25, HEIGHT - 55)])

    # Dirt mounds
    for i in range(0, WIDTH, 150):
        pygame.draw.circle(surface, (82, 56, 32), (i + 75, HEIGHT - 30), 30)
        pygame.draw.circle(surface, (82, 56, 32), (i + 175, HEIGHT - 45), 25)


def draw_power_bar(surface: pygame.Surface, angle: float, power: float, max_power: float = MAX_POWER):
    """Draw angle and power indicators."""
    # Angle display
    angle_text = FONT.render(f"Angle: {int(angle)}°", True, WHITE)
    surface.blit(angle_text, (20, 20))

    # Power bar background
    pygame.draw.rect(surface, DARK_GRAY, (20, 50, 200, 25))

    # Power bar fill
    bar_width = int((power / max_power) * 200)
    pygame.draw.rect(surface, ORANGE, (20, 50, bar_width, 25))

    # Power text
    power_text = FONT.render(f"Power: {int(power)}/{int(max_power)}", True, BLACK)
    surface.blit(power_text, (20, 75))

    # Angle indicator arc
    center = (200, 100)
    radius = 30
    pygame.draw.circle(surface, (255, 255, 255, 50), center, radius, 1)
    # Draw angle arc
    start_angle = math.radians(angle - 90)
    end_angle = math.radians(angle - 90)  # Would need dynamic calculation
    # Just draw a simple indicator
    indicator_x = int(200 + radius * math.cos(start_angle))
    indicator_y = int(100 + radius * math.sin(start_angle))
    pygame.draw.line(surface, ORANGE, center, (indicator_x, indicator_y), 3)


def main():
    """Main game loop."""
    running = True
    game_over = False
    level_complete = False
    level = 1
    score = 0

    # Create birds - authentic Angry Birds types
    birds = [
        Bird(x=150, y=HEIGHT - 100, radius=20, color=RED, type_name="red"),
        Bird(x=150, y=HEIGHT - 130, radius=20, color=BLUE_BIRD, type_name="blue"),
        Bird(x=150, y=HEIGHT - 160, radius=20, color=YELLOW_BIRD, type_name="yellow"),
    ]

    current_bird_index = 0
    current_bird = birds[current_bird_index]

    # Create structure
    structure = create_level1_structure()

    # Physics state
    pulling = False
    start_pos = (0, 0)
    angle = 0
    power = 0
    max_power = MAX_POWER

    # Game state
    birds_used = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    # Reset game
                    level = 1
                    score = 0
                    birds = [
                        Bird(x=150, y=HEIGHT - 100, radius=20, color=RED, type_name="red"),
                        Bird(x=150, y=HEIGHT - 130, radius=20, color=BLUE_BIRD, type_name="blue"),
                        Bird(x=150, y=HEIGHT - 160, radius=20, color=YELLOW_BIRD, type_name="yellow"),
                    ]
                    current_bird_index = 0
                    current_bird = birds[current_bird_index]
                    structure = create_level1_structure()
                    angle = 0
                    power = 0
                    pulling = False
                    game_over = False
                    level_complete = False
                    birds_used = 0

                # Blue bird special ability: split into 3
                if event.key == pygame.K_c and current_bird and current_bird.launched:
                    if current_bird.type_name == "blue" and not current_bird.caught:
                        current_bird.caught = True
                        # Split into 3 birds at 30 degree offsets
                        base_angle = math.degrees(math.atan2(
                            -current_bird.velocity[1], current_bird.velocity[0]))
                        for i in range(3):
                            offset = i * 30 - 30  # -30, 0, +30 degrees
                            new_angle = base_angle + offset
                            vel_power = 6
                            rad = math.radians(new_angle)
                            vx = vel_power * math.cos(rad)
                            vy = -vel_power * math.sin(rad)
                            new_bird = Bird(
                                x=current_bird.x,
                                y=current_bird.y,
                                radius=15,
                                color=BLUE_BIRD,
                                type_name="blue",
                                velocity=[vx, vy],
                                launched=True
                            )
                            birds.append(new_bird)

                # Yellow bird speed boost
                if event.key == pygame.K_f and current_bird and current_bird.launched:
                    if current_bird.type_name == "yellow" and not current_bird.caught:
                        current_bird.caught = True
                        # Triple speed for a short duration
                        current_bird.velocity[0] *= 2.5
                        current_bird.velocity[1] *= 2.5

            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_bird and not current_bird.launched and not game_over and not level_complete:
                    pulling = True
                    start_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if pulling and current_bird and not current_bird.launched:
                    end_pos = pygame.mouse.get_pos()
                    dx = end_pos[0] - start_pos[0]
                    dy = start_pos[1] - end_pos[1]  # Inverted Y
                    angle = math.degrees(math.atan2(dy, dx))
                    power = min(math.hypot(dx, dy) / 20, max_power)
                    current_bird.launch(angle, power)
                    pulling = False
                    birds_used += 1
                    # Switch to next bird
                    current_bird_index += 1
                    if current_bird_index < len(birds):
                        current_bird = birds[current_bird_index]
                    else:
                        current_bird = None  # All birds used

        # Update birds physics
        for bird in birds:
            if bird.launched and not bird.caught:
                bird.update(structure)

        # Check level complete
        if len(structure.bricks) == 0:
            level_complete = True
            score += 100 * level

        # Game over condition
        active_birds = [b for b in birds if b.launched and not b.caught and not b.is_off_screen()]
        birds_not_yet_launched = [b for b in birds if not b.launched]
        if (len(birds_not_yet_launched) == 0 and len(active_birds) == 0 and
                not level_complete and not game_over):
            game_over = True

        # Drawing
        draw_sky(screen)
        draw_ground(screen)
        structure.draw(screen)

        # Draw birds
        for bird in birds:
            bird.draw(screen)

        # Draw trajectory when dragging
        if current_bird and not current_bird.launched and not game_over and not level_complete:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - current_bird.x
            dy = current_bird.y - mouse_pos[1]  # Inverted Y
            angle = math.degrees(math.atan2(dy, dx))
            power = min(math.hypot(dx, dy) / 20, max_power)

            # Draw trajectory preview
            if power > 3:
                temp_vel = [power * math.cos(math.radians(angle)),
                            -power * math.sin(math.radians(angle))]
                traj_points = [(current_bird.x, current_bird.y)]
                bx, by = current_bird.x, current_bird.y
                grav = GRAVITY
                for i in range(25):
                    bx += temp_vel[0] * 3
                    by += temp_vel[1] * 3 + 0.5 * grav * (i + 1)
                    if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
                        traj_points.append((bx, by))
                    else:
                        break

                # Draw trajectory as fading lines
                for i in range(len(traj_points) - 1):
                    alpha = int(200 * (1 - i / len(traj_points)))
                    color = (255, 165, 0, alpha) if hasattr(pygame, 'gfxdraw') else ORANGE
                    width = max(1, int(4 * (1 - i / len(traj_points))))
                    pygame.draw.line(screen, color,
                                     (int(traj_points[i][0]), int(traj_points[i][1])),
                                     (int(traj_points[i+1][0]), int(traj_points[i+1][1])), width)

            draw_power_bar(screen, angle, power, max_power)

            # Instruction text
            if not pulling:
                instruct_text = FONT.render("Drag the bird to launch", True, WHITE)
                screen.blit(instruct_text, (WIDTH // 2 - 120, HEIGHT - 40))

        # Draw UI panel
        # Panel background
        panel_width, panel_height = 200, 180
        panel_x, panel_y = WIDTH - panel_width - 20, 20
        pygame.draw.rect(screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3)

        # Score
        score_text = BIG_FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (panel_x + 10, panel_y + 10))

        # Level
        level_text = FONT.render(f"Level: {level}", True, BLACK)
        screen.blit(level_text, (panel_x + 10, panel_y + 45))

        # Birds remaining
        birds_left = len([b for b in birds if not b.launched or b.caught]) + len(
            [b for b in birds if b.launched and not b.caught])
        birds_text = FONT.render(f"Birds: {birds_used + 1}/{len(birds)}", True, BLACK)
        screen.blit(birds_text, (panel_x + 10, panel_y + 80))

        # Title
        title_text = FONT.render("Angry Birds", True, RED)
        screen.blit(title_text, (panel_x + 50, panel_y + 130))

        # Game over / level complete messages
        if game_over and not level_complete:
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
            overlay.fill((178, 34, 34))  # Red overlay
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            lc_text = BIG_FONT.render("LEVEL COMPLETE!", True, WHITE)
            bonus_text = FONT.render(f"Bonus: +{100 * level} points!", True, YELLOW_ACCENT)
            restart_text = FONT.render("Press R to continue or Q to quit", True, WHITE)
            screen.blit(lc_text, (WIDTH // 2 - lc_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(bonus_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
            screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 40))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
