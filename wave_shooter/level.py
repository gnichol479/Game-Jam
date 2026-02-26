import pygame
import csv
import os
from settings import *

class Level:
    def __init__(self):
        self.tile_list = []
        self.load_images()

    def load_images(self):
        self.tiles = {}
        path = "Assets/img/tile"
        for i in range(21): # Tiles 0 to 20
            img_path = f"{path}/{i}.png"
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.tiles[i] = img

    def load_data(self, data_path):
        self.tile_list = []
        with open(data_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    tile_id = int(tile)
                    if tile_id >= 0:
                        img = self.tiles.get(tile_id)
                        if img:
                            rect = img.get_rect()
                            rect.x = y * TILE_SIZE
                            rect.y = x * TILE_SIZE
                            self.tile_list.append((img, rect))

    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class World:
    def __init__(self):
        self.obstacle_list = []
        self.decoration_list = []

    def process_data(self, data, tiles):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = tiles.get(tile)
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    
                    # Store tiles in different lists based on their ID
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        pass # water or something
                    elif tile >= 11 and tile <= 14:
                        self.decoration_list.append(tile_data) # decorations or pillars
                    elif tile == 15: # player
                        self.player_spawn = (x * TILE_SIZE, y * TILE_SIZE)
                    elif tile == 16: # enemy
                        self.enemy_spawn = (x * TILE_SIZE, y * TILE_SIZE)
                    elif tile >= 17 and tile <= 19:
                        pass # items
                    elif tile == 20: # exit
                        pass
        return self.obstacle_list

    def draw(self, screen, screen_scroll):
        # Draw decorations first (behind obstacles)
        for tile in self.decoration_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])
        # Draw obstacles
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])
