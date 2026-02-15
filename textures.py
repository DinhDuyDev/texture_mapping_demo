import pygame
pygame.init()

screen = pygame.display.set_mode((1,1), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE, vsync=1)

brick_texture = pygame.image.load("sprites/brick_texture.png").convert()
brick_texture_subsurfaces = [ brick_texture.subsurface(i, 0, 1, brick_texture.height) for i in range(brick_texture.width) ]
fun_texture = pygame.image.load("sprites/dontbedead.png").convert()
fun_texture_subsurfaces = [ fun_texture.subsurface(i, 0, 1, fun_texture.height) for i in range(fun_texture.width) ]
stone_texture = pygame.image.load("sprites/stone_flat_slab.jpeg").convert()
stone_texture_subsurfaces = [ stone_texture.subsurface(i, 0, 1, stone_texture.height) for i in range(stone_texture.width) ]
dirty_brick_texture = pygame.image.load("sprites/dirty_brick.png").convert()
dirty_brick_texture_subsurfaces = [ dirty_brick_texture.subsurface(i, 0, 1, dirty_brick_texture.height) for i in range(dirty_brick_texture.width) ]
doom_sky_texture = pygame.image.load("sprites/doom_sky.webp").convert()
doom_sky_texture_scaled = pygame.transform.scale(doom_sky_texture, (640, 360))
gore_head_texture = pygame.image.load("sprites/romero_head.png").convert()

mobster_texture = pygame.image.load("sprites/mobster.png").convert_alpha()
mobster_texture_subsurfaces = [ mobster_texture.subsurface(i, 0, 1, mobster_texture.height) for i in range(mobster_texture.width) ]

fireball_texture = pygame.image.load("sprites/fireball.png").convert_alpha()

quick_access_texture = {
    1: (brick_texture, brick_texture_subsurfaces),
    2: (fun_texture, fun_texture_subsurfaces),
    3: (stone_texture, stone_texture_subsurfaces),
    4: (dirty_brick_texture, dirty_brick_texture_subsurfaces),
}
pygame.display.quit()