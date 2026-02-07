import pygame
import screen_elements
import math
import utilityfuncs
import settings
import textures
import numpy
import actors
from numba import njit

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

# Try the NumPy approach.
PLAYER_HEIGHT = 16
RAYCAST_SIZE_SCALE = 320 # 360
MAX_SPRITE_SCALE = 720
# 3600 is the limit
RAYCAST_LOOKUP_TABLE:dict[float:dict[str:float]] = dict()
TEXTURE_LOOKUP_TABLE:dict[tuple[float, int] : pygame.Surface]
# limit: 640
FISHEYE_CORRECTION_LOOKUP_TABLE:dict[float:float] = dict()


def raycast(screen_width, screen_height, resolution, x, y, direction, fov, map:list[list[int]], spriteList:list[actors.WorldSprite]) -> list[screen_elements.ScreenElement]:
        map_w, map_h = len(map[0]), len(map)

        height_scale = 40
        __d = direction + fov/2
        column_width = round(screen_width/resolution)
        previous_height = 0

        screen_elements_list:list[screen_elements.ScreenElement] = []
        

        for i in range(resolution):
            if __d != 0:
                dircos, dirsin = -1, -1
                verStepX, verStepY = -1, -1
                horStepX, horStepY = -1, -1

                dircos, dirsin = math.cos(math.radians(__d)), math.sin(math.radians(__d))
                verStepX, verStepY = utilityfuncs.sign(dircos) * settings.cell_width, settings.cell_width * math.tan(math.radians(__d)) * utilityfuncs.sign(dircos)
                horStepX, horStepY = utilityfuncs.sign(dirsin) * settings.cell_width / math.tan(math.radians(__d)), utilityfuncs.sign(dirsin) * settings.cell_width

                horizontal_intersection_distances = []
                vertical_intersection_distances   = []
                # if __d not in RAYCAST_LOOKUP_TABLE.keys():
                #     dircos, dirsin = math.cos(math.radians(__d)), math.sin(math.radians(__d))
                #     verStepX, verStepY = utilityfuncs.sign(dircos) * settings.cell_width, settings.cell_width * math.tan(math.radians(__d)) * utilityfuncs.sign(dircos)
                #     horStepX, horStepY = utilityfuncs.sign(dirsin) * settings.cell_width / math.tan(math.radians(__d)), utilityfuncs.sign(dirsin) * settings.cell_width
                #     # store these values in lookup tables
                #     RAYCAST_LOOKUP_TABLE[__d] = {
                #         "DIRCOS" : -1,
                #         "DIRSIN" : -1,
                #         "VERSTEPX" : -1,
                #         "VERSTEPY" : -1,
                #         "HORSTEPX" : -1,
                #         "HORSTEPY" : -1,
                #     }
                #     RAYCAST_LOOKUP_TABLE[__d]["DIRCOS"] = dircos
                #     RAYCAST_LOOKUP_TABLE[__d]["DIRSIN"] = dirsin
                #     RAYCAST_LOOKUP_TABLE[__d]["VERSTEPX"] = verStepX
                #     RAYCAST_LOOKUP_TABLE[__d]["VERSTEPY"] = verStepY
                #     RAYCAST_LOOKUP_TABLE[__d]["HORSTEPX"] = horStepX
                #     RAYCAST_LOOKUP_TABLE[__d]["HORSTEPY"] = horStepY
                # else:
                #     dircos, dirsin = RAYCAST_LOOKUP_TABLE[__d]["DIRCOS"], RAYCAST_LOOKUP_TABLE[__d]["DIRSIN"]
                #     verStepX, verStepY = RAYCAST_LOOKUP_TABLE[__d]["VERSTEPX"], RAYCAST_LOOKUP_TABLE[__d]["VERSTEPY"]
                #     horStepX, horStepY = RAYCAST_LOOKUP_TABLE[__d]["HORSTEPX"], RAYCAST_LOOKUP_TABLE[__d]["HORSTEPY"]


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
                    Hy = int(y / settings.cell_width) * settings.cell_width - 1 * (utilityfuncs.sign(dirsin) > 0)
                Hx = x + (y - Hy) / math.tan(math.radians(__d))

                horLength = utilityfuncs.square_distance(x, y, Vx, Vy)
                verLength = utilityfuncs.square_distance(x, y, Hx, Hy)

                hitX, hitY = -1, -1
                orientation = -1 # 0 -> Horizontal, 1 -> Vertical
                while True:
                    if horLength < verLength:
                        if map[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)] != 0:
                            hitX = Vx
                            hitY = Vy
                            orientation = 0
                            break
                        vertical_intersection_distances.append(horLength)
                        Vx += verStepX
                        Vy -= verStepY
                        horLength = utilityfuncs.square_distance(x, y, Vx, Vy) + 0.01
                    else:
                        if map[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)] != 0:
                            hitX = Hx
                            hitY = Hy
                            orientation = 1
                            break
                        horizontal_intersection_distances.append(verLength)
                        Hx += horStepX
                        Hy -= horStepY
                        verLength = utilityfuncs.square_distance(x, y, Hx, Hy) + 0.01

            # pushwalls
            height_offset = 0

            # Fisheye correction + lookup table
            offset_ratio = 1
            if (__d - direction) not in FISHEYE_CORRECTION_LOOKUP_TABLE.keys():
                offset_ratio = math.cos(math.radians(__d - direction))
                FISHEYE_CORRECTION_LOOKUP_TABLE[(__d - direction)] = offset_ratio
            else:
                offset_ratio = FISHEYE_CORRECTION_LOOKUP_TABLE[(__d - direction)]

            # Wall height calculation
            dist = round(utilityfuncs.point_distance(x, y, hitX, hitY)) + 0.1
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
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, screen_height/2-height/2 - (height_offset/16) * height/2, dist, height, texture_surface))
                
            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                shadow_surface = pygame.Surface((column_width, height))
                shadow_surface.fill((0,0,0))
                shadow_surface.set_alpha(150)
                texture_surface.blit(shadow_surface)
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, screen_height/2-height/2 - (height_offset/16) * height/2, dist, height, texture_surface))
            
            # Floorcasting -> will be done in a differe
            # for distance in horizontal_intersection_distances:
                # draw 
                # floor_draw_surface = pygame.Surface((4, 4))
                #y_coordinate = screen_height/2 + height/2 #+ (1/(distance+0.1)) * dist
                #half_h = screen_height/2
                # full_dist = dist
                # n = full_dist / (full_dist - distance)
                # x, y = 
                # screen_elements_floor_list.append(screen_elements.ScreenElement(i*column_width, y_coordinate, distance, 4, floor_draw_surface))
            __d -= fov/resolution
        # Sprite rendering
        # Can do better -> zbuffering
        # Basically split up the sprite into different parts.
        # Can "add" a strip to another -> add a function to the strip.
        for sprite in spriteList:
            sprite_x = sprite.x
            sprite_y = sprite.y
            direction_to_sprite = utilityfuncs.clamp_directionals(utilityfuncs.point_direction(x, y, sprite_x, sprite_y)) #utilityfuncs.clamp_directionals(direction - utilityfuncs.point_direction(x, y, sprite_x, sprite_y))
            left_direction = utilityfuncs.clamp_directionals(direction + (fov/2))
            delta_dir = utilityfuncs.clamp_directionals(left_direction - direction_to_sprite) / (fov)
            sprite_x_onscreen = delta_dir * screen_width
            distance_to_sprite = utilityfuncs.point_distance(x, y, sprite_x, sprite_y) + 0.1
            sprite_height = (RAYCAST_SIZE_SCALE / (distance_to_sprite/height_scale))
            sprite_height = min(sprite_height, MAX_SPRITE_SCALE)
            screen_elements_list.append(screen_elements.ScreenElement(sprite_x_onscreen, screen_height/2-sprite_height/2, distance_to_sprite, sprite_height, sprite.get_texture(), True, center_sprite=True))

        screen_elements_list.sort(reverse=True)
        return screen_elements_list


