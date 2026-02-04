import pygame
import math
import settings
import utilityfuncs
import textures
import screen_elements
import actors

EXTREME_RES = 1280 # benchmarking
MAX_RES = 640
DEFAULT_RES = 160
BETTER_RES = 320
MIN_RES = 80
RAYCAST_SIZE_SCALE = 320 # 360


# 16x16 resize
# sprite_x, sprite_y = 8 * settings.cell_width, 3 * settings.cell_width
# sprite_hitbox:pygame.Rect = pygame.Rect(sprite_x - 16, sprite_y - 16, 32, 32)
mobster_sprite = textures.mobster_texture
# mobster_sprite_subsurface = textures.mobster_texture_subsurfaces
# sprite_direction = 0

all_sprites:list[actors.WorldSprite] = [
    actors.WorldSprite(8 * settings.cell_width, 4 * settings.cell_width, 32, 32, mobster_sprite),
    actors.WorldSprite(14 * settings.cell_width, 1.5 * settings.cell_width, 32, 32, mobster_sprite),
    # actors.WorldSprite(8 * settings.cell_width, 3 * settings.cell_width, 32, 32),
    # actors.WorldSprite(8 * settings.cell_width, 3 * settings.cell_width, 32, 32)
]
# upds

lightsource = (8 * settings.cell_width, 3 * settings.cell_width)
light_radius = 192

class Player:
    def __init__(self, x: int, y: int):
        self.x:int = x
        self.y:int = y
        self.resolution = MAX_RES
        self.direction = 0
        self.offset = 0
    
    def movement(self, map:list[list[int]]):
        direction_to_me = utilityfuncs.point_direction(all_sprites[0].x, all_sprites[0].y, self.x, self.y)
        all_sprites[0].x += math.cos(math.radians(math.radians(direction_to_me))) #* 4
        all_sprites[0].y -= math.sin(math.radians(math.radians(direction_to_me))) #* 4
        all_sprites[0].update()

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
                # texture_rect = pygame.Rect(i * column_width, h/2-height/2, column_width, height)
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, h/2-height/2, dist, height, texture_surface))
                # dest.blit(texture_surface, texture_rect)
                
            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                height = min(1280, height)
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                # texture_rect = pygame.Rect(i * column_width, h/2-height/2, column_width, height)
                screen_elements_list.append(screen_elements.ScreenElement(i * column_width, h/2-height/2, dist, height, texture_surface))
                
                # dest.blit(texture_surface, texture_rect)

            # if abs(__d - self.direction + fov/2) < 2 or abs(__d - self.direction - fov/2) < 2:
            #     pygame.draw.line(dest, (255, 0, 255), (self.x/2, self.y/2), (hitX/2, hitY/2))

            # This is accurate, but too slow. I thought this was good, but it's not good enough.
            # for asdf in range(10):
            # is_in_fov = abs(utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y) - self.direction) < fov/2 + 20
            # line_clipped = sprite_hitbox.clipline(self.x, self.y, hitX, hitY)
            # sprite_bound_distance = abs(utilityfuncs.dist_to_line((sprite_x, sprite_y), (self.x, self.y), (hitX, hitY)))
            # if sprite_bound_distance < 16 and line_clipped: #and is_in_fov:
            #     # angle left / right ==> +90 is the left side
            #     angle_side = utilityfuncs.side_of_line((self.x, self.y), (hitX, hitY), (sprite_x, sprite_y))#utilityfuncs.sign(utilityfuncs.point_direction(self.x, self.y, hitX, hitY) - direction_to_sprite)
            #     left_x = sprite_x + math.cos(math.radians(self.direction + 90)) * 16
            #     left_y = sprite_y - math.sin(math.radians(self.direction + 90)) * 16
            #     right_x = sprite_x + math.cos(math.radians(self.direction - 90)) * 16
            #     right_y = sprite_y - math.sin(math.radians(self.direction - 90)) * 16
            #     contact_x = sprite_x + math.cos(math.radians(self.direction + 90 * angle_side)) * sprite_bound_distance
            #     contact_y = sprite_y - math.sin(math.radians(self.direction + 90 * angle_side)) * sprite_bound_distance
            #     distance_to_sprite = utilityfuncs.point_distance(self.x, self.y, sprite_x, sprite_y)
            #     distance_from_left = utilityfuncs.point_distance(contact_x, contact_y, left_x, left_y)
            #     distance_ratio = (distance_from_left / 32) * mobster_sprite.width
            #     subsurface_to_be_drawn = mobster_sprite_subsurface[int(distance_ratio)]
            #     elements_found.append(("sprite", (sprite_x, sprite_y), distance_to_sprite, subsurface_to_be_drawn))

            # for element in elements_found:
            #     dist = element[2]
            #     subsurf = element[3]
            #     height_of_element = min(720, (RAYCAST_SIZE_SCALE / (dist/height_scale)) / offset_ratio)
            #     scaled_surf = pygame.transform.scale(subsurf, (column_width, height_of_element))
            #     scaled_rect = scaled_surf.get_rect(topleft=(i * column_width, h/2 - height_of_element/2))
            #     dest.blit(scaled_surf, scaled_rect)

            # Better system required:
            #   - Calculate sprite position.
            #   - Check grid-by-grid, only render if sprite is in a grid that has passed checking.
            #   - Scale the sprite, and find out if any part of the sprite overlaps with that of wall. If distance to the wall is greater than to the sprite,
            #   - Create some sort of overworld sprite object => add grids to the game. Check each sprites' position.
            #   - Do system design to facilitate multiple sprites at once.
            # then render the sprite.
            __d -= fov/self.resolution

        # Sprite rendering
        for sprite in all_sprites:
            sprite_x = sprite.x
            sprite_y = sprite.y
            direction_to_sprite = utilityfuncs.clamp_directionals(utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y)) #utilityfuncs.clamp_directionals(self.direction - utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y))
            left_direction = utilityfuncs.clamp_directionals(self.direction + (fov/2))
            delta_dir = utilityfuncs.clamp_directionals(left_direction - direction_to_sprite) / (fov)
            sprite_x_onscreen = delta_dir * w
            distance_to_sprite = utilityfuncs.point_distance(self.x, self.y, sprite_x, sprite_y)
            sprite_height = (RAYCAST_SIZE_SCALE / (distance_to_sprite/height_scale))
            sprite_height = min(sprite_height, 1280)
            screen_elements_list.append(screen_elements.ScreenElement(sprite_x_onscreen, h/2-sprite_height/2, distance_to_sprite, sprite_height, sprite.get_texture(), True, center_sprite=True))

            screen_elements_list.sort(reverse=True)
            for scr_element in screen_elements_list:
                render_data = scr_element.surface_and_rect()
                dest.blit(render_data[0], render_data[1])

        # for i in range(self.resolution):
        #     wall_information = wall_data[i]
        #     texture_rect = pygame.Rect(i * column_width, h/2-wall_information[0]/2, column_width, wall_information[0])
        #     dest.blit(wall_information[1], texture_rect)