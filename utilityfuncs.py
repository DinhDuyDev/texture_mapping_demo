# Utility functions
import math
def point_direction(x1:float, y1:float, x2:float, y2:float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    deg = math.atan2(-dy, dx)
    return math.degrees(deg)

def point_distance(x1:float, y1:float, x2:float, y2:float) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
def square_distance(x1:float, y1:float, x2:float, y2:float) -> float:
    return (x2 - x1) ** 2 + (y2 - y1) ** 2
def sign(x : float) -> int:#int[-1, 0, 1]:
    if x == 0:
        return 0
    return int(x / abs(x))

def normalize(a : list[float]) -> list[float]:
    vecl = point_distance(0, 0, a[0], a[1])
    return [a[0] / vecl, a[1]/vecl]

def vec_length(a: list[float]|tuple[float,float]) -> float:
    sum = 0
    for element in a:
        sum += element ** 2
    return sum ** 1/len(a)

# Credit: written by Sebastian Lague: https://www.youtube.com/watch?v=KHuI9bXZS74
def dist_to_line(point:tuple[float,float], startLine:tuple[float,float], endLine:tuple[float,float]) -> float:
    if square_distance(startLine[0], startLine[1], endLine[0], endLine[1]) == 0:
        return point_distance(point[0], point[1], startLine[0], startLine[1])
    numerator = abs((point[0] - startLine[0]) * (-endLine[1] + startLine[1]) + (point[1] - startLine[1]) * (endLine[0] - startLine[0]))
    denominator = math.sqrt((-endLine[1] + endLine[1]) ** 2 + (endLine[0] - startLine[0]) ** 2)
    if denominator == 0:
        return 0
    return numerator / denominator

# Credit: written by Sebastian Lague: https://github.com/SebLague/Gamedev-Maths/blob/master/DistanceToLine.cs
def side_of_line(a:tuple[float,float], b:tuple[float,float], c:tuple[float,float]):
    return sign((c[0] - a[0]) * (-b[1] + a[1]) + (c[1] - a[1]) * (b[0] - a[0]))

def clamp_directionals(direction: float):
    if direction == 360:
        return 0
    while not (0 <= direction < 360):
        if direction >= 360:
            direction -= 360
        elif direction < 0:
            direction += 360
    return direction
    
# I'm so lonely
def utilityfuncs():
    print("Thank you for using utility funcs :)")


utilityfuncs()