##### DEMO FOR TEXTURE MAPPING
import pygame
import actor
import worldmap
import psutil
import settings
import textures
import worldsprite
import deleter
import render
import actor
import random

pygame.init()
pygame.font.init()

# setup
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.SRCALPHA|pygame.SCALED|pygame.FULLSCREEN, vsync=1)
draw_dest = screen.copy()
debug_font = pygame.sysfont.SysFont("Arial", 10, False)

pygame.mouse.set_visible(False)

clock = pygame.Clock()
GAME_FPS = 60

gameData = {
    "MAX_FPS" : -999,
    "MIN_FPS" : 999,
    "CUR_FPS" : 0,
    "DEBUG_MODE" : True
}

player_obj = actor.Player(48, 48)

# All sprites
# for i in range(100):
    # worldsprite.WorldSprite(8 * settings.cell_width + random.randrange(-32, 32), 3 * settings.cell_width + random.randrange(-32, 32), 16, 32, 32, textures.mobster_texture, sprite_scale=0.2)

# Map geometry
map_geometry = worldmap.game_map
worldsprite.WorldSprite(160, 160, 16, 12, 12, textures.lamp_texture, 1)

# game
def game():
    running = True
    while running:
        # Game loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    player_obj.resolution += 5
                elif event.key == pygame.K_DOWN:
                    player_obj.resolution -= 5
            elif event.type == pygame.QUIT:
                running = False
        
        # FPS counter
        current_fps = clock.get_fps()
        if gameData["MIN_FPS"] > current_fps and current_fps > 10:
            gameData["MIN_FPS"] = current_fps
        if gameData["MAX_FPS"] < current_fps:
            gameData["MAX_FPS"] = current_fps

        # Player movement
        player_obj.movement(map_geometry)

        # Game logic - Actors and NPCs
        for at in actor.Actor.all_enemies:
            at.update()

        for at in actor.Actor.all_projectiles:
            at.update()

        # Display
        draw_dest.fill((0, 0, 0))
        player_obj.rendering(draw_dest, map_geometry) # drawing
        for spr in worldsprite.WorldSprite.all_sprites:
            spr.update()

        # all light points
        for coords in render.light_points:
            c = max(coords[0], 25)
            pygame.draw.rect(draw_dest, (c, c, c), (coords[0]-1, coords[1]-1, 2, 2))

        if gameData["DEBUG_MODE"]:
            # fps
            fps_counter = debug_font.render(str(current_fps), False, (255, 0, 0), (0, 255, 0))
            fps_rect = fps_counter.get_rect(topleft=(0,0))
            resolution_counter = debug_font.render(str(player_obj.resolution), False, (255, 0, 0), (0, 255, 0))
            resolution_rect = resolution_counter.get_rect(topleft=(0, 10))
            draw_dest.blit(fps_counter, fps_rect)
            draw_dest.blit(resolution_counter, resolution_rect)

            # memory used
            memory_amount = debug_font.render(f"Memory (mB) used: {str(psutil.Process().memory_info().rss / 1024 ** 2)[:6]}", False, (255, 255, 255))
            memory_rect = memory_amount.get_rect(topleft=(0, 20))
            draw_dest.blit(memory_amount, memory_rect)

            # fisheye lookup length
            max_fps_display = debug_font.render(f"MAX_FPS: {gameData["MAX_FPS"]}", False, (255, 255, 255))
            min_fps_display = debug_font.render(f"MIN_FPS: {gameData["MIN_FPS"]}", False, (255, 255, 255))
            max_fps_rect = max_fps_display.get_rect(topleft=(0, 30))
            min_fps_rect = min_fps_display.get_rect(topleft=(0, 40))
            draw_dest.blit(max_fps_display, max_fps_rect)
            draw_dest.blit(min_fps_display, min_fps_rect)

            # all sprites on screen
            sprites_rendered = debug_font.render(f"Sprites rendered: {len(worldsprite.WorldSprite.all_sprites)}", False, (255, 255, 255))
            draw_dest.blit(sprites_rendered, sprites_rendered.get_rect(topleft=(0,50)))


        # UI
        pygame.draw.circle(draw_dest, (255, 0, 0), (settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2), radius=5, width=1)

        # deleting
        deleter.Deleter.delete_all_requests()

        screen.blit(pygame.transform.scale(draw_dest, (screen.get_width(), screen.get_height())), (0, 0))

        pygame.display.flip()
        clock.tick(GAME_FPS)

if __name__ == "__main__":
    game()

    # print out every sprite present in the block map
    for row in worldsprite.sprite_blockmap:
        for block in row:
            if block.contained_sprites:
                print(block.contained_sprites)

    # print out every light points
    print(int(player_obj.x), int(player_obj.y))