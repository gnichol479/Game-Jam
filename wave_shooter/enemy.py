import pygame
import os
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level=1):
        super().__init__()

        self.health = level
        self.animations = {}
        self.load_animations()

        self.action = "Idle"
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.flip = False
        self.vel_y = 0
        self.direction = 1
        self.speed = 2
        
        self.shoot_cooldown = 0
        self.alive = True
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.update_time = pygame.time.get_ticks()

    def load_animations(self):
        animation_types = ["Idle", "Run", "Jump", "Death"]

        for animation in animation_types:
            temp_list = []
            path = f"Assets/img/enemy/{animation}"
            if not os.path.exists(path):
                continue
            frames = len(os.listdir(path))

            for i in range(frames):
                img = pygame.image.load(f"{path}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * 1.5),
                                                   int(img.get_height() * 1.5)))
                temp_list.append(img)

            self.animations[animation] = temp_list

    def update(self, screen_scroll, obstacle_list, player, enemy_bullet_group, bullet_class):
        self.update_animation()
        if self.alive:
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            self.move(obstacle_list, player, enemy_bullet_group, bullet_class)
            self.rect.x += screen_scroll
        else:
            self.rect.x += screen_scroll
            if self.frame_index >= len(self.animations["Death"]) - 1:
                self.kill()

    def move(self, obstacle_list, player, enemy_bullet_group, bullet_class):
        dx = 0
        dy = 0

        # Vision check
        vision_rect = pygame.Rect(0, 0, 150, 20)
        vision_rect.center = self.rect.center
        if self.direction == 1:
            vision_rect.left = self.rect.right
        else:
            vision_rect.right = self.rect.left

        if vision_rect.colliderect(player.rect) and player.alive:
            self.idling = True
            self.idling_counter = 20
            # Shoot
            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 240
                bullet = bullet_class(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction),
                                      self.rect.centery,
                                      self.direction)
                enemy_bullet_group.add(bullet)

        if not self.idling:
            dx = self.speed * self.direction
            self.move_counter += 1
            if self.move_counter > TILE_SIZE: # Change direction after moving one tile size
                self.direction *= -1
                self.move_counter *= -1
                self.idling = True
                self.idling_counter = random.randint(30, 90)
        else:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Collision with environment
        # Check for collision in x direction
        self.rect.x += dx
        for tile in obstacle_list:
            if tile[1].colliderect(self.rect):
                if dx > 0:
                    self.rect.right = tile[1].left
                    self.direction = -1
                    self.move_counter = 0
                elif dx < 0:
                    self.rect.left = tile[1].right
                    self.direction = 1
                    self.move_counter = 0
                dx = 0

        # Check for collision in y direction
        self.rect.y += dy
        for tile in obstacle_list:
            if tile[1].colliderect(self.rect):
                # Check if below the ground (jumping)
                if self.vel_y < 0:
                    self.vel_y = 0
                    self.rect.top = tile[1].bottom
                    dy = 0
                # Check if above the ground (falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.rect.bottom = tile[1].top
                    dy = 0

        # Ledge detection (only if on the ground and moving)
        if self.vel_y == 0 and dy == 0 and dx != 0:
            ledge_check_x = self.rect.right + 2 if self.direction == 1 else self.rect.left - 2
            ledge_check_y = self.rect.bottom + 2
            on_ledge = True
            for tile in obstacle_list:
                if tile[1].collidepoint(ledge_check_x, ledge_check_y):
                    on_ledge = False
                    break
            if on_ledge:
                self.direction *= -1
                self.move_counter = 0
                self.rect.x -= dx # undo move

        # Direction flip
        if self.direction == 1:
            self.flip = False
        else:
            self.flip = True

        # Animation switching
        if dx != 0:
            self.update_action("Run")
        else:
            self.update_action("Idle")

    def update_animation(self):
        # Update animation
        ANIMATION_COOLDOWN = 100
        # Update image depending on current frame
        if self.action in self.animations and len(self.animations[self.action]) > 0:
            self.image = self.animations[self.action][self.frame_index]
            if self.flip:
                self.image = pygame.transform.flip(self.image, True, False)

            # Check if enough time has passed since the last update
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1

            # If the animation has run out then reset back to the start
            if self.frame_index >= len(self.animations[self.action]):
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action and new_action in self.animations:
            self.action = new_action
            self.frame_index = 0
