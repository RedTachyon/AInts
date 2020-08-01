from __future__ import annotations

import random
from typing import Sequence, List, Set, Tuple

import numpy as np

from utils import normalize, DIRECTIONS, Point, Action, Cell, Direction
import constants as c


class Observation:
    def __init__(self, world: World, ant: Ant):
        self.here = self.get_cell(world, ant.position)
        self.ahead, self.left, self.right = [self.get_cell(world, pos) for pos in ant.visible]
        self.visible = [self.ahead, self.left, self.right]

    def get_cell(self, world: World, position: Point):
        cell = Cell(
            home=bool(world.home[position]),
            home_pheromone=world.home_pheromone[position],
            food=world.food[position],
            food_pheromone=world.food_pheromone[position],
            ant=bool(world.ants_map[position])
        )
        return cell


class Ant:
    position: Point
    direction: Direction
    food: bool

    count: int = 0

    def __init__(self, position: Sequence[int], direction: Direction):
        self.direction = direction
        self.position = Point.new(*position)
        self.food = False

        self.id = Ant.count
        Ant.count += 1

        self.history = set()

    def select_action(self, obs: Observation):
        if self.food:
            # looking for home
            if obs.here.home:
                return Action.DROP
            elif obs.ahead.home:# and not obs.ahead.ant:
                return Action.MOVE
            else:
                return self.follow_trail(obs, home=True)
        else:
            # looking for food
            if obs.here.food and not obs.here.home:
                return Action.TAKE
            elif obs.ahead.food and not obs.ahead.home:# and not obs.ahead.ant
                return Action.MOVE
            else:
                return self.follow_trail(obs, home=False)

    def follow_trail(self, obs: Observation, home: bool = False):
        if home:
            ranking = [place.home + place.home_pheromone for place in obs.visible]
        else:
            ranking = [(1-place.home) * place.food + (1-place.home) * place.food_pheromone for place in obs.visible]

        best_idx = int(np.argmax(ranking))
        ranking[best_idx] *= 3  # TODO: magic number

        # ignore = 0 if obs.ahead.ant else None
        ignore = None
        probs = normalize(ranking, ignore)

        choice = np.random.choice(range(len(probs)), p=probs)

        return [Action.MOVE, Action.LEFT, Action.RIGHT][choice]

    @property
    def ahead(self) -> Point:
        # noinspection PyTypeChecker
        return self.position + DIRECTIONS[self.direction]

    @property
    def visible(self) -> List[Point]:
        # noinspection PyTypeChecker
        return [self.position + DIRECTIONS[self.direction],
                self.position + DIRECTIONS[(self.direction - 1) % 8],
                self.position + DIRECTIONS[(self.direction + 1) % 8]]

    def move(self):
        self.history.add(tuple(self.position))
        self.position += DIRECTIONS[self.direction]

    def turn(self, amount: int):
        self.direction = (self.direction + amount) % 8

    def drop(self):
        self.food = False
        self.history.clear()

    def take(self):
        self.food = True
        self.history.clear()

    def __str__(self):
        food = 'F' if self.food else 'N'
        return f"{self.id:02}{food} {self.position.x} {self.position.y} {self.direction}"

    def __repr__(self):
        return f"<{str(self)}>"


class World:
    def __init__(self, size: int):
        self.size = size
        self.shape = (size, size)

        self.home = np.zeros(self.shape)
        self.home_pheromone = np.zeros(self.shape)

        self.food = np.zeros(self.shape)
        self.food_pheromone = np.zeros(self.shape)

        self.ants_map = np.empty(self.shape, dtype=Ant)
        self.ants = []

        self.setup()

    def step(self):
        for ant in self.ants:
            obs = Observation(self, ant)
            action = ant.select_action(obs)

            if action == Action.MOVE:
                self.ants_map[ant.position] = None
                self.ants_map[ant.ahead] = ant
                ant.move()

            elif action == Action.LEFT:
                ant.turn(-1)

            elif action == Action.RIGHT:
                ant.turn(1)

            elif action == Action.DROP:
                if ant.food:
                    self.mark_trail(ant.history, home=True)
                    self.food[ant.position] += 1
                    ant.drop()
                    ant.turn(4)

            elif action == Action.TAKE:
                if self.food[ant.position] > 0:
                    self.mark_trail(ant.history, home=False)
                    ant.take()
                    self.food[ant.position] -= 1
                    ant.turn(4)

            else:
                raise ValueError(f"{action} is not a valid action")

        self.food_pheromone = np.where(self.food_pheromone > 1e-2, self.food_pheromone * c.EVAP_RATE, 0.)
        self.home_pheromone = np.where(self.home_pheromone > 1e-2, self.home_pheromone * c.EVAP_RATE, 0.)

    def mark_trail(self, history: Set[Tuple[int, int]], home: bool = False):
        for (i, j) in history:
            if home:
                self.home_pheromone[i, j] += 1
            else:
                self.food_pheromone[i, j] += 1

    def add_ant(self, ant: Ant):
        self.ants.append(ant)
        self.ants_map[ant.position] = ant

    def setup(self):
        for _ in range(c.FOOD_PLACES):
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            self.food[x, y] = c.FOOD_MAX

        for i in c.HOME_RANGE:
            for j in c.HOME_RANGE:
                ant = Ant([i, j], random.randint(0, 7))
                self.ants_map[i, j] = ant
                self.home[i, j] = 1
                self.ants.append(ant)
