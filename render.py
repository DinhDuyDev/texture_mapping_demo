import pygame
import screen_elements
import math
import utilityfuncs
import settings
import textures
import worldsprite
from geometry import Door
from worldmap import game_map

invisible = {0}
traversable = {0}
ray_castable = {-1, 0}

debug_font = pygame.sysfont.SysFont("Arial", 10, False)

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

oneDoor = Door(10, 1, game_map)


# Texture decal test
wall_decal_texture = textures.fireball_texture
wall_decal_texture_subsurfaces = textures.fireball_texture_subsurfaces
wall_decal_coords = (5 * settings.cell_width, 1 * settings.cell_width)


def raycast_new(screen_width, screen_height, resolution, x, y, z, dirX, dirY, planeX, planeY, fov, maph:list[list[int]]):
    height_scale = 2
    column_width = screen_width / resolution

    posX = x / settings.cell_width
    posY = y / settings.cell_width

    screen_elements_list:list[screen_elements.ScreenElement] = []

    for i in range(resolution):
        mapPosX = int(x / settings.cell_width)
        mapPosY = int(y / settings.cell_width)

        cameraX = 2 * (i / resolution) - 1
        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX

        deltaDistX = 1e30 if rayDirX == 0 else abs(1/rayDirX)
        deltaDistY = 1e30 if rayDirY == 0 else abs(1/rayDirY)

        perpWallDist = -1
        sideDistX = -1
        sideDistY = -1

        stepX = -1
        stepY = -1

        hit = False
        side = 0

        if rayDirX < 0:
            stepX = -1
            sideDistX = (posX - mapPosX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapPosX + 1.0 - posX) * deltaDistX


        if rayDirY < 0:
            stepY = -1
            sideDistY = (posY - mapPosY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapPosY + 1.0 - posY) * deltaDistY

        while not hit:
            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                mapPosX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapPosY += stepY
                side = 1
            
            if maph[mapPosY][mapPosX] not in ray_castable:
                hit = True

        texture_tuple = textures.quick_access_texture[maph[mapPosY][mapPosX]]
        whole_texture = texture_tuple[0]
        texture_strips = texture_tuple[1]
        wallX = -1
    
        # side determination
        if side == 0: 
            perpWallDist = abs(sideDistX - deltaDistX)
        else: 
            perpWallDist = abs(sideDistY - deltaDistY)
        
        # where on wall did it hit
        if side == 0:
            wallX = posY + perpWallDist * rayDirY
        else:
            wallX = posX + perpWallDist * rayDirX
        wallX -= int(wallX)

        # Texture strip
        tex_width = whole_texture.width
        texX = int(wallX * tex_width)
        if side == 0 and rayDirX > 0: texX = tex_width - texX - 1
        if side == 1 and rayDirY < 0: texX = tex_width - texX - 1

        height = min(RAYCAST_SIZE_SCALE / (perpWallDist * height_scale), 1280)

        # texture surface
        texture_surface = pygame.transform.scale(texture_strips[texX], (column_width, height))
        texture_y = screen_height/2-height/2 - ((z-16)/32) * height

        strip = screen_elements.ScreenElement((resolution-i) * column_width, texture_y, perpWallDist, height+0.1, texture_surface)
        screen_elements_list.append(strip)

    # Sprite rendering
    for sprite in worldsprite.WorldSprite.all_sprites:
        distToSprite = utilityfuncs.point_distance(x, y, sprite.x, sprite.y) / settings.cell_width

        if distToSprite > 0.5:
            __x, __y = sprite.x / settings.cell_width, sprite.y / settings.cell_width
            
            pX = x / settings.cell_width
            pY = y / settings.cell_width

            sprite_x = __x - pX
            sprite_y = __y - pY
            sprite_z = sprite.z - 16

            invDet = 1.0 / (-planeX * dirY + dirX * planeY) # required for correct matrix multiplication
            transformX = invDet * (dirY * sprite_x - dirX * sprite_y)
            transformY = -invDet * (-planeY * sprite_x + planeX * sprite_y) + 0.1 # depth inside the screen

            if transformY < 0:
                continue

            sprite_screen_x = int((screen_width / 2) * (1 + (transformX / transformY)))
            sprite_height = min(abs(int(screen_height / transformY / height_scale)), 1280)
            sprite_screen_y = (screen_height/2) - (sprite_height/2) * sprite.sprite_scale - (sprite_z/32) * (sprite_height) - (z/32) * (sprite_height)

            screen_elements_list.append(screen_elements.ScreenElement(
                sprite_screen_x
                , sprite_screen_y
                , distToSprite
                , sprite_height
                , sprite.get_texture()
                , True
                , center_sprite=True
                , rescale_val=sprite.sprite_scale
                , no_repeats=True
                ))

    screen_elements_list.sort(reverse=True)
    return screen_elements_list


