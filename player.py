import pygame
import math
import settings
import utilityfuncs
import textures
import screen_elements
import actors
import random

EXTREME_RES = 1280 # benchmarking
MAX_RES = 640
DEFAULT_RES = 160
BETTER_RES = 320
MIN_RES = 80
RAYCAST_SIZE_SCALE = 320 # 360
MAX_SPRITE_SCALE = 720


# 16x16 resize
# sprite_x, sprite_y = 8 * settings.cell_width, 3 * settings.cell_width
# sprite_hitbox:pygame.Rect = pygame.Rect(sprite_x - 16, sprite_y - 16, 32, 32)
mobster_sprite = textures.mobster_texture
# mobster_sprite_subsurface = textures.mobster_texture_subsurfaces
# sprite_direction = 0

all_sprites:list[actors.WorldSprite] = [
    actors.WorldSprite(8 * settings.cell_width, 4 * settings.cell_width, 32, 32, textures.gore_head_texture) for i in range(20)#,
    # actors.WorldSprite(14 * settings.cell_width, 1.5 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(1.5 * settings.cell_width, 1.5 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(12 * settings.cell_width, 11.5 * settings.cell_width, 32, 32, mobster_sprite)
]
# upds

lightsource = (8 * settings.cell_width, 3 * settings.cell_width)
light_radius = 192

