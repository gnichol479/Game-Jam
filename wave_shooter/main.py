import pygame
import sys
import os
import csv
from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from level import Level, World

pygame.init()
pygame.mixer.init()

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Shooter")
clock = pygame.time.Clock()

# Load background images
sky_img = pygame.image.load("Assets/img/background/sky_cloud.png").convert_alpha()
mountain_img = pygame.image.load("Assets/img/background/mountain.png").convert_alpha()
pine1_img = pygame.image.load("Assets/img/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("Assets/img/background/pine2.png").convert_alpha()

# Load UI images
heart_img = pygame.image.load("Assets/img/icons/heart.png").convert_alpha() if os.path.exists("Assets/img/icons/heart.png") else pygame.Surface((30, 30))
if not os.path.exists("Assets/img/icons/heart.png"):
    heart_img.fill((255, 0, 0)) # Red square fallback

# Game variables
bg_color = (144, 201, 120)
TILE_SIZE = 40
screen_scroll = 0
scroll = 0

def draw_bg():
    screen.fill(bg_color)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - scroll * 0.6, HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - scroll * 0.7, HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - scroll * 0.8, HEIGHT - pine2_img.get_height()))

# Load music and sounds
try:
    pygame.mixer.music.load("Assets/audio/music2.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0, 5000)
    shot_sound = pygame.mixer.Sound("Assets/audio/shot.wav")
    jump_sound = pygame.mixer.Sound("Assets/audio/jump.wav")
except Exception as e:
    print(f"Error loading audio: {e}")
    shot_sound = jump_sound = None

# Sprite groups
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

kills = 0

# Load level
world_data = []
for row in range(16):
    r = [-1] * 150
    world_data.append(r)

with open("Assets/level1_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

level = Level()
world = World()
obstacle_list = world.process_data(world_data, level.tiles)

# Spawn objects based on world_data
for y, row in enumerate(world_data):
    for x, tile in enumerate(row):
        if tile == 15: # Player
            player = Player(x * TILE_SIZE, y * TILE_SIZE)
            player_group.add(player)
        elif tile == 16: # Enemy
            enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE)
            enemy_group.add(enemy)

# Fallback if no player spawned
if 'player' not in locals():
    player = Player(200, HEIGHT - 100)
    player_group.add(player)

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

def reset_level():
    global scroll, screen_scroll, kills, player, world, obstacle_list
    scroll = 0
    screen_scroll = 0
    kills = 0
    player_group.empty()
    enemy_group.empty()
    bullet_group.empty()
    enemy_bullet_group.empty()
    
    # Reset world to restore tile positions
    world = World()
    obstacle_list = world.process_data(world_data, level.tiles)

    # Respawn based on world_data
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile == 15: # Player
                player = Player(x * TILE_SIZE, y * TILE_SIZE)
                player_group.add(player)
            elif tile == 16: # Enemy
                enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE)
                enemy_group.add(enemy)
                
    if 'player' not in globals() or len(player_group) == 0:
        player = Player(200, HEIGHT - 100)
        player_group.add(player)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == PLAYING and player.alive:
                player.shoot(bullet_group, Bullet)
                if shot_sound: shot_sound.play()

    if game_state == MENU:
        draw_bg()
        draw_text("Wave Shooter", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Press SPACE to Start", WIDTH // 2 - 140, HEIGHT // 2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING

    elif game_state == PLAYING:
        draw_bg()
        
        # Draw world tiles
        world.draw(screen, screen_scroll)

        # Update sprites
        screen_scroll, jumped = player.move(obstacle_list)
        scroll -= screen_scroll # Total world scroll
        
        if jumped and jump_sound: 
            jump_sound.play()
            
        player_group.update()
        enemy_group.update(screen_scroll, obstacle_list, player, enemy_bullet_group, Bullet)
        bullet_group.update(screen_scroll)
        enemy_bullet_group.update(screen_scroll)
        
        # Check for collisions between bullets and enemies
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, True):
                if enemy.alive:
                    enemy.alive = False
                    enemy.update_action("Death")
                    kills += 1

        # Check for collisions between enemy bullets and player
        if pygame.sprite.spritecollide(player, enemy_bullet_group, True):
            if player.alive:
                player.health -= 1
                player.check_alive()
                if not player.alive:
                    game_state = GAME_OVER

        # Check for collisions between bullets and obstacles
        for bullet in bullet_group:
            for tile in obstacle_list:
                if tile[1].colliderect(bullet.rect):
                    bullet.kill()
                    break
        for bullet in enemy_bullet_group:
            for tile in obstacle_list:
                if tile[1].colliderect(bullet.rect):
                    bullet.kill()
                    break

        # Draw sprites
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)
        enemy_bullet_group.draw(screen)

        # Draw UI
        draw_text(f"Kills: {kills}", 10, 10)
        for i in range(player.health):
            screen.blit(heart_img, (10 + (i * 35), 45))

    elif game_state == GAME_OVER:
        draw_bg()
        draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(f"Final Kills: {kills}", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Press R to Respawn", WIDTH // 2 - 140, HEIGHT // 2 + 50)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_level()
            game_state = PLAYING

    pygame.display.update()

pygame.quit()
sys.exit()
