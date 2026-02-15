import pygame
import screen_elements
import math
import utilityfuncs
import settings
import textures
import worldsprite


# Dictionary
    # Key: Direction: 
        # Value:
        # Dictionary: 
            # ALL KEYS:      ALL VALS
            # verStepX          - val
            # verStepY          - val
            # horStepX          - val
            # horStepY          - val
            # dircos            - val
            # dirsin            - val

MAX_DARKNESS_LEVEL = 0

PLAYER_HEIGHT = 16
RAYCAST_SIZE_SCALE = 320 # 360
MAX_SPRITE_SCALE = 720
# 3600 is the limit
RAYCAST_LOOKUP_TABLE:dict[float:dict[str:float]] = dict()
TEXTURE_LOOKUP_TABLE:dict[tuple[float, int] : pygame.Surface]
# limit: 640
FISHEYE_CORRECTION_LOOKUP_TABLE:dict[float:float] = dict()

light_pos_dict:dict[tuple[int, int], int] = dict()

def raycast(screen_width, screen_height, resolution, x, y, direction, fov, maph:list[list[int]]) -> list[screen_elements.ScreenElement]:
        height_scale = 40
        __d = direction + fov/2
        column_width = round(screen_width/resolution)
        previous_height = 0

        screen_elements_list:list[screen_elements.ScreenElement] = []
        floor_elements_list :list[screen_elements.ScreenElement] = []

        all_visible_sprites :set[worldsprite.WorldSprite] = set()

        for i in range(resolution):
            if __d != 0:
                dircos, dirsin = -1, -1
                verStepX, verStepY = -1, -1
                horStepX, horStepY = -1, -1

                dircos, dirsin = math.cos(math.radians(__d)), math.sin(math.radians(__d))
                verStepX, verStepY = utilityfuncs.sign(dircos) * settings.cell_width, settings.cell_width * math.tan(math.radians(__d)) * utilityfuncs.sign(dircos)
                horStepX, horStepY = utilityfuncs.sign(dirsin) * settings.cell_width / math.tan(math.radians(__d)), utilityfuncs.sign(dirsin) * settings.cell_width

                # Vertical Intersection
                Vx, Vy = 0, 0
                if utilityfuncs.sign(dircos) > 0:
                    Vx = math.floor(x/settings.cell_width) * settings.cell_width + settings.cell_width
                else:
                    Vx = int(x/settings.cell_width) * settings.cell_width - 1 
                Vy = y + (x - Vx) * math.tan(math.radians(__d))

                # Horizontal Intersection
                Hx, Hy = 0, 0
                if -utilityfuncs.sign(dirsin) > 0:
                    Hy = int(y / settings.cell_width) * settings.cell_width + settings.cell_width
                else:
                    Hy = int(y / settings.cell_width) * settings.cell_width - 1 * (utilityfuncs.sign(dirsin) > 0) - 0.01
                Hx = x + (y - Hy) / math.tan(math.radians(__d))

                horLength = utilityfuncs.square_distance(x, y, Vx, Vy)
                verLength = utilityfuncs.square_distance(x, y, Hx, Hy)

                hitX, hitY = -1, -1
                orientation = -1 # 0 -> Horizontal, 1 -> Vertical
                while True:
                    if horLength < verLength:
                        spr_block_atpos = worldsprite.sprite_blockmap[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)]
                        for spr in spr_block_atpos.contained_sprites:
                            all_visible_sprites.add(spr)
                        if maph[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)] != 0:
                            hitX = Vx
                            hitY = Vy
                            orientation = 0
                            break
                        Vx += verStepX
                        Vy -= verStepY
                        horLength = utilityfuncs.square_distance(x, y, Vx, Vy) + 0.01
                    else:
                        spr_block_atpos = worldsprite.sprite_blockmap[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)]
                        for spr in spr_block_atpos.contained_sprites:
                            all_visible_sprites.add(spr)
                        if maph[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)] != 0:
                            hitX = Hx
                            hitY = Hy
                            orientation = 1
                            break
                        Hx += horStepX
                        Hy -= horStepY
                        verLength = utilityfuncs.square_distance(x, y, Hx, Hy) + 0.01

            # pushwalls
            height_offset = 0
            offset_ratio = math.cos(math.radians(__d - direction))

            # Wall height calculation
            dist = round(utilityfuncs.point_distance(x, y, hitX, hitY)) + 0.1
            height = (RAYCAST_SIZE_SCALE / (dist/height_scale)) / offset_ratio
            if __d == 0:
                height = previous_height
            else:
                previous_height = height

            # Texturing
            texture_tuple = textures.quick_access_texture[maph[int(hitY/settings.cell_width)][int(hitX/settings.cell_width)]]
            s_texture = texture_tuple[0]
            s_texture_sub = texture_tuple[1]

            if orientation == 1:
                percentage_of_cube = (hitX - (int(hitX/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)

                # Darkness
                darkness_surface = pygame.Surface((column_width, height))
                darkness_surface.fill((0, 0, 0))
                darkness_level = MAX_DARKNESS_LEVEL
                if (int(hitX/4), int(hitY/4)) in light_points:#[(int(hitX/4), int(hitY/4))]
                    if light_points[(int(hitX/4), int(hitY/4))][1] == orientation:
                        darkness_level = MAX_DARKNESS_LEVEL - light_points[(int(hitX/4), int(hitY/4))][0]
                darkness_surface.set_alpha(darkness_level)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                texture_surface.blit(darkness_surface, darkness_surface.get_rect(topleft=(0,0)))
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, screen_height/2-height/2 - (height_offset/16) * height/2, dist, height, texture_surface))
                
            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                
                # Darkness
                darkness_surface = pygame.Surface((column_width, height))
                darkness_surface.fill((0, 0, 0))
                darkness_level = MAX_DARKNESS_LEVEL
                if (int(hitX/4), int(hitY/4)) in light_points:#[(int(hitX/4), int(hitY/4))]
                    if light_points[(int(hitX/4), int(hitY/4))][1] == orientation:
                        darkness_level = MAX_DARKNESS_LEVEL - light_points[(int(hitX/4), int(hitY/4))][0]
                darkness_surface.set_alpha(darkness_level + 100)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                texture_surface.blit(darkness_surface, darkness_surface.get_rect(topleft=(0,0)))
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, screen_height/2-height/2 - (height_offset/16) * height/2, dist, height, texture_surface))

            __d -= fov/resolution

        # Sprite rendering
        # Can do better -> zbuffering
        # Basically split up the sprite into different parts.
        # Can "add" a strip to another -> add a function to the strip.
        for sprite in all_visible_sprites:
            sprite_x = sprite.x
            sprite_y = sprite.y
            direction_to_sprite = utilityfuncs.clamp_directionals(utilityfuncs.point_direction(x, y, sprite_x, sprite_y)) #utilityfuncs.clamp_directionals(direction - utilityfuncs.point_direction(x, y, sprite_x, sprite_y))
            left_direction = utilityfuncs.clamp_directionals(direction + (fov/2))
            delta_dir = utilityfuncs.clamp_directionals(left_direction - direction_to_sprite) / (fov)
            sprite_x_onscreen = delta_dir * screen_width
            distance_to_sprite = utilityfuncs.point_distance(x, y, sprite_x, sprite_y) + 0.1
            sprite_height = (RAYCAST_SIZE_SCALE / (distance_to_sprite/height_scale))
            sprite_height = min(sprite_height, MAX_SPRITE_SCALE)
            screen_elements_list.append(screen_elements.ScreenElement(sprite_x_onscreen, screen_height/2-(sprite_height/2) * sprite.sprite_scale, distance_to_sprite, sprite_height, sprite.get_texture(), True, center_sprite=True, rescale_val=sprite.sprite_scale))

        screen_elements_list.sort(reverse=True)
        return floor_elements_list + screen_elements_list

