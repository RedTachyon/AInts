from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib import animation

from core import Ant, World
import constants as c
from visualize import show_picture
from tqdm import trange, tqdm

ITERS = 10000

world = World(c.DIMENSIONS)


fig, ax = plt.subplots()
pbar = tqdm(total=ITERS)

# animation function.  This is called sequentially
def animate(i):
    ax.cla()
    img = show_picture(world)
    world.step()

    pbar.update(1)
    im = ax.imshow(img)
    return im,


anim = animation.FuncAnimation(fig, animate,
                               frames=ITERS, interval=20, blit=True)

anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

plt.show()