import pygame
import math
import settings
import utilityfuncs
import textures
import render
import deleter
import worldmap
import worldsprite
from random import randrange

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
        self.zheight:int = 0
        self.hsp = 0
        self.vsp = 0
        self.movespeed = 1.5
        self.cam_x = self.x
        self.cam_y = self.y
        self.resolution = MAX_RES
        self.direction = 0
        self.locked_dir = 0
        self.z_lookup = 0
        self.z_lookup_limit = 256
        self.rof = 0

        self.hitbox_width = 18
        self.hitbox = pygame.Rect(self.x - self.hitbox_width/2, self.y - self.hitbox_width/2, self.hitbox_width, self.hitbox_width)

        self.bob_count = 0
        self.bob_magnitude = 0
    
    def movement(self, maph:list[list[int]]):

        forward_movement = (pygame.key.get_pressed()[pygame.K_w] - pygame.key.get_pressed()[pygame.K_s]) * self.movespeed
        sidestep_movement = (pygame.key.get_pressed()[pygame.K_a] - pygame.key.get_pressed()[pygame.K_d]) * self.movespeed

        self.hsp = pygame.math.lerp(self.hsp, math.cos(math.radians(self.direction)) * forward_movement + math.cos(math.radians(self.direction+90)) * sidestep_movement, 0.2)
        self.vsp = pygame.math.lerp(self.vsp, math.sin(math.radians(self.direction)) * forward_movement + math.sin(math.radians(self.direction+90)) * sidestep_movement, 0.2)
        
        # Firing projectile
        if pygame.mouse.get_pressed()[0] and self.rof > 15:
            for i in range(7):
                # hitscan(self.x, self.y, 16, 1000, self.direction + randrange(-3, 3), self.z_lookup/9 + randrange(-3, 3), 10, maph)
                FireBall(self.x
                         , self.y
                         , self.zheight+16 + self.bob_magnitude, 12
                         , textures.fireball_texture
                         , self.direction + randrange(-3, 3)
                         , self.z_lookup/9 + randrange(-3, 3)
                         , 5
                         )
            self.rof = 0
        self.rof += 1

        # collision and movement
        # search for all nearby hitboxes
        cell_x, cell_y = int(self.x / settings.cell_width), int(self.y / settings.cell_width)
        all_surrounding_hitboxes:list[pygame.Rect] = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if maph[cell_y+j][cell_x+i] != 0:
                    all_surrounding_hitboxes.append(pygame.Rect((cell_x + i) * settings.cell_width, (cell_y + j) * settings.cell_width, settings.cell_width, settings.cell_width))
        
        # Collision and movement
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
        
        # Head bob
        if abs(self.hsp + self.vsp) > 0.01:
            self.bob_count += 0.3
            if self.bob_count >= 360:
                self.bob_count = 0
            self.bob_magnitude = math.sin(self.bob_count/2) * 0.5
        else:
            self.bob_magnitude = pygame.math.lerp(self.bob_magnitude, 0, 0.1)

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
        levels = worldmap.worldheight
        all_screen_elements_sorted = render.raycast(w, h, self.resolution, self.x, self.y, self.bob_magnitude - self.zheight, self.z_lookup, self.direction, 90, maph)
        for scr_element in all_screen_elements_sorted:
            if scr_element.no_repeats:
                surf, rect = scr_element.surface_and_rect()
                rect.y -= self.z_lookup
                dest.blit(surf, rect)
            else:
                if scr_element.y + scr_element.height < 0:
                    continue
                surf, rect = scr_element.surface_and_rect()
                rect.y -= self.z_lookup

                for i in range(levels):
                    if rect.y + scr_element.height and rect.y < settings.SCREEN_HEIGHT:
                        dest.blit(surf, rect)
                    rect.y -= scr_element.height-1