class Player:
    def __init__(self, x: int, y: int):
        self.x:int = x
        self.y:int = y
        self.resolution = BETTER_RES#MAX_RES
        self.direction = 0
        self.offset = 0
    
    def movement(self, map:list[list[int]]):
        movement_vector = (pygame.key.get_pressed()[pygame.K_w] - pygame.key.get_pressed()[pygame.K_s]) * 2
        front_vec_x = self.x + math.cos(math.radians(self.direction)) * movement_vector * 8
        front_vec_y = self.y - math.sin(math.radians(self.direction)) * movement_vector * 8
        
        conv_x, conv_y = settings.translate_coords((front_vec_x, front_vec_y))
        
        # horizontal
        if map[int(conv_y)][int(self.x/settings.cell_width)] == 0:
            self.y -= math.sin(math.radians(self.direction)) * movement_vector
        if map[int(self.y/settings.cell_width)][int(conv_x)] == 0:
            self.x += math.cos(math.radians(self.direction)) * movement_vector

        rotate_vector = (pygame.key.get_pressed()[pygame.K_a] - pygame.key.get_pressed()[pygame.K_d]) * (0.01 + int(pygame.key.get_pressed()[pygame.K_LSHIFT]) + 1)
        self.direction += rotate_vector
        self.direction = utilityfuncs.clamp_directionals(self.direction)

    def rendering(self, dest: pygame.Surface, map:list[list[int]]):
        w, h = dest.get_width(), dest.get_height()
        map_w, map_h = len(map[0]), len(map)

        # BETTER RAYCASTER
        fov = 90
        height_scale = 40
        __d = self.direction + fov/2
        column_width = w/self.resolution
        previous_height = 0

        screen_elements_list:list[screen_elements.ScreenElement] = []

        for i in range(self.resolution):
            elements_found = [] # [( element_name: str, element_coords: [float, float], distance_to_element: float, subsurface_array )]
            
            if __d != 0:
                verStepX, verStepY = -1, -1
                horStepX, horStepY = -1, -1
                dircos, dirsin = math.cos(math.radians(__d)), math.sin(math.radians(__d))

                # Vertical Intersection
                Vx, Vy = 0, 0
                if utilityfuncs.sign(dircos) > 0:
                    Vx = math.floor(self.x/settings.cell_width) * settings.cell_width + settings.cell_width
                else:
                    Vx = int(self.x/settings.cell_width) * settings.cell_width - 1
                Vy = self.y + (self.x - Vx) * math.tan(math.radians(__d))

                verStepX = utilityfuncs.sign(dircos) * settings.cell_width
                verStepY = settings.cell_width * math.tan(math.radians(__d)) * utilityfuncs.sign(dircos)


                # Horizontal Intersection
                Hx, Hy = 0, 0
                if -utilityfuncs.sign(dirsin) > 0:
                    Hy = int(self.y / settings.cell_width) * settings.cell_width + settings.cell_width
                else:
                    Hy = int(self.y / settings.cell_width) * settings.cell_width - 1
                Hx = self.x + (self.y - Hy) / math.tan(math.radians(__d))
                
                horStepX = utilityfuncs.sign(dirsin) * settings.cell_width / math.tan(math.radians(__d))
                horStepY = utilityfuncs.sign(dirsin) * settings.cell_width

                horLength = utilityfuncs.square_distance(self.x, self.y, Vx, Vy)
                verLength = utilityfuncs.square_distance(self.x, self.y, Hx, Hy)


                hitX, hitY = -1, -1
                orientation = -1 # 0 -> Vertical, 1 -> Horizontal
                while True:
                    if horLength < verLength:
                        if map[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)] != 0:
                            hitX = Vx
                            hitY = Vy
                            orientation = 0
                            break
                        Vx += verStepX
                        Vy -= verStepY
                        horLength = utilityfuncs.square_distance(self.x, self.y, Vx, Vy)
                    else:
                        if map[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)] != 0:
                            hitX = Hx
                            hitY = Hy
                            orientation = 1
                            break
                        Hx += horStepX
                        Hy -= horStepY
                        verLength = utilityfuncs.square_distance(self.x, self.y, Hx, Hy)
            
            # Wall height calculation
            dist = round(utilityfuncs.point_distance(self.x, self.y, hitX, hitY)) + 0.1
            offset_ratio = math.cos(math.radians(__d - self.direction))
            height = (RAYCAST_SIZE_SCALE / (dist/height_scale)) / offset_ratio
            if __d == 0:
                height = previous_height
            else:
                previous_height = height

            # Texturing
            texture_tuple = textures.quick_access_texture[map[int(hitY/settings.cell_width)][int(hitX/settings.cell_width)]-1]
            s_texture = texture_tuple[0]
            s_texture_sub = texture_tuple[1]

            if orientation == 1:
                percentage_of_cube = (hitX - (int(hitX/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, h/2-height/2, dist, height, texture_surface))
                
            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, h/2-height/2, dist, height, texture_surface))

            __d -= fov/self.resolution

        # Sprite rendering
        for sprite in all_sprites:
            sprite_x = sprite.x
            sprite_y = sprite.y
            direction_to_sprite = utilityfuncs.clamp_directionals(utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y)) #utilityfuncs.clamp_directionals(self.direction - utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y))
            left_direction = utilityfuncs.clamp_directionals(self.direction + (fov/2))
            delta_dir = utilityfuncs.clamp_directionals(left_direction - direction_to_sprite) / (fov)
            sprite_x_onscreen = delta_dir * w
            distance_to_sprite = utilityfuncs.point_distance(self.x, self.y, sprite_x, sprite_y) + 0.1
            sprite_height = (RAYCAST_SIZE_SCALE / (distance_to_sprite/height_scale))
            sprite_height = min(sprite_height, MAX_SPRITE_SCALE)
            screen_elements_list.append(screen_elements.ScreenElement(sprite_x_onscreen, h/2-sprite_height/2, distance_to_sprite, sprite_height, sprite.get_texture(), True, center_sprite=True))

        screen_elements_list.sort(reverse=True)
        for scr_element in screen_elements_list:
            render_data = scr_element.surface_and_rect()
            dest.blit(render_data[0], render_data[1])

        # for i in range(self.resolution):
        #     wall_information = wall_data[i]
        #     texture_rect = pygame.Rect(i * column_width, h/2-wall_information[0]/2, column_width, wall_information[0])
        #     dest.blit(wall_information[1], texture_rect)