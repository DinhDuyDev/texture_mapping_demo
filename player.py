import pygame
import math
import settings
import utilityfuncs
import textures

EXTREME_RES = 1280 # benchmarking
MAX_RES = 640
DEFAULT_RES = 160
BETTER_RES = 320
MIN_RES = 80

# 16x16 resize
sprite_x, sprite_y = 8 * settings.cell_width, 3 * settings.cell_width
sprite_hitbox:pygame.Rect = pygame.Rect(sprite_x - 8, sprite_y - 8, 16, 16)
mobster_sprite = textures.mobster_texture
mobster_sprite_subsurface = textures.mobster_texture_subsurfaces
sprite_direction = 0

class Player:
    def __init__(self, x: int, y: int):
        self.x:int = x
        self.y:int = y
        self.resolution = MAX_RES
        self.direction = 0
        self.z_look = 0
    
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


        rotate_vector = (pygame.key.get_pressed()[pygame.K_a] - pygame.key.get_pressed()[pygame.K_d]) * 2
        self.direction += rotate_vector * 2
        
        if self.direction >= 360:
            self.direction = 0
        elif self.direction < 0:
            self.direction = 360

    def rendering(self, dest: pygame.Surface, map:list[list[int]]):
        w, h = dest.get_width(), dest.get_height()
        map_w, map_h = len(map[0]), len(map)

        # BETTER RAYCASTER
        fov = 100#90
        height_scale = 40
        __d = self.direction + fov/2
        column_width = w/self.resolution
        previous_height = 0

        for i in range(self.resolution):
            elements_found = [] # [( element_name: str, element_coords: [float, float], distance_to_element: float, subsurface_array )]
            item_found = []
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
            dist = round(utilityfuncs.point_distance(self.x, self.y, hitX, hitY))
            offset_ratio = math.cos(math.radians(__d - self.direction))
            height = (360 / (dist/height_scale)) / offset_ratio
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
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                texture_rect = texture_surface.get_rect(topleft=(i * column_width, h/2-height/2 + self.z_look))
                dest.blit(texture_surface, texture_rect)
            else:
                percentage_of_cube = (hitY - (int(hitY/settings.cell_width) * settings.cell_width)) / settings.cell_width
                texture_surface = s_texture_sub[int(percentage_of_cube * s_texture.width)]
                texture_surface = pygame.transform.scale(texture_surface, (column_width, height))
                texture_rect = texture_surface.get_rect(topleft=(i * column_width, h/2-height/2 + self.z_look))
                dest.blit(texture_surface, texture_rect)

            # for _ in _:
            # dir_to_sprite = utilityfuncs.point_direction(self.x, self.y, sprite_x, sprite_y)
            # if abs(dir_to_sprite - self.direction) < fov/2 + 20:
            #     distance_to_player = utilityfuncs.point_distance(self.x, self.y, sprite_x, sprite_y)
            #     height_of_sprite = (360 / (distance_to_player / height_scale)) / offset_ratio
            #     render_spr = pygame.transform.scale(mobster_sprite, (mobster_sprite.width * (height / mobster_sprite.width), height))
            #     x_onscreen = ((dir_to_sprite - (self.direction - fov/2)) / fov) * self.resolution
            #     render_rect = render_spr.get_rect(center=(x_onscreen, 180))
            #     dest.blit(render_spr, render_rect)

            
            # Drawing static sprites
            # 2D sprites like doors / railings would be welcomed here
            line_clipped = sprite_hitbox.clipline(self.x, self.y, hitX, hitY)
            if line_clipped:
                # Finding out the midpoint of the clipline
                clip_start, clip_end = line_clipped
                mid_x, mid_y = (clip_start[0] + clip_end[0]) / 2, (clip_start[1] + clip_end[1]) / 2
                distance_to_clippoint = utilityfuncs.point_distance(sprite_x, sprite_y, mid_x, mid_y)
                if distance_to_clippoint < 16:
                    # translate the distance into the plane that the sprite would be drawn on
                    angle_between_clip_and_sprite_plane = utilityfuncs.point_direction(sprite_x, sprite_y, mid_x, mid_y)
                    angle_cos = math.cos(math.radians(angle_between_clip_and_sprite_plane - (self.direction + 90)))
                    distance_to_contact = distance_to_clippoint * angle_cos
                    angle_sign = utilityfuncs.sign(utilityfuncs.point_direction(sprite_x, sprite_y, self.x, self.y) + 90 - utilityfuncs.point_direction(self.x, self.y, mid_x, mid_y))
                    contact_x = sprite_x + math.cos(math.radians(self.direction+90 * angle_sign)) * distance_to_contact
                    contact_y = sprite_y - math.sin(math.radians(self.direction+90 * angle_sign)) * distance_to_contact 

                    distance_to_sprite = utilityfuncs.point_distance(self.x, self.y, contact_x, contact_y)

                    # side coords
                    left_x, left_y = sprite_x + math.cos(math.radians(self.direction+90)) * 16, sprite_y - math.sin(math.radians(self.direction + 90)) * 16
                    # right_x, right_y = sprite_x + math.cos(math.radians(self.direction - 90)) * 8, sprite_y - math.sin(math.radians(self.direction - 90)) * 8
                    distance_from_left = utilityfuncs.point_distance(left_x, left_y, contact_x, contact_y)
                    distance_ratio = (distance_from_left / 32) * mobster_sprite.width

                    # angle to sprite
                    subsurface_to_be_drawn = mobster_sprite_subsurface[int(distance_ratio)]

                    elements_found.append(("sprite", (sprite_x, sprite_y), distance_to_sprite, subsurface_to_be_drawn))

            for element in elements_found:
                dist = element[2]
                subsurf = element[3]
                height_of_element = (360 / (dist/height_scale)) / offset_ratio
                scaled_surf = pygame.transform.scale(subsurf, (column_width, height_of_element))
                scaled_rect = scaled_surf.get_rect(topleft=(i * column_width, h/2 - height_of_element/2 + self.z_look))
                dest.blit(scaled_surf, scaled_rect)
                # pygame.draw.rect(dest, (255, 0, 0), (i * column_width, h/2 - height_of_element/2, column_width, height_of_element))

            __d -= fov/self.resolution