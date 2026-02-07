import pygame
import math
import settings
import utilityfuncs
import actors
import geometry
import textures
import raycast
import numpy

EXTREME_RES = 1280 # benchmarking
MAX_RES = 640
DEFAULT_RES = 160
BETTER_RES = 320
MIN_RES = 80


# 16x16 resize
mobster_sprite = textures.mobster_texture

all_sprites:list[actors.WorldSprite] = [
    # actors.WorldSprite(17 * settings.cell_width/2 + random.randrange(-64, 64), 14 * settings.cell_width/2 + random.randrange(-64, 64), 32, 32, mobster_sprite) for i in range(10)
    actors.WorldSprite(8 * settings.cell_width, 3 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(14 * settings.cell_width, 1.5 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(1.5 * settings.cell_width, 1.5 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(12 * settings.cell_width, 11.5 * settings.cell_width, 32, 32, mobster_sprite)
]

# temporary
all_push_walls:list[geometry.PushWall] = [
    # geometry.PushWall(6, 5, map.game_map),
    # geometry.PushWall(i, 7, map.game_map) for i in range(1, 7)
]

lightsource = (8 * settings.cell_width, 3 * settings.cell_width)
light_radius = 192



class Player:
    def __init__(self, x: int, y: int):
        self.x:int = x
        self.y:int = y
        self.resolution = MAX_RES
        self.direction = 0
        self.locked_dir = 0
        self.offset = 0
    
    def movement(self, map:list[list[int]]):
        if pygame.key.get_pressed()[pygame.K_t]:
            for push_wall in all_push_walls:
                push_wall.is_pushed = True
        for wall in all_push_walls:
            wall.update()
        movement_vector = (pygame.key.get_pressed()[pygame.K_w] - pygame.key.get_pressed()[pygame.K_s]) * 2
        front_vec_x = self.x + math.cos(math.radians(self.direction)) * movement_vector * 8
        front_vec_y = self.y - math.sin(math.radians(self.direction)) * movement_vector * 8
        
        conv_x, conv_y = settings.translate_coords((front_vec_x, front_vec_y))
        
        # horizontal
        if map[int(conv_y)][int(self.x/settings.cell_width)] == 0:
            self.y -= math.sin(math.radians(self.direction)) * movement_vector
        if map[int(self.y/settings.cell_width)][int(conv_x)] == 0:
            self.x += math.cos(math.radians(self.direction)) * movement_vector

        rotate_vector = (pygame.key.get_pressed()[pygame.K_a] - pygame.key.get_pressed()[pygame.K_d]) * (0.01 + int(pygame.key.get_pressed()[pygame.K_LSHIFT]) + 1.99)
        self.direction += rotate_vector
        self.direction = utilityfuncs.clamp_directionals(self.direction)

        # how to lock direction into 10 per 1 angle -> 3600 directions you can view

    def rendering(self, dest: pygame.Surface, map:list[list[int]], floor_matrix:numpy.ndarray):
        w, h = dest.get_width(), dest.get_height()

        floor_matrix.fill(0)
        raycast.floorcast(self.x, self.y, self.direction, floor_matrix)
        floor_surf = pygame.surfarray.make_surface(255 * floor_matrix)
        floor_surf = pygame.transform.scale(floor_surf, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        dest.blit(floor_surf, floor_surf.get_rect(topleft=(0,0)))

        all_screen_elements_sorted = raycast.raycast(dest.width, dest.height, self.resolution, self.x, self.y, self.direction, 90, map, all_sprites)
        for scr_element in all_screen_elements_sorted:
            surf, rect = scr_element.surface_and_rect()
            dest.blit(surf, rect)