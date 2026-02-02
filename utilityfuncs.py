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

def dist_to_line(point:tuple[float,float], startLine:tuple[float,float], endLine:tuple[float,float]) -> float:
    AB_vec = (endLine[0] - startLine[0], endLine[1] - startLine[1])
    perpendicular_vec = (-AB_vec[1], AB_vec[0])
    AC_vec = (point[0] - startLine[0], point[1] - startLine[1])
    distance = (AC_vec[0] * perpendicular_vec[0] + AC_vec[1] * perpendicular_vec[1]) / vec_length(perpendicular_vec)
    return distance

def rangify_directionals(direction: float):
    if direction == 360:
        return 0
    while not (0 <= direction < 360):
        if direction > 360:
            direction -= 360
        elif direction < 0:
            direction += 360
    return direction
def utilityfuncs():
    print("Thank you for using utility funcs :)")
