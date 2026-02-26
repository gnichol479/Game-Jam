import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.animations = {}
        self.load_animations()

        self.action = "Idle"
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.flip = False
        self.vel_y = 0
        self.jumped = False
        self.in_air = True

        self.speed = PLAYER_SPEED
        self.direction = 1

        self.shoot_cooldown = 0
        self.alive = True

    def load_animations(self):
        animation_types = ["Idle", "Run", "Jump", "Death"]

        for animation in animation_types:
            temp_list = []
            path = f"Assets/img/player/{animation}"
            frames = len(os.listdir(path))

            for i in range(frames):
                img = pygame.image.load(f"{path}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * 1.5),
                                                   int(img.get_height() * 1.5)))
                temp_list.append(img)

            self.animations[animation] = temp_list

    def update(self):
        self.update_animation()
        self.check_alive()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self):
        dx = 0
        dy = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if keys[pygame.K_d]:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if keys[pygame.K_w] and not self.jumped and not self.in_air:
            self.vel_y = -15
            self.jumped = True

        if not keys[pygame.K_w]:
            self.jumped = False

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Ground collision (temporary flat ground)
        if self.rect.bottom + dy > HEIGHT - 50:
            dy = HEIGHT - 50 - self.rect.bottom
            self.in_air = False
        else:
            self.in_air = True

        self.rect.x += dx
        self.rect.y += dy

        # Animation switching
        if not self.alive:
            self.update_action("Death")
        elif self.in_air:
            self.update_action("Jump")
        elif dx != 0:
            self.update_action("Run")
        else:
            self.update_action("Idle")

    def shoot(self, bullet_group, bullet_class):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            bullet = bullet_class(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction),
                                  self.rect.centery,
                                  self.direction)
            bullet_group.add(bullet)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animations[self.action][self.frame_index]

        if pygame.time.get_ticks() % ANIMATION_COOLDOWN == 0:
            self.frame_index += 1

        if self.frame_index >= len(self.animations[self.action]):
            if self.action == "Death":
                self.frame_index = len(self.animations[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0

    def check_alive(self):
        if not self.alive:
            self.speed = 0