def hitscan(x:float, y:float, z:float, _range: int, direction:float, zdirection:float, damage:int, maph:list[list[int]]):
    movement_vector_x = math.cos(math.radians(direction)) * 4 * math.cos(math.radians(zdirection))
    movement_vector_y = math.sin(math.radians(direction)) * 4 * math.cos(math.radians(zdirection))
    movement_vector_z = math.sin(math.radians(zdirection)) * 4
    z -= movement_vector_z

    while _range > 0:
        ix, iy = int(x / settings.cell_width), int(y / settings.cell_width)
        vix, viy = int((x + movement_vector_x * 4) / settings.cell_width), int((y - movement_vector_y * 4) / settings.cell_width)
        
        if maph[viy][ix]:
            _range = -1000
        else:
            x += movement_vector_x
        if maph[iy][vix]:
            _range = -1000
        else:
            y -= movement_vector_y

        if not (z >= 0 and z <= 32 * worldmap.worldheight):
            _range = -1000
        else:
            z -= movement_vector_z
        
        _range -= 1
    
    FireBall(x, y, z, 12, textures.fireball_texture, direction, zdirection, 5)


class Actor:
    all_enemies:list[BaseEnemy] = []
    all_projectiles:list[FireBall] = []
    def __init__(self, x, y, z, width, texture:pygame.Surface, scale_size=1):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.hitbox = pygame.Rect(self.x - self.width/2, self.y - self.width/2, self.width, self.width)
        self.world_sprite = worldsprite.WorldSprite(self.x, self.y, self.z, self.width, self.width, texture, scale_size)
        self.current_actor_block: ActorBlock = actor_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)]

    def update(self):
        self.hitbox.center = (self.x, self.y)
        self.world_sprite.x = self.x
        self.world_sprite.y = self.y
        self.world_sprite.z = self.z
        self.world_sprite.update()

        # changing actor blocks and removing itself from any blocks not currently in
        if actor_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)] != self.current_actor_block:
            self.current_actor_block.contained_actor.discard(self)
            self.current_actor_block = actor_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)]
        if self not in self.current_actor_block.contained_actor:
            self.current_actor_block.contained_actor.add(self)
    
    # Must implement destroy themselves
    def destroy(self):
        pass

class BaseEnemy(Actor):
    def __init__(self, x, y, z, width):
        super().__init__(x, y, z, width, textures.mobster_texture)
        Actor.all_enemies.append(self)

    def update(self):
        super().update()

    def destroy(self):
        deleter.Deleter.request_delete(self, Actor.all_enemies)
        self.world_sprite.destroy()


class FireBall(Actor):
    def __init__(self, x, y, z, width, texture, direction, zdirection, speed):
        super().__init__(x, y, z, width, texture, 0.1)
        self.direction = direction
        self.zdirection = zdirection
        self.speed = speed
        Actor.all_projectiles.append(self)

        self.z -= math.sin(math.radians(self.zdirection)) * self.speed

        self.is_moving = True

    def update(self):
        super().update()
        if self.is_moving:
            self.x += math.cos(math.radians(self.direction)) * self.speed * math.cos(math.radians(self.zdirection))
            self.y -= math.sin(math.radians(self.direction)) * self.speed * math.cos(math.radians(self.zdirection))
            self.z -= math.sin(math.radians(self.zdirection)) * self.speed

        cell_x, cell_y = int(self.x / settings.cell_width), int(self.y / settings.cell_width)
        if worldmap.game_map[cell_y][cell_x] != 0 or not (self.z > 0 and self.z < 32 * worldmap.worldheight):
            self.destroy()
    
    def destroy(self):
        deleter.Deleter.request_delete(self, Actor.all_projectiles)
        self.world_sprite.destroy()


# blockmaps for collision purposes
class ActorBlock:
    def __init__(self):
        self.contained_actor:set[Actor] = set()

actor_blockmap = [
    [ActorBlock() for i in range(len(worldmap.game_map[0]))] for j in range(len(worldmap.game_map))
]