# Light Source
# x, y, and orientation
light_points:dict[tuple[int, int], tuple[int, int]] = dict()


# Fatum iustum stultorum

def raycast(screen_width, screen_height, resolution, x, y, z, z_lookup, direction, fov, maph:list[list[int]], surface:pygame.Surface=None) -> list[screen_elements.ScreenElement]:
        

        height_scale = 40

        column_width = screen_width/resolution
        previous_height = 0

        screen_elements_list:list[screen_elements.ScreenElement] = []
        all_visible_sprites :set[worldsprite.WorldSprite] = set()
        
        i = 0

        fov_ratio = fov / 90

        distance_from_projection = 50 / (fov / resolution)

        for dy in range(int(resolution//2), int(-resolution//2), -1):
            __d = direction + math.degrees(math.atan2(dy, distance_from_projection))
            if __d != 0:
                dircos, dirsin = -1, -1
                verStepX, verStepY = -1, -1
                horStepX, horStepY = -1, -1
                hitDist = -1

                dircos, dirsin = math.cos(math.radians(__d)), math.sin(math.radians(__d))
                verStepX, verStepY = utilityfuncs.sign(dircos) * settings.cell_width, settings.cell_width * math.tan(math.radians(__d)) * utilityfuncs.sign(dircos)
                horStepX, horStepY = utilityfuncs.sign(dirsin) * settings.cell_width / math.tan(math.radians(__d)), utilityfuncs.sign(dirsin) * settings.cell_width

                # Vertical Intersection
                Vx, Vy = 0, 0
                if utilityfuncs.sign(dircos) > 0:
                    Vx = int(x/settings.cell_width) * settings.cell_width + settings.cell_width
                else:
                    Vx = int(x/settings.cell_width) * settings.cell_width - 1 * (utilityfuncs.sign(dircos) < 0) + 0.9
                Vy = y + (x - Vx) * math.tan(math.radians(__d))

                # Horizontal Intersection
                Hx, Hy = 0, 0
                if -utilityfuncs.sign(dirsin) > 0:
                    Hy = int(int(y / settings.cell_width) * settings.cell_width + settings.cell_width)
                else:
                    Hy = int(y / settings.cell_width) * settings.cell_width - 1 * (utilityfuncs.sign(dirsin) > 0) + 0.9
                Hx = x + (y - Hy) / math.tan(math.radians(__d))

                horLength = utilityfuncs.square_distance(x, y, Vx, Vy)
                verLength = utilityfuncs.square_distance(x, y, Hx, Hy)

                hitX, hitY = -1, -1
                orientation = -1 # 0 -> Horizontal, 1 -> Vertical
                while True:
                    if horLength < verLength:
                        # All sprites seen
                        s_blockX = Vx + 2 * (dirsin < 0)
                        s_blockY = Vy + 2 * (dircos < 0)
                        spr_block_atpos = worldsprite.sprite_blockmap[int(s_blockY/settings.cell_width)][int(s_blockX/settings.cell_width)]
                        for spr in spr_block_atpos.contained_sprites:
                            all_visible_sprites.add(spr)

                        if maph[int(Vy/settings.cell_width)][int(Vx/settings.cell_width)] not in ray_castable:
                            hitX = Vx
                            hitY = Vy
                            orientation = 0
                            hitDist = math.sqrt(horLength) * fov_ratio
                            break
                            
                        Vx += verStepX
                        Vy -= verStepY
                        horLength = utilityfuncs.square_distance(x, y, Vx, Vy) + 0.01
                        
                    else:
                        # All sprites seen
                        s_blockX = Hx + 2 * (dirsin < 0)
                        s_blockY = Hy + 2 * (dircos < 0)
                        spr_block_atpos = worldsprite.sprite_blockmap[int(s_blockY/settings.cell_width)][int(s_blockX/settings.cell_width)]
                        for spr in spr_block_atpos.contained_sprites:
                            all_visible_sprites.add(spr)

                        if maph[int(Hy/settings.cell_width)][int(Hx/settings.cell_width)] not in ray_castable:
                            hitX = Hx
                            hitY = Hy
                            orientation = 1
                            hitDist = math.sqrt(verLength) * fov_ratio
                            break
                        Hx += horStepX
                        Hy -= horStepY
                        verLength = utilityfuncs.square_distance(x, y, Hx, Hy) + 0.01

            # offset ratio (correction)
            offset_ratio = math.cos(math.radians(__d - direction))

            # Wall height calculation
            height = ((RAYCAST_SIZE_SCALE / (hitDist/height_scale)) / offset_ratio)

            # A particular bug with __d = 0
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
                darkness_surface = pygame.Surface((column_width+1, height))
                darkness_surface.fill((0, 0, 0))
                darkness_level = (1-(height/1280) ** 0.8) * 254#MAX_DARKNESS_LEVEL
                if (int(hitX/4), int(hitY/4)) in light_points:#[(int(hitX/4), int(hitY/4))]
                    if light_points[(int(hitX/4), int(hitY/4))][1] == orientation:
                        darkness_level = MAX_DARKNESS_LEVEL - light_points[(int(hitX/4), int(hitY/4))][0]
                darkness_surface.set_alpha(darkness_level)
                texture_surface = pygame.transform.scale(texture_surface, (column_width+1, height))
                texture_surface.blit(darkness_surface, darkness_surface.get_rect(topleft=(0,0)))

                # Draw multiple floors at once
                y_onscreen = screen_height/2-(height/2) - (z/16) * height/2

                strip = screen_elements.ScreenElement(i * column_width, y_onscreen, hitDist, height, texture_surface)
                screen_elements_list.append(strip)

                # Drawing a wall decal
                if utilityfuncs.point_distance(hitX, hitY, wall_decal_coords[0], wall_decal_coords[1]) < wall_decal_texture.width and hitX > wall_decal_coords[0]:
                    slice_index = max(min(int(hitX - wall_decal_coords[0]), wall_decal_texture.width), 0)
                    texture_surf = pygame.transform.scale(wall_decal_texture_subsurfaces[slice_index], (column_width+1, height))
                    strip_y_onscreen = screen_height/2-height/2 - (z/16) * height/2
                    strip.add_accompanying_decal(screen_elements.ScreenElement(i * column_width, strip_y_onscreen, hitDist, height * 0.2, texture_surf))

            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                
                # Darkness
                darkness_surface = pygame.Surface((column_width+1, height))
                darkness_surface.fill((0, 0, 0))
                darkness_level = (1-(height/1280) ** 0.8) * 254 #MAX_DARKNESS_LEVEL
                if (int(hitX/4), int(hitY/4)) in light_points:#[(int(hitX/4), int(hitY/4))]
                    if light_points[(int(hitX/4), int(hitY/4))][1] == orientation:
                        darkness_level = MAX_DARKNESS_LEVEL - light_points[(int(hitX/4), int(hitY/4))][0]
                darkness_surface.set_alpha(darkness_level)
                texture_surface = pygame.transform.scale(texture_surface, (column_width+1, height))
                texture_surface.blit(darkness_surface, darkness_surface.get_rect(topleft=(0,0)))

                # Drawing multiple floors at once
                y_onscreen = screen_height/2-(height/2) - (z/16) * height/2
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, y_onscreen, hitDist, height, texture_surface))

            
            i += 1

        # Sprite rendering
        max_possible_left = math.degrees(math.atan2(resolution//2, distance_from_projection)) / 2
        fov_as = math.degrees(math.atan2(int(resolution//2), distance_from_projection)) 
        for sprite in all_visible_sprites:
            sprite_x = sprite.x
            sprite_y = sprite.y
            sprite_z = sprite.z - 16
            direction_to_sprite = utilityfuncs.clamp_directionals(utilityfuncs.point_direction(x, y, sprite_x, sprite_y))
            angle_diff = utilityfuncs.polarize_dir(direction= - direction_to_sprite)#abs(direction - direction_to_sprite)
            rescale_factor = math.cos(math.radians(angle_diff))
            delta_dir = utilityfuncs.polarize_dir(direction_to_sprite - direction) / fov_as

            distance_to_sprite = utilityfuncs.point_distance(x, y, sprite_x, sprite_y) + 0.1
            dist = distance_to_sprite * fov_ratio + 0.1
            if distance_to_sprite > 16:
                sprite_x_onscreen = screen_width / 2 - delta_dir * (screen_width/2)
                # screen_x = (center_x) * (1 + math.tan(relative_angle) / math.tan(FOV / 2))
                # sprite_x_onscreen = screen_width/2 * (1 + math.tan(angle_diff) / math.tan(fov/2))
                
                sprite_height = RAYCAST_SIZE_SCALE / (dist/height_scale)
                sprite_height = min(sprite_height, MAX_SPRITE_SCALE)
                sprite_y_onscreen = screen_height/2-(sprite_height/2) * sprite.sprite_scale - (sprite_z/16) * (sprite_height/2) - (z/16) * (sprite_height/2)

                if sprite_y_onscreen + z + sprite_height - z_lookup > 0 and sprite_y_onscreen - z_lookup < settings.SCREEN_HEIGHT:
                    screen_elements_list.append(screen_elements.ScreenElement(
                        sprite_x_onscreen
                        , sprite_y_onscreen
                        , dist
                        , sprite_height
                        , sprite.get_texture()
                        , True
                        , center_sprite=True
                        , rescale_val=sprite.sprite_scale
                        , no_repeats=True
                        ))
                    
        screen_elements_list.sort(reverse=True)
        return screen_elements_list
