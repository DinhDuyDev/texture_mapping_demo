import pygame

class ScreenElement:
    def __init__(self, x_pos : float # horizontal position on screen
                 , y_pos: float # horizontal position on screen
                 , distance_to_observer # distance to observer to sort
                 , height # height of the strip -> scaling
                 , surface_to_render : pygame.Surface # what surface to render
                 , explicit_scaling = False
                 , center_sprite = False
                 ):
        self.x = x_pos
        self.y = y_pos
        self.dist_to_observer = distance_to_observer
        self.height = height
        self.height_ratio = self.height / surface_to_render.height
        self.width = surface_to_render.width * self.height_ratio if explicit_scaling else surface_to_render.width
        self.center = center_sprite
        self.surface_to_render: pygame.Surface = pygame.transform.scale(surface_to_render, (self.width, self.height))

    
    def surface_and_rect(self) -> tuple[pygame.Surface, pygame.Rect]:
        # Rect scaling
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.center:
            rect.center = (self.x, self.y + self.height/2)
        return (self.surface_to_render, rect)
    
    # def add_to_surf(self) -> tuple[pygame.Surface, pygame.Rect]:

    def __lt__(self, other:ScreenElement):
        if not isinstance(other, ScreenElement):
            return False
        return self.dist_to_observer < other.dist_to_observer
    
    def __gt__(self, other:ScreenElement):
        if not isinstance(other, ScreenElement):
            return False
        return self.dist_to_observer > other.dist_to_observer

    def __eq__(self, other:ScreenElement):
        if not isinstance(other, ScreenElement):
            return False
        return self.dist_to_observer == other.dist_to_observer