sky_texture = pygame.surfarray.array3d(pygame.transform.scale(textures.doom_sky_texture, (360, settings.SCREEN_HEIGHT//2)))/255
floor_texture = pygame.surfarray.array3d(textures.brick_texture)/255

@njit()
def floorcast(x, y, direction, floor_matrix:numpy.ndarray):
    x /= settings.cell_width
    y /= settings.cell_width
    hor_n = floor_matrix.shape[0]
    ver_n = floor_matrix.shape[1]
    half_ver = ver_n // 2
    mod = hor_n / 90
    for i in range(hor_n):
        rot_i = numpy.deg2rad(direction) + numpy.deg2rad(i/mod - 45)
        sin, cos, cos2 = numpy.sin(rot_i), numpy.cos(rot_i), numpy.cos(numpy.deg2rad(i/mod-45))
        floor_matrix[hor_n-1-i][:] = sky_texture[int(numpy.rad2deg(rot_i)%359)][:]
        for j in range(int(half_ver)):
            n = half_ver / (half_ver-j) / cos2
            pos_x, pos_y = x + cos*n, y - sin*n
            xx, yy, = int(pos_x%1*int(floor_texture.shape[0])), int(pos_y%1*int(floor_texture.shape[1]))
            floor_matrix[hor_n-i-1][ver_n-j-1] = floor_texture[xx][yy]