"""
 Pygame base template for opening a window

 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/

 Explanation video: http://youtu.be/vRB_983kUMc
"""
from typing import List, Tuple

import pygame
from pygame import Surface
from core import World, Ant
import numpy as np
import constants as c
from utils import rotation, TAU


def draw_arrow(surface: Surface,
               color: Tuple[int, int, int],
               start: List[int],
               end: List[int],
               width: int = 1):
    start, end = np.array(start), np.array(end)

    vec = start - end
    length = np.linalg.norm(vec)
    vec = vec / length

    [v1, v2] = vec

    orthogonal = np.array([-v2, v1])

    left_end = end + (vec + orthogonal) * 0.25 * c.C2P
    right_end = end + (vec - orthogonal) * 0.25 * c.C2P

    pygame.draw.line(surface, color, start.tolist(), end.tolist(), width=width)
    pygame.draw.line(surface, color, left_end.tolist(), end.tolist(), width=width)
    pygame.draw.line(surface, color, right_end.tolist(), end.tolist(), width=width)


def draw_ant(ant: Ant, surface: Surface):
    y, x = ant.position
    pos = (np.array([x, y]) + 0.5) * c.C2P
    rot = rotation(-ant.direction * TAU / 8)
    start = (rot @ np.array([0., -c.C2P / 3]) + pos).astype(int)
    end = (rot @ np.array([0., c.C2P / 3]) + pos).astype(int)

    color = (255, 0, 0) if ant.food else (0, 0, 0)

    # pygame.draw.line(surface, color, start.tolist(), end.tolist(), width=1)
    draw_arrow(surface, color, end.tolist(), start.tolist(), width=1)


def draw_world(world: World, surface: Surface):
    for i in range(world.size):
        for j in range(world.size):
            if (food := world.food[i, j]) > 0:
                value = food / c.FOOD_MAX
                color = [1, 1 - value, 1 - value]
            elif world.home[i, j]:
                color = [1, 1, 1]
            elif (food_pheromone := world.food_pheromone[i, j]) > 0:
                value = food_pheromone / c.PHEROMONE_SCALE
                color = [1 - value, 1 - value, 1]
            elif (home_pheromone := world.home_pheromone[i, j]) > 0:
                value = home_pheromone / c.PHEROMONE_SCALE
                color = [1 - value, 1, 1 - value]
            else:
                color = [1, 1, 1]

            color = [int(v * 255) for v in color]
            color = np.clip(color, 0, 255).astype(int).tolist()

            pygame.draw.rect(surface, color, [j * c.C2P, i * c.C2P, c.C2P, c.C2P])

    pygame.draw.rect(surface,
                     BLACK,
                     [c.HOME_START * c.C2P, c.HOME_START * c.C2P, c.NANTS_SQRT * c.C2P, c.NANTS_SQRT * c.C2P],
                     width=2)

    for ant in world.ants:
        draw_ant(ant, surface)


world = World(c.DIMENSIONS)
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()

# Set the width and height of the screen [width, height]
size = (c.RESOLUTION, c.RESOLUTION)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("AInts")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

pause = True
step = False
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            pause = not pause
        if event.type == pygame.MOUSEBUTTONDOWN:
            step = True

    if not pause or step:
        world.step()
        step = False

    screen.fill(WHITE)

    # --- Drawing code should go here
    draw_world(world, screen)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
