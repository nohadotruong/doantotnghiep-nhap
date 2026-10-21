import math

def calc_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]

    x2 = p2[0]
    y2 = p2[1]

    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)