# Light Source
# x, y, and orientation
light_points:dict[tuple[int, int], tuple[int, int]] = dict()

def add_light_source(x:int, y:int, direction:int, field_dir:int, radius:int, maph:list[list[int]]):
    all_visited_points = set()
    while field_dir > 0:
        r = radius

        verStepX, verStepY = -1, -1
        horStepX, horStepY = -1, -1
        orientation = 0

        dircos, dirsin = math.cos(math.radians(direction)), math.sin(math.radians(direction))
        verStepX, verStepY = utilityfuncs.sign(dircos) * settings.cell_width, settings.cell_width * math.tan(math.radians(direction)) * utilityfuncs.sign(dircos)
        horStepX, horStepY = utilityfuncs.sign(dirsin) * settings.cell_width / (math.tan(math.radians(direction)) + 0.01), utilityfuncs.sign(dirsin) * settings.cell_width

        # Vertical Intersection
        Vx, Vy = 0, 0
        if utilityfuncs.sign(dircos) > 0:
            Vx = math.floor(x/settings.cell_width) * settings.cell_width + settings.cell_width
        else:
            Vx = int(x/settings.cell_width) * settings.cell_width - 1 
        Vy = y + (x - Vx) * math.tan(math.radians(direction))

        # Horizontal Intersection
        Hx, Hy = 0, 0
        if -utilityfuncs.sign(dirsin) > 0:
            Hy = int(y / settings.cell_width) * settings.cell_width + settings.cell_width
        else:
            Hy = int(y / settings.cell_width) * settings.cell_width - 1 * (utilityfuncs.sign(dirsin) > 0)
        Hx = x + (y - Hy) / (math.tan(math.radians(direction)) + 0.01)

        horLength = utilityfuncs.square_distance(x, y, Vx, Vy)
        verLength = utilityfuncs.square_distance(x, y, Hx, Hy)

        hitX, hitY = -1, -1
        while r > 0:
            if horLength < verLength:
                if maph[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)] != 0:
                    hitX = Vx
                    hitY = Vy
                    orientation = 0
                    break
                Vx += verStepX
                Vy -= verStepY
                horLength = utilityfuncs.square_distance(x, y, Vx, Vy) + 0.01
            else:
                if maph[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)] != 0:
                    hitX = Hx
                    hitY = Hy
                    orientation = 1
                    break
                Hx += horStepX
                Hy -= horStepY
                verLength = utilityfuncs.square_distance(x, y, Hx, Hy) + 0.01

            r -= 32
        
        # The higher the brightness level is, the more bright the walls become
        d = utilityfuncs.point_distance(x, y, hitX, hitY)
        light_level = (1-d/radius) * MAX_DARKNESS_LEVEL
        pt = int(hitX/4), int(hitY/4)
        if (pt in light_points.keys()): #and (pt not in all_visited_points):
            light_points[pt] = (max(light_points[pt][0], light_level), light_points[pt][1])
        else:
            light_points[pt] = (light_level, orientation)
        
        all_visited_points.add(pt)

        direction += 0.01
        field_dir -= 0.01


class LightSource:
    all_light_sources:list[LightSource] = []
    def __init__(self, x:int, y:int, direction:int, field_dir:int, radius:int):
        self.x = x
        self.y = y
        self.direction = direction
        self.field_dir = field_dir
        self.radius = radius
    