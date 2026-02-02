##### DEMO FOR TEXTURE MAPPING
import pygame
import player
import map
import math
import settings
import textures
import utilityfuncs

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 360), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.SRCALPHA, vsync=1)
draw_dest = screen.copy()

debug_font = pygame.sysfont.SysFont("Arial", 10, False)

clock = pygame.Clock()
GAME_FPS = 60

controller = player.Player(48, 48)
map_geometry = map.game_map

def game():
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    # controller.resolution += 5
                    controller.z_look += 20
                elif event.key == pygame.K_DOWN:
                    # controller.resolution -= 5
                    controller.z_look -= 20
                elif event.key == pygame.K_RETURN:
                    if controller.resolution == player.MAX_RES:
                        controller.resolution = player.EXTREME_RES
                    else:
                        controller.resolution = player.MAX_RES
            elif event.type == pygame.QUIT:
                running = False
        
        controller.movement(map_geometry)

        draw_dest.fill((0,0,0))

        # Drawing the skybox
        draw_dest.blit(textures.doom_sky_texture_scaled, textures.doom_sky_texture_scaled.get_rect(topleft=(0,-160 + controller.z_look)))
        pygame.draw.rect(draw_dest, (100, 100, 100), (0, 180+controller.z_look, 640, 640))

        controller.rendering(draw_dest, map_geometry)
        # player.sprite_y -= 0.001
        # player.sprite_hitbox.y -= 0.001
        
        fps_counter = debug_font.render(str(clock.get_fps()), False, (255, 0, 0), (0, 255, 0))
        fps_rect = fps_counter.get_rect(topleft=(0,0))
        resolution_counter = debug_font.render(str(controller.resolution), False, (255, 0, 0), (0, 255, 0))
        resolution_rect = resolution_counter.get_rect(topleft=(0, 10))
        draw_dest.blit(fps_counter, fps_rect)
        draw_dest.blit(resolution_counter, resolution_rect)

        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(GAME_FPS)

if __name__ == "__main__":
    game()
    utilityfuncs.utilityfuncs()