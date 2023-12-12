import numpy as np
from PIL import Image


def wfc_post_process_image(tile_index_grid, top_left_pixel_of_each_tile):
    grid = []
    for x in range(len(tile_index_grid)):
        grid[x] = []
        for y in range(len(tile_index_grid[x])):
            grid[x].append(top_left_pixel_of_each_tile[tile_index_grid[x][y]])

    return Image.fromarray(np.array(grid))
