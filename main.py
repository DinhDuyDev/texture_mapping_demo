##### DEMO FOR TEXTURE MAPPING
import pygame
import player
import map
import textures
import psutil
import raycast
import numpy
import settings

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.SRCALPHA|pygame.SCALED|pygame.FULLSCREEN, vsync=1)
draw_dest = screen.copy()
floor_screen_matrix = numpy.random.uniform(0, 1, (int(settings.SCREEN_WIDTH//2), int(settings.SCREEN_HEIGHT//2), 3))
print(floor_screen_matrix.shape)
debug_font = pygame.sysfont.SysFont("Arial", 10, False)

clock = pygame.Clock()
GAME_FPS = 60

gameData = {
    "MAX_FPS" : -999,
    "MIN_FPS" : 999,
    "CUR_FPS" : 0
}

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
                    controller.resolution += 5
                elif event.key == pygame.K_DOWN:
                    controller.resolution -= 5
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
        draw_dest.blit(textures.doom_sky_texture_scaled, textures.doom_sky_texture_scaled.get_rect(topleft=(0,-160)))
        pygame.draw.rect(draw_dest, (100, 100, 100), (0, 180, 640, 640))

        controller.rendering(draw_dest, map_geometry, floor_screen_matrix)

        
        fps_counter = debug_font.render(str(clock.get_fps()), False, (255, 0, 0), (0, 255, 0))
        fps_rect = fps_counter.get_rect(topleft=(0,0))
        resolution_counter = debug_font.render(str(controller.resolution), False, (255, 0, 0), (0, 255, 0))
        resolution_rect = resolution_counter.get_rect(topleft=(0, 10))
        draw_dest.blit(fps_counter, fps_rect)
        draw_dest.blit(resolution_counter, resolution_rect)

        # memory used
        memory_amount = debug_font.render(f"Memory (mB) used: {str(psutil.Process().memory_info().rss / 1024 ** 2)[:6]}", False, (255, 255, 255))
        memory_rect = memory_amount.get_rect(topleft=(0, 20))
        draw_dest.blit(memory_amount, memory_rect)

        # raycast lookup length
        r_lookup_amount = debug_font.render(f"Raycast lookup length: {len(raycast.RAYCAST_LOOKUP_TABLE)}", False, (255, 255, 255))
        r_lookup_rect = r_lookup_amount.get_rect(topleft=(0, 30))
        draw_dest.blit(r_lookup_amount, r_lookup_rect)

        # fisheye lookup length
        f_lookup_amount = debug_font.render(f"Fisheye lookup length: {len(raycast.FISHEYE_CORRECTION_LOOKUP_TABLE)}", False, (255, 255, 255))
        f_lookup_rect = f_lookup_amount.get_rect(topleft=(0, 40))
        draw_dest.blit(f_lookup_amount, f_lookup_rect)

        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(GAME_FPS)

if __name__ == "__main__":
    game()