import pygame
import random

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    QUIT
)

# define colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# initialize pygame
pygame.init()

# set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Avoid the Obstacles")

# load game sprites and sounds
player_image = pygame.image.load("player.png").convert_alpha()
coin_image = pygame.image.load("coin.png").convert_alpha()
obstacle_image = pygame.image.load("obstacle.png").convert_alpha()
background_image = pygame.image.load("background.png").convert()
game_over_sound = pygame.mixer.Sound("game_over.wav")


# define the player sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(screen_width / 2, screen_height / 2))
        self.hp = 3
        self.damage_delay = 0
        self.score = 0
        self.speed = 5
        self.invincibility_counter = 180

    def update(self):
        if self.damage_delay > 0:
            self.damage_delay -= 1

        if self.invincibility_counter > 0:
            self.invincibility_counter -= 1

    def take_damage(self):
        if self.damage_delay == 0 and self.invincibility_counter == 0:
            self.hp -= 1
            self.damage_delay = 30  # delay before taking damage again
            self.invincibility_counter = 180  # reset invincibility period

    def flash(self):
        if self.damage_delay > 0 and self.invincibility_counter % 10 < 5:
            self.image.set_alpha(0)  # make player sprite transparent
        else:
            self.image.set_alpha(255)  # make player sprite opaque

    def move(self, dx, dy):
        # adjust player movement speed
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        # keep the player within the screen boundaries
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, screen_height)


# define the obstacle sprite
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        if self.rect.top < 0 or self.rect.bottom > screen_height:
            self.speed_y *= -1

        # randomly change direction of movement
        if random.random() < 0.01:
            self.speed_x = random.uniform(-2, 2)
            self.speed_y = random.uniform(-2, 2)


# define the coin sprite
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect(center=(x, y))
        self.teleport_chance = 0.1

    def update(self):
        # rotate the coin sprite
        self.image = pygame.transform.rotate(self.image, 5)

    def teleport(self):
        if random.random() < self.teleport_chance:
            self.rect.x = random.randrange(screen_width)
            self.rect.y = random.randrange(screen_height)


# create player sprite
player = Player()

# create sprite groups for coins and obstacles
coins = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# set up the game clock
clock = pygame.time.Clock()

# spawn initial coins
for _ in range(10):
    x = random.randrange(screen_width)
    y = random.randrange(screen_height)
    coin = Coin(x, y)
    coins.add(coin)

# spawn initial obstacles
for _ in range(10):
    x = random.randrange(screen_width)
    y = random.randrange(screen_height)
    speed_x = random.uniform(-3, 3)
    speed_y = random.uniform(-3, 3)
    obstacle = Obstacle(x, y, speed_x, speed_y)
    obstacles.add(obstacle)

# game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player_movement = keys[K_RIGHT] - keys[K_LEFT], keys[K_DOWN] - keys[K_UP]
    player.move(*player_movement)
    player.update()

    # check for collisions between player and coins
    coins_collected = pygame.sprite.spritecollide(player, coins, False)
    for coin in coins_collected:
        if random.random() < 0.5:
            coin.kill()
        else:
            coin.teleport()

    player.score += len(coins_collected)

    # check for collisions between player and obstacles
    if pygame.sprite.spritecollide(player, obstacles, False) and player.invincibility_counter == 0:
        player.take_damage()

    # spawn additional coins
    if len(coins) < 10 and random.random() < 0.015:  # 1% chance of spawning a new coin
        x = random.randrange(screen_width)
        y = random.randrange(screen_height)
        coin = Coin(x, y)
        coins.add(coin)

    obstacles.update()

    # draw background
    screen.blit(background_image, (0, 0))

    # draw sprites
    coins.draw(screen)
    obstacles.draw(screen)
    player.flash()
    screen.blit(player.image, player.rect)

    # render player HP and score text
    font_large = pygame.font.Font(None, 36)
    hp_text = font_large.render("HP: " + str(player.hp), True, YELLOW)
    score_text = font_large.render("Score: " + str(player.score), True, YELLOW)
    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, (10, 60))

    # check if player is defeated
    if player.hp <= 0:
        game_over_sound.play()
        game_over_text = font_large.render("Game Over", True, RED)
        screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2, screen_height / 2))
        pygame.display.flip()
        pygame.time.delay(2000)  # delay for 2 seconds
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
