import pygame
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = BULLET_SPEED
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 255, 0)) # Yellow bullet
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, screen_scroll):
        # Move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
