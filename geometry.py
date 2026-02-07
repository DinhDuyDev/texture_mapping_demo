import settings
import utilityfuncs
class PushWall:
    def __init__(self, x: int, y: int, map_to_modify: list[list[int]]):
        self.x:int = x
        self.y:int = y
        self.map_to_modify:list[list[int]] = map_to_modify
        self.texture_index:int = map_to_modify[y][x]
        self.is_pushed = False
        self.finished_pushing = False
        self.z_height = 0
    
    def update(self):
        if self.is_pushed and (not self.finished_pushing):
            self.z_height -= 1
            if self.z_height <= -32:
                self.finished_pushing = True