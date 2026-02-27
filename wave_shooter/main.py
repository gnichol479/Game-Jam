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

kills = 0

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))

# Load level variables
current_level = 1
MAX_LEVELS = 3
world_data = []

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
STORE = 4
LEVEL_COMPLETE = 5
GAME_BEATEN = 6
game_state = MENU

def reset_level(advance_level=False):
    global scroll, screen_scroll, kills, player, world, obstacle_list, spawn_timer, current_level, world_data, level
    
    old_extra_jumps = 0
    old_regen_level = 0
    old_extra_bullets = 0
    old_shields = 0
    old_max_shields = 0
    
    if advance_level:
        current_level += 1
        if 'player' in globals():
            old_extra_jumps = player.extra_jumps
            old_regen_level = player.regen_level
            old_extra_bullets = player.extra_bullets
            old_shields = player.shields
            old_max_shields = player.max_shields
    else:
        kills = 0
        
    scroll = 0
    screen_scroll = 0
    spawn_timer = 0
    player_group.empty()
    enemy_group.empty()
    bullet_group.empty()
    enemy_bullet_group.empty()
    
    # Reload world_data based on current_level
    world_data = []
    for row in range(16):
        r = [-1] * 150
        world_data.append(r)

    csv_path = f"Assets/level{current_level}_data.csv"
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
                    
    # Initialize world using the new data
    level = Level()
    world = World()
    obstacle_list = world.process_data(world_data, level.tiles)

    # Respawn based on world_data
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile == 15: # Player
                player = Player(x * TILE_SIZE, y * TILE_SIZE)
                player_group.add(player)
            elif tile == 16: # Enemy
                enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, level=current_level)
                enemy_group.add(enemy)
                
    if 'player' not in globals() or len(player_group) == 0:
        player = Player(200, HEIGHT - 100)
        player_group.add(player)

    if advance_level:
        player.extra_jumps = old_extra_jumps
        player.regen_level = old_regen_level
        player.extra_bullets = old_extra_bullets
        player.shields = old_shields
        player.max_shields = old_max_shields

# Initial setup call
level = Level()
reset_level()

