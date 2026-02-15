import pygame
import math
import settings
import utilityfuncs
import textures
import render
import deleter
import worldmap
import worldsprite

EXTREME_RES = 1280 # benchmarking
MAX_RES = 640
DEFAULT_RES = 160
BETTER_RES = 320
MIN_RES = 80


# 16x16 resize
mobster_sprite = textures.mobster_texture

# Player 
class Player:
    def __init__(self, x: int, y: int):
        self.x:int = x
        self.y:int = y

        self.hsp = 0
        self.vsp = 0
        self.cam_x = self.x
        self.cam_y = self.y
        self.resolution = MAX_RES
        self.direction = 0
        self.locked_dir = 0
        self.z_lookup = 0
        self.z_lookup_limit = 128

        self.hitbox_width = 18
        self.hitbox = pygame.Rect(self.x - self.hitbox_width/2, self.y - self.hitbox_width/2, self.hitbox_width, self.hitbox_width)
    
    def movement(self, maph:list[list[int]]):

        forward_movement = (pygame.key.get_pressed()[pygame.K_w] - pygame.key.get_pressed()[pygame.K_s])
        sidestep_movement = (pygame.key.get_pressed()[pygame.K_a] - pygame.key.get_pressed()[pygame.K_d])

        self.hsp = pygame.math.lerp(self.hsp, math.cos(math.radians(self.direction)) * forward_movement + math.cos(math.radians(self.direction+90)) * sidestep_movement, 0.5)
        self.vsp = pygame.math.lerp(self.vsp, math.sin(math.radians(self.direction)) * forward_movement + math.sin(math.radians(self.direction+90)) * sidestep_movement, 0.5)
        
        wishX = self.x + self.hsp * 8
        wishY = self.y - self.hsp * 8

        conv_x, conv_y = settings.translate_coords((wishX, wishY))
        
        # Weird hitscan stuff
        if pygame.key.get_pressed()[pygame.K_e]:
            for i in range(7):
                hitscan(self.x, self.y, 1000, self.direction, 10, maph)

        # collision and movement
        # search for all nearby hitboxes
        cell_x, cell_y = int(self.x / settings.cell_width), int(self.y / settings.cell_width)
        all_surrounding_hitboxes:list[pygame.Rect] = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if maph[cell_y+j][cell_x+i] != 0:
                    all_surrounding_hitboxes.append(pygame.Rect((cell_x + i) * settings.cell_width, (cell_y + j) * settings.cell_width, settings.cell_width, settings.cell_width))
        
        # collision
        for hitbox in all_surrounding_hitboxes:
            # hitbox in the front
            wishX_hitbox = pygame.Rect(self.x - self.hitbox_width/2 + self.hsp, self.y - self.hitbox_width/2, self.hitbox_width, self.hitbox_width)
            wishY_hitbox = pygame.Rect(self.x - self.hitbox_width/2, self.y - self.hitbox_width/2 - self.vsp, self.hitbox_width, self.hitbox_width)
            if wishX_hitbox.colliderect(hitbox):
                self.hsp = 0
            if wishY_hitbox.colliderect(hitbox):
                self.vsp = 0
        
        
        self.x += self.hsp
        self.y -= self.vsp

        # using mouse rotate direction
        self.direction -= (pygame.mouse.get_pos()[0] - settings.SCREEN_WIDTH/2) * 0.1
        self.z_lookup += (pygame.mouse.get_pos()[1] - settings.SCREEN_HEIGHT/2) * 0.75
        self.z_lookup = min(max(-self.z_lookup_limit, self.z_lookup), self.z_lookup_limit)

        # using keys to rotate direction
        rotate_vector = (pygame.key.get_pressed()[pygame.K_LEFT] - pygame.key.get_pressed()[pygame.K_RIGHT]) * (0.01 + int(pygame.key.get_pressed()[pygame.K_LSHIFT]) + 1.99)
        self.direction += rotate_vector
        self.direction = utilityfuncs.clamp_directionals(self.direction)

        self.cam_x = pygame.math.lerp(self.cam_x, self.x, 0.1)
        self.cam_y = pygame.math.lerp(self.cam_y, self.y, 0.1)

        pygame.mouse.set_pos((settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2))



    def rendering(self, dest: pygame.Surface, maph:list[list[int]]):
        w, h = dest.get_width(), dest.get_height()
        all_screen_elements_sorted = render.raycast(w, h, self.resolution, self.x, self.y, self.direction, 90, maph)
        for scr_element in all_screen_elements_sorted:
            surf, rect = scr_element.surface_and_rect()
            rect.y -= self.z_lookup
            dest.blit(surf, rect)



def hitscan(x:float, y:float, range: int, direction:float, damage:int, maph:list[list[int]]):
    movement_vector_x = math.cos(math.radians(direction)) * 4
    movement_vector_y = math.sin(math.radians(direction)) * 4

    while range > 0:
        ix, iy = int(x / settings.cell_width), int(y / settings.cell_width)
        vix, viy = int((x + movement_vector_x * 4) / settings.cell_width), int((y - movement_vector_y * 4) / settings.cell_width)
        
        if maph[viy][ix]:
            range = -1000
        else:
            x += movement_vector_x
        if maph[iy][vix]:
            range = -1000
        else:
            y -= movement_vector_y


class Actor:
    all_enemies:list[BaseEnemy] = []
    all_projectiles:list[FireBall] = []
    def __init__(self, x, y, width, texture:pygame.Surface):
        self.x = x
        self.y = y
        self.width = width
        self.hitbox = pygame.Rect(self.x - self.width/2, self.y - self.width/2, self.width, self.width)
        self.world_sprite = worldsprite.WorldSprite(self.x, self.y, self.width, self.width, texture, 0.4)

    def update(self):
        self.hitbox.center = (self.x, self.y)
        self.world_sprite.x = self.x
        self.world_sprite.y = self.y
        self.world_sprite.update()
    
    # Must implement destroy themselves
    def destroy(self):
        pass

class BaseEnemy(Actor):
    def __init__(self, x, y, width):
        super().__init__(x, y, width, textures.mobster_texture)
        Actor.all_enemies.append(self)

    def update(self):
        super().update()

    def destroy(self):
        deleter.Deleter.request_delete(self, Actor.all_enemies)
        self.world_sprite.destroy()

class FireBall(Actor):
    def __init__(self, x, y, width, texture, direction, speed):
        super().__init__(x, y, width, texture)
        self.direction = direction
        self.speed = speed
        Actor.all_projectiles.append(self)

    def update(self):
        super().update()
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y -= math.sin(math.radians(self.direction)) * self.speed
        cell_x, cell_y = int(self.x / settings.cell_width), int(self.y / settings.cell_width)
        if worldmap.game_map[cell_y][cell_x] != 0:
            self.destroy()
    
    def destroy(self):
        deleter.Deleter.request_delete(self, Actor.all_projectiles)
        # self.world_sprite.destroy()