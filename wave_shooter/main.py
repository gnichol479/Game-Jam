import pygame
import sys
from settings import *

pygame.init()
pygame.mixer.init()

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Shooter")
clock = pygame.time.Clock()

# Load background (temporary solid color if needed)
bg_color = (30, 30, 30)

# Load music
pygame.mixer.music.load("Assets/Audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

# Load sounds
shot_sound = pygame.mixer.Sound("Assets/Audio/shot.wav")
jump_sound = pygame.mixer.Sound("Assets/Audio/jump.wav")
grenade_sound = pygame.mixer.Sound("Assets/Audio/grenade.wav")

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

game_state = MENU

# Sprite groups
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Temporary font
font = pygame.font.SysFont("Futura", 30)

def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(bg_color)

    if game_state == MENU:
        draw_text("Wave Shooter", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Press SPACE to Start", WIDTH // 2 - 140, HEIGHT // 2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING

    elif game_state == PLAYING:
        # UPDATE SPRITES
        player_group.update()
        enemy_group.update()
        bullet_group.update()
        explosion_group.update()

        # DRAW SPRITES
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)
        explosion_group.draw(screen)

    elif game_state == GAME_OVER:
        draw_text("Game Over", WIDTH // 2 - 80, HEIGHT // 2)
        draw_text("Press R to Restart", WIDTH // 2 - 120, HEIGHT // 2 + 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = PLAYING

    pygame.display.update()

pygame.quit()
sys.exit()