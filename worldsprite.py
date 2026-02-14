import pygame
import map
import settings
import deleter

class WorldSprite:
    all_sprites:list[WorldSprite] = []
    def __init__(self, x, y, width, height, texture: pygame.Surface):
        self.x:float = x
        self.y:float = y
        self.rect: pygame.Rect = pygame.Rect((self.x - width/2, self.y -  height/2, width, height))
        self.rect.center = (self.x, self.y)
        self.texture: pygame.Surface = texture
        self.current_sprite_block:SpriteBlock = sprite_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)]
        self.owner = None
        self.all_sprites.append(self)

    def update(self):
        self.rect.center = (self.x, self.y)
        # changing sprite blocks and removing itself from any blocks not seen
        if sprite_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)] != self.current_sprite_block:
            self.current_sprite_block.contained_sprites.discard(self)
            self.current_sprite_block = sprite_blockmap[int(self.y / settings.cell_width)][int(self.x / settings.cell_width)]
        if self not in self.current_sprite_block.contained_sprites:
            self.current_sprite_block.contained_sprites.add(self)
        
        if pygame.key.get_pressed()[pygame.K_0]:
            self.destroy()
        if pygame.key.get_pressed()[pygame.K_q]:
            self.x += 1
            self.y += 1

    def get_texture(self) -> pygame.Surface:
        return self.texture
    
    def destroy(self):
        deleter.Deleter.request_delete(self, self.current_sprite_block.contained_sprites)
        deleter.Deleter.request_delete(self, WorldSprite.all_sprites)
    
class SpriteBlock:
    def __init__(self):
        self.contained_sprites:set[WorldSprite] = set()

# Sprites blockmap to optimize sprite rendering.
sprite_blockmap = [
    [SpriteBlock() for i in range(len(map.game_map[0]))] for j in range(len(map.game_map))
]