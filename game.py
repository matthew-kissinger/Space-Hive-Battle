import pygame
import random
import math
from pygame.locals import *

# Constants
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH, WORLD_HEIGHT = 3 * WIDTH, 3 * HEIGHT
PLAYER_SPEED = 5
ALIEN_SPEED = 2
LASER_SPEED = 10
PLAYER_HEALTH = 100
HIVE_HEALTH = 300
BASE_HEALTH = 500
RANGED_HEALTH = 25
MELEE_HEALTH = 50
RANGED_DAMAGE = 5
MELEE_DAMAGE = 10
LASER_DAMAGE = 10
SPAWN_RATE = 5 * 1000
LASER_WIDTH = 5
LASER_HEIGHT = 5
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 25
HIVE_WIDTH = 30
HIVE_HEIGHT = 30
ALIEN_WIDTH = 20
ALIEN_HEIGHT = 20
BASE_WIDTH = 100
BASE_HEIGHT = 100
HEALTH_IMAGE_PATH = 'health.png'
LASER_IMAGE_PATH = 'laser.png'
LASER_POWERUP_IMAGE_PATH = 'laserpowerup.png'
BACKGROUND_IMAGE_PATH = 'background.png'
BASE_HEALTH_IMAGE_PATH = 'basehealth.png'
BASE_IMAGE_PATH = 'base.png'
HEALTH_POWERUP_WIDTH = 50
HEALTH_POWERUP_HEIGHT = 50
LASER_POWERUP_WIDTH = 50
LASER_POWERUP_HEIGHT = 50
BASE_HEALTH_POWERUP_WIDTH = 50
BASE_HEALTH_POWERUP_HEIGHT = 50
BASE_HEALTH_POWERUP_HEAL_AMOUNT = 100


# Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("SpaceHive Battle")


class HealthPowerUp(pygame.sprite.Sprite):
    def __init__(self, healing_target):
        super().__init__()
        self.image = pygame.image.load(HEALTH_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (HEALTH_POWERUP_WIDTH, HEALTH_POWERUP_HEIGHT))
        self.rect = self.image.get_rect(center=(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)))
        self.healing_target = healing_target
        self.heal_amount = 50

class BaseHealthPowerUp(pygame.sprite.Sprite):
    def __init__(self, healing_target):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(BASE_HEALTH_IMAGE_PATH).convert_alpha(), (BASE_HEALTH_POWERUP_WIDTH, BASE_HEALTH_POWERUP_HEIGHT))
        self.rect = self.image.get_rect(center=(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)))
        self.healing_target = healing_target
        self.heal_amount = BASE_HEALTH_POWERUP_HEAL_AMOUNT

class LaserPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(LASER_POWERUP_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (LASER_POWERUP_WIDTH, LASER_POWERUP_HEIGHT))
        self.rect = self.image.get_rect(center=(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)))
        self.duration = 30 * 1000  # 30 seconds in milliseconds
        self.laser_speed = 5


