from collections import namedtuple
from enum import Enum
from typing import List, Optional, NamedTuple

import numpy as np

import constants as c

TAU = 2 * np.pi


def normalize(vec: List[float], ignore: Optional[int] = None) -> List[float]:
    if ignore is None:
        total = sum(vec)
        n = len(vec)
        if total == 0:
            out = [1. / n for _ in vec]
        else:
            out = [v / total for v in vec]
    else:
        total = sum([v for i, v in enumerate(vec) if i != ignore])
        n = len(vec) - 1
        if total == 0:
            out = [1. / n for _ in vec]
        else:
            out = [v / total for v in vec]
        out[ignore] = 0.

    return out


def rotation(theta: float) -> np.ndarray:
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, s],
        [-s, c]
    ])


class Point(namedtuple("Point", ["x", "y"])):
    def __add__(self, other):
        return Point.new(self.x + other.x, self.y + other.y)

    @staticmethod
    def new(x, y):
        # This ensures that the point stays within bounds by wrapping it around as a torus
        return Point(x % c.DIMENSIONS, y % c.DIMENSIONS)


DIRECTIONS: List[Point] = [
    Point(-1, 0),  # N
    Point(-1, 1),  # NE
    Point(0, 1),  # E
    Point(1, 1),  # SE
    Point(1, 0),  # S
    Point(1, -1),  # SW
    Point(0, -1),  # W
    Point(-1, -1),  # NW
]


class Action(Enum):
    MOVE = 0
    LEFT = 1
    RIGHT = 2
    DROP = 3
    TAKE = 4


class Cell(NamedTuple):
    home: bool
    home_pheromone: float
    food: int
    food_pheromone: float
    ant: bool


Direction = int
