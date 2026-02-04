# Actors
import pygame
import textures

class WorldSprite:
    def __init__(self, x, y, width, height, texture: pygame.Surface):
        self.x:float = x
        self.y:float = y
        self.rect: pygame.Rect = pygame.Rect((self.x - width/2, self.y -  height/2, width, height))
        self.rect.center = (self.x, self.y)
        self.texture: pygame.Surface = texture

    def update(self):
        self.rect.center = (self.x, self.y)
    
    def get_texture(self) -> pygame.Surface:
        return self.texture