class PlayerSection:
    def __init__(self, center):
        x = max(0, min(WORLD_WIDTH - WIDTH, center[0] - WIDTH // 2))
        y = max(0, min(WORLD_HEIGHT - HEIGHT, center[1] - HEIGHT // 2))
        self.rect = pygame.Rect(x, y, WIDTH, HEIGHT)
    
    def contains(self, rect):
        return self.rect.colliderect(rect)


# Game Objects - Modify the classes to load images for the sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image = pygame.image.load("spaceship.png").convert_alpha()
        self.image = pygame.transform.scale(image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(center=(WIDTH + WIDTH // 2, HEIGHT + HEIGHT // 2))
        self.health = PLAYER_HEALTH

    def update(self, keys):
        old_rect = self.rect.copy()  # Store the previous position of the player

        if keys[K_w] or keys[K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[K_s] or keys[K_DOWN]:
            self.rect.y += PLAYER_SPEED
        if keys[K_a] or keys[K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[K_d] or keys[K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Clamp the player position to the world boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))


class AlienHive(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image = pygame.image.load("hive.png").convert_alpha()
        self.image = pygame.transform.scale(image, (HIVE_WIDTH, HIVE_HEIGHT))
        self.rect = self.image.get_rect(center=(random.randint(0, WORLD_WIDTH - HIVE_WIDTH), random.randint(0, WORLD_HEIGHT - HIVE_HEIGHT)))
        self.health = HIVE_HEALTH
        self.max_health = self.health

    def draw_health_bar(self, screen, screen_section):
        health_ratio = self.health / self.max_health
        bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0)
        bar_width = int(self.rect.width * health_ratio)

        pygame.draw.rect(screen, bar_color, (self.rect.x - screen_section[0], self.rect.y - 10 - screen_section[1], bar_width, 5))



class Alien(pygame.sprite.Sprite):
    def __init__(self, target, alien_type, spawn_position=None):
        super().__init__()
        image = pygame.image.load("alien.png").convert_alpha()
        self.image = pygame.transform.scale(image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.target = target
        self.alien_type = alien_type
        self.health = RANGED_HEALTH if alien_type == "ranged" else MELEE_HEALTH
        self.max_health = self.health
        self.speed = ALIEN_SPEED
        if spawn_position:
            self.rect.center = spawn_position
    def update(self):
        direction = self.target.rect.center - pygame.math.Vector2(self.rect.center)
        self.velocity = direction.normalize() * self.speed
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
    def draw_health_bar(self, screen, screen_section):
        health_ratio = self.health / self.max_health
        bar_color = (255 - int(255 * health_ratio), int(255 * health_ratio), 0)
        bar_width = int(self.rect.width * health_ratio)

        pygame.draw.rect(screen, bar_color, (self.rect.x - screen_section[0], self.rect.y - 10 - screen_section[1], bar_width, 5))
        

class Base(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image = pygame.image.load("base.png").convert_alpha()
        self.image = pygame.transform.scale(image, (BASE_WIDTH, BASE_HEIGHT))
        self.rect = self.image.get_rect(center=(WIDTH + WIDTH // 2, HEIGHT + HEIGHT // 2))
        self.health = BASE_HEALTH

class Laser(pygame.sprite.Sprite):
    def __init__(self, origin, target):
        super().__init__()
        self.image = pygame.Surface((LASER_WIDTH, LASER_HEIGHT))
        self.image.fill((0, 255, 0))  # RGB values for green
        self.rect = self.image.get_rect(center=origin)
        self.speed = LASER_SPEED
        direction = target - pygame.math.Vector2(origin)
        self.velocity = direction.normalize() * self.speed
    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Remove the laser if it goes off the world boundaries
        if not pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT).collidepoint(self.rect.center):
            self.kill()

# Add a new function to start the next level
def start_next_level(level, hives, all_sprites):
    for _ in range(level):
        hive = AlienHive()
        hives.add(hive)
        all_sprites.add(hive)

def draw_health_bar(surface, x, y, pct, width=100, height=10, color=(0, 255, 0), bg_color=(255, 0, 0)):
    filled_width = int(pct * width)
    outline_rect = pygame.Rect(x, y, width, height)
    filled_rect = pygame.Rect(x, y, filled_width, height)
    
    pygame.draw.rect(surface, bg_color, outline_rect)
    pygame.draw.rect(surface, color, filled_rect)
    pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)


def draw_player_health(screen, player):
    x, y = 10, 30  # Adjust the position
    pct = player.health / PLAYER_HEALTH
    draw_health_bar(screen, x, y, pct)

def draw_base_health_bar(screen, base):
    x, y = 10, 70  # Adjust the position
    pct = base.health / BASE_HEALTH
    draw_health_bar(screen, x, y, pct, color=(0, 0, 255))

def draw_level(screen, level):
    font = pygame.font.Font(None, 36)
    text = font.render("Level: {}".format(level), True, (255, 255, 255))
    screen.blit(text, (WIDTH - 150, 20))  # Adjust the position

def draw_health_labels(screen):
    font = pygame.font.Font(None, 24)
    player_health_text = font.render("Ship Health:", True, (255, 255, 255))
    base_health_text = font.render("Base Health:", True, (255, 255, 255))
    screen.blit(player_health_text, (10, 10))  # Adjust the position
    screen.blit(base_health_text, (10, 50))  # Adjust the position

def menu_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render("SpaceHive Battle", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    font = pygame.font.Font(None, 24)
    text = font.render("Press SPACE to start", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False
            if event.type == KEYDOWN and event.key == K_SPACE:
                return True

def level_screen(level):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level {level}", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    font = pygame.font.Font(None, 24)
    text = font.render("Press SPACE to start", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()
    pygame.time.delay(2000)

def lose_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over!", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.flip()
    pygame.time.delay(3000)

def in_same_section(rect1, rect2):
    return (
        rect1.left // WIDTH == rect2.left // WIDTH
        and rect1.top // HEIGHT == rect2.top // HEIGHT
    )

# Add a new function to draw the mini-map
def draw_mini_map(screen, screen_section):
    mini_map_size = 100
    mini_map_rect = pygame.Rect(10, HEIGHT - mini_map_size - 10, mini_map_size, mini_map_size)

    pygame.draw.rect(screen, (128, 128, 128), mini_map_rect)
    section_rect_size = mini_map_size // 3
    player_section_rect = pygame.Rect(
        mini_map_rect.x + (screen_section[0] // WIDTH) * section_rect_size,
        mini_map_rect.y + (screen_section[1] // HEIGHT) * section_rect_size,
        section_rect_size,
        section_rect_size,
    )
    pygame.draw.rect(screen, (255, 255, 0), player_section_rect)


# Game Loop - Modify the game loop to incorporate levels and change alien spawning
def game_loop():
    if not menu_screen():
        return
    
    # Set up the screen and background
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE_PATH).convert_alpha(), (WORLD_WIDTH, WORLD_HEIGHT))



    player = Player()
    player_laser_powerup_active = False
    base = Base()
    hives = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player, base)
    health_powerups = pygame.sprite.Group()
    laser_powerups = pygame.sprite.Group()
    base_health_powerups = pygame.sprite.Group()
    powerup_event = pygame.USEREVENT + 2
    pygame.time.set_timer(powerup_event, 10 * 1000)  # every 10 seconds


    level = 1
    start_next_level(level, hives, all_sprites)
    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, SPAWN_RATE)

    section_x = 0
    section_y = 0
    screen_section = (section_x, section_y)

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, (-section_x, -section_y))

        for entity in all_sprites:
            if in_same_section(entity.rect, player.rect):
                screen.blit(entity.image, (entity.rect.x - screen_section[0], entity.rect.y - screen_section[1]))

        for entity in all_sprites:
            if in_same_section(entity.rect, player.rect) and isinstance(entity, (Alien, AlienHive)):
                entity.draw_health_bar(screen, screen_section)





        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                world_click_pos = pygame.math.Vector2(pygame.mouse.get_pos()) + pygame.math.Vector2(screen_section)
                laser = Laser(player.rect.center, world_click_pos)
                lasers.add(laser)
                all_sprites.add(laser)
            if player_laser_powerup_active:
                current_time = pygame.time.get_ticks()
                if isinstance(powerup, LaserPowerUp) and current_time - player_laser_powerup_start > powerup.duration:
                    player_laser_powerup_active = False
                elif player_laser_powerup_active:
                    # Fire lasers in all directions
                    for angle in range(0, 360, 45):
                        direction = pygame.math.Vector2()
                        direction.from_polar((1, angle))
                        laser = Laser(player.rect.center, pygame.math.Vector2(player.rect.center) + direction * 100)
                        lasers.add(laser)
                        all_sprites.add(laser)

            if event.type == spawn_event:
                for hive in hives:
                    alien_type = random.choice(["ranged", "melee"])
                    alien_target = base if random.random() < 0.5 else player
                    alien = Alien(alien_target, alien_type, spawn_position=hive.rect.center)
                    aliens.add(alien)
                    all_sprites.add(alien)

            if event.type == powerup_event:
                # Add a 50% chance to spawn either a health power-up or a laser power-up
                if random.random() < 0.5:
                    health_powerup = HealthPowerUp("player" if random.random() < 0.5 else "base")
                    health_powerups.add(health_powerup)
                    all_sprites.add(health_powerup)
                else:
                    laser_powerup = LaserPowerUp()
                    laser_powerups.add(laser_powerup)
                    all_sprites.add(laser_powerup)

                # Spawn a base health power-up with a probability of 25%
                if random.random() < 0.25:
                    base_health_powerup = BaseHealthPowerUp("base")
                    base_health_powerups.add(base_health_powerup)
                    all_sprites.add(base_health_powerup)



            health_powerup_collisions = pygame.sprite.spritecollide(player, health_powerups, True)
            for powerup in health_powerup_collisions:
                if powerup.healing_target == "player":
                    player.health = min(PLAYER_HEALTH, player.health + powerup.heal_amount)

            base_health_powerup_collisions = pygame.sprite.spritecollide(player, base_health_powerups, True)
            for powerup in base_health_powerup_collisions:
                if powerup.healing_target == "base":
                    base.health = min(BASE_HEALTH, base.health + powerup.heal_amount)

            laser_powerup_collisions = pygame.sprite.spritecollide(player, laser_powerups, True)
            for powerup in laser_powerup_collisions:
                player_laser_powerup_start = pygame.time.get_ticks()
                player_laser_powerup_active = True


        player.update(keys)

        # Check if the player enters a new section
        if player.rect.x < section_x:
            section_x -= WIDTH
            screen_section = (section_x, section_y)
        elif player.rect.x > section_x + WIDTH:
            section_x += WIDTH
            screen_section = (section_x, section_y)
        elif player.rect.y < section_y:
            section_y -= HEIGHT
            screen_section = (section_x, section_y)
        elif player.rect.y > section_y + HEIGHT:
            section_y += HEIGHT
            screen_section = (section_x, section_y)
        if base.health <= 0 or player.health <= 0:
            lose_screen()
            running = False
            break

        if len(hives) == 0:
            level += 1
            level_screen(level)
            start_next_level(level, hives, all_sprites)




        for alien in aliens:
            alien.update()

        for laser in lasers:
            laser.update()

        collisions = pygame.sprite.groupcollide(aliens, lasers, False, True)
        for alien, hits in collisions.items():
            if alien.health > 0:
                alien.health -= LASER_DAMAGE * len(hits)
                if alien.health <= 0:
                    alien.kill()

        base_collisions = pygame.sprite.spritecollide(base, aliens, False)
        for alien in base_collisions:
            if alien.health > 0:
                if alien.alien_type == "melee":
                    base.health -= MELEE_DAMAGE
                else:
                    base.health -= RANGED_DAMAGE
                alien.kill()

        player_collisions = pygame.sprite.spritecollide(player, aliens, False)
        for alien in player_collisions:
            if alien.health > 0:
                if alien.alien_type == "melee":
                    player.health -= MELEE_DAMAGE
                else:
                    player.health -= RANGED_DAMAGE
                alien.kill()


        hives_collisions = pygame.sprite.groupcollide(hives, lasers, False, True)
        for hive, hits in hives_collisions.items():
            hive.health -= LASER_DAMAGE * len(hits)
            if hive.health <= 0:
                hive.kill()
            else:
                # Check if the hive is in the player's section
                if PlayerSection(pygame.math.Vector2(hive.rect.center)) == PlayerSection(pygame.math.Vector2(player.rect.center)):
                    all_sprites.add(Alien(hive, "melee"))

        # Check if any hives are left, if not, go to the next level
        if not hives:
            level += 1
            start_next_level(level, hives, all_sprites)
            pygame.time.set_timer(spawn_event, SPAWN_RATE // level)

        for hive in hives:
            if in_same_section(hive.rect, player.rect):
                hive.draw_health_bar(screen, screen_section)


        for alien in aliens:
            if in_same_section(alien.rect, player.rect):
                alien.draw_health_bar(screen, screen_section)

        draw_player_health(screen, player)
        draw_base_health_bar(screen, base)
        draw_level(screen, level)
        draw_health_labels(screen)
        draw_mini_map(screen, screen_section)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
if __name__ == "__main__":
    game_loop()