spawn_timer = 0
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
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSED
                elif game_state == PAUSED:
                    game_state = PLAYING
                    
            if event.key == pygame.K_q and game_state in [PLAYING, PAUSED, STORE] and player.alive:
                player.health = 0
                player.check_alive()
                game_state = GAME_OVER
                    
            if event.key == pygame.K_TAB and game_state in [PLAYING, STORE] and player.alive:
                game_state = STORE if game_state == PLAYING else PLAYING
                
            if game_state == STORE:
                if event.key == pygame.K_1 and kills >= 5:
                    kills -= 5
                    player.extra_jumps += 1
                if event.key == pygame.K_2 and kills >= 10:
                    kills -= 10
                    player.regen_level += 1
                if event.key == pygame.K_3 and kills >= 15:
                    kills -= 15
                    player.extra_bullets += 1
                if event.key == pygame.K_4 and kills >= 20:
                    kills -= 20
                    player.max_shields += 1
                    player.shields += 1

    if game_state == MENU:
        draw_bg()
        draw_text("Wave Shooter", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Press SPACE to Start", WIDTH // 2 - 140, HEIGHT // 2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING

    elif game_state in [PLAYING, PAUSED, STORE]:
        draw_bg()
        
        # Draw world tiles
        world.draw(screen, screen_scroll)

        if game_state == PLAYING:
            # Dynamic Spawning
            spawn_timer += 1
            if spawn_timer >= 360: # Spawn every 6 seconds
                spawn_timer = 0
                import random
                spawn_x = random.randint(WIDTH + 50, WIDTH + 200)
                new_enemy = Enemy(spawn_x, -50, level=current_level)
                enemy_group.add(new_enemy)

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
                hit_list = pygame.sprite.spritecollide(enemy, bullet_group, True)
                for bullet in hit_list:
                    if enemy.alive:
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemy.alive = False
                            enemy.update_action("Death")
                            if shot_sound:
                                shot_sound.play()
                            kills += 1
                            break
            # Check for collisions between enemy bullets and player
            if pygame.sprite.spritecollide(player, enemy_bullet_group, True):
                if player.alive:
                    if player.shields > 0:
                        player.shields -= 1
                    else:
                        player.health -= 1
                    if shot_sound: # This sound is typically for shooting, but included in the instruction.
                        shot_sound.play()
                    player.check_alive() # Ensure player's alive status is updated
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

            # Handle falling off the map
            if not player.alive:
                game_state = GAME_OVER

            # Handle reaching the end of the level
            level_length_pixels = len(world_data[0]) * TILE_SIZE
            if abs(scroll) + player.rect.x > level_length_pixels - 120:
                game_state = LEVEL_COMPLETE

        # Draw sprites (happens in both PLAYING and PAUSED)
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)
        enemy_bullet_group.draw(screen)

        # Draw UI
        draw_text(f"Kills: {kills}", 10, 10)
        draw_text("Press Q to Give Up", 10, 115)
        for i in range(player.health):
            screen.blit(heart_img, (10 + (i * 35), 45))
        for i in range(player.shields):
            pygame.draw.rect(screen, (0, 100, 255), (10 + (i * 35), 45 + 35, 25, 25))

        if game_state == PAUSED:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            draw_text("PAUSED", WIDTH // 2 - 50, HEIGHT // 2 - 20)

        elif game_state == STORE:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            draw_text("UPGRADE STORE (Press TAB to Close)", WIDTH // 2 - 200, 50)
            draw_text(f"Available Kills: {kills}", WIDTH // 2 - 100, 100)
            
            color1 = (0, 255, 0) if kills >= 5 else (150, 150, 150)
            text1 = "1. Extra Jumps (Cost: 5 Kills)" + (f" [Level {player.extra_jumps}]" if player.extra_jumps > 0 else "")
            img1 = font.render(text1, True, color1)
            screen.blit(img1, (WIDTH // 2 - 200, 200))

            color2 = (0, 255, 0) if kills >= 10 else (150, 150, 150)
            text2 = "2. Faster Regen (Cost: 10 Kills)" + (f" [Level {player.regen_level}]" if player.regen_level > 0 else "")
            img2 = font.render(text2, True, color2)
            screen.blit(img2, (WIDTH // 2 - 200, 260))

            color3 = (0, 255, 0) if kills >= 15 else (150, 150, 150)
            text3 = "3. Extra Bullets (Cost: 15 Kills)" + (f" [Level {player.extra_bullets}]" if player.extra_bullets > 0 else "")
            img3 = font.render(text3, True, color3)
            screen.blit(img3, (WIDTH // 2 - 200, 320))

            color4 = (0, 255, 0) if kills >= 20 else (150, 150, 150)
            text4 = "4. Max Shield (Cost: 20 Kills)" + (f" [Level {player.max_shields}]" if player.max_shields > 0 else "")
            img4 = font.render(text4, True, color4)
            screen.blit(img4, (WIDTH // 2 - 200, 380))

    elif game_state == GAME_OVER:
        draw_bg()
        draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(f"Final Kills: {kills}", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Press R to Respawn", WIDTH // 2 - 140, HEIGHT // 2 + 50)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_level()
            game_state = PLAYING

    elif game_state == LEVEL_COMPLETE:
        draw_bg()
        draw_text(f"LEVEL {current_level} CLEARED!", WIDTH // 2 - 120, HEIGHT // 2 - 50)
        draw_text(f"Kills: {kills}", WIDTH // 2 - 100, HEIGHT // 2)
        
        if current_level < MAX_LEVELS:
            draw_text("Press N to Start Next Level", WIDTH // 2 - 160, HEIGHT // 2 + 50)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_n]:
                reset_level(advance_level=True)
                game_state = PLAYING
        else:
            game_state = GAME_BEATEN

    elif game_state == GAME_BEATEN:
        draw_bg()
        draw_text("YOU BEAT THE GAME!", WIDTH // 2 - 140, HEIGHT // 2 - 50)
        draw_text(f"Total Kills: {kills}", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("Press R to Restart Game", WIDTH // 2 - 160, HEIGHT // 2 + 50)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            kills = 0
            current_level = 1
            reset_level()
            game_state = PLAYING

    pygame.display.update()

pygame.quit()
sys.exit()
