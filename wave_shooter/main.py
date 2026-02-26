import pygame
import sys
from settings import *
from player import Player

pygame.init()
pygame.mixer.init()

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Shooter")
clock = pygame.time.Clock()

# Load background (temporary solid color if needed)
bg_color = (30, 30, 30)

# Load music
try:
    pygame.mixer.music.load("Assets/audio/music2.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0, 5000)
except Exception as e:
    print(f"Could not load music: {e}")

# Load sounds
try:
    shot_sound = pygame.mixer.Sound("Assets/audio/shot.wav")
    jump_sound = pygame.mixer.Sound("Assets/audio/jump.wav")
    grenade_sound = pygame.mixer.Sound("Assets/audio/grenade.wav")
except Exception as e:
    print(f"Could not load sounds: {e}")
    shot_sound = jump_sound = grenade_sound = None

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

# Create player
player = Player(200, HEIGHT - 100)
player_group.add(player)

# Temporary font
font = pygame.font.SysFont("Futura", 30)

def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(bg_color)
    pygame.draw.line(screen, WHITE, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50))

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_state == MENU:
        draw_bg()
        draw_text("Wave Shooter", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Press SPACE to Start", WIDTH // 2 - 140, HEIGHT // 2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING

    elif game_state == PLAYING:
        draw_bg()
        
        # UPDATE SPRITES
        player.move()
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
        draw_bg()
        draw_text("Game Over", WIDTH // 2 - 80, HEIGHT // 2)
        draw_text("Press R to Restart", WIDTH // 2 - 120, HEIGHT // 2 + 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = PLAYING

    pygame.display.update()

pygame.quit()
sys.exit()
