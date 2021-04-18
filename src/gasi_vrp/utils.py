import math
import random
from location import Location

def euclidean_distance(locA: Location, locB: Location) -> float:
    a_x, a_y = locA.coords
    b_x, b_y = locB.coords

    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)

def random_pairs(iterative):
    n = len(iterative)
    random.shuffle(iterative)
    for i in range(0, n, 2):
        yield (iterative[i], iterative[i+1])


def cut_points(lst, cnt):
    return tuple(sorted(random.sample(range(len(lst)), cnt)))