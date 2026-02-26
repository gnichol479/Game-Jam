import pygame
from settings import *

class UpgradeMenu:

    def __init__(self, player):
        self.player = player
        self.active = False
        self.font = pygame.font.SysFont("Futura", 30)
        self.big_font = pygame.font.SysFont("Futura", 50)

        self.double_jump_unlocked = False
        self.double_shot_unlocked = False

    def toggle(self):
        self.active = not self.active

    def update(self, events):
        if not self.active:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1 and not self.double_jump_unlocked:
                    self.player.max_jumps = 2
                    self.double_jump_unlocked = True

                if event.key == pygame.K_2 and not self.double_shot_unlocked:
                    self.player.double_shot = True
                    self.double_shot_unlocked = True

                if event.key == pygame.K_3:
                    self.player.health = self.player.max_health

    def draw(self, screen):

        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = self.big_font.render("UPGRADE MENU", True, WHITE)
        screen.blit(title, (WIDTH // 2 - 180, 120))

        dj_text = "1 - Double Jump"
        if self.double_jump_unlocked:
            dj_text += " (UNLOCKED)"

        ds_text = "2 - Double Shot"
        if self.double_shot_unlocked:
            ds_text += " (UNLOCKED)"

        rh_text = "3 - Restore Health"

        screen.blit(self.font.render(dj_text, True, WHITE), (WIDTH // 2 - 160, 220))
        screen.blit(self.font.render(ds_text, True, WHITE), (WIDTH // 2 - 160, 270))
        screen.blit(self.font.render(rh_text, True, WHITE), (WIDTH // 2 - 160, 320))
        screen.blit(self.font.render("ESC - Resume", True, WHITE), (WIDTH // 2 - 160, 380))