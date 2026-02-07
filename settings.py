SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 360
cell_width = 32

def translate_coords(loc:tuple[float,float]) -> tuple[float, float]:
    return loc[0]/cell_width, loc[1]/cell_width

colors = {
    1 : (255, 255, 255),
    2 : (255, 0, 0),
    3 : (255, 0, 255),
    4 : (255, 255, 0)
}
