from copy import deepcopy
from enum import Enum

import numpy as np
from PIL import Image


class direction(Enum):
    LEFT = 0
    RIGHT = 0
    UP = 0
    DOWN = 0


def wfc_pre_process_image(input_image: Image, tile_size: int) -> list:
    tiles = []
    tiles_all = []

    data = np.asarray(input_image)
    for x in range(input_image.size[0]):
        for y in range(input_image.size[1]):
            arr = []
            for xx in range(tile_size):
                sub_arr = []
                for yy in range(tile_size):
                    sub_arr.append(
                        data[(x + xx) % input_image.size[0]][
                            (y + yy) % input_image.size[1]
                        ]
                    )
                arr.append(sub_arr)
            tiles.append(np.asarray(arr))

    # print("normal: ", len(tiles))

    for tile in tiles:
        flipped_tile = np.fliplr(tile)

        rotated = tile
        rotated_flipped = flipped_tile

        normal_rotations = [tile]
        flipped_rotations = [flipped_tile]

        for _ in range(3):
            rotated = np.rot90(rotated)
            normal_rotations.append(rotated)

            rotated_flipped = np.rot90(rotated_flipped)
            flipped_rotations.append(rotated_flipped)

        tiles_all += normal_rotations + flipped_rotations

    # print("normal, flipped, rotated normal, rotated flipped: ", len(tiles_all))

    hash_to_tile = {}
    tile_hash_to_frequencies = {}
    tile_frequencies = {}
    tile_top_left = {}
    unique_tiles = {}

    for tile in tiles_all:
        _hash = hash(tuple(map(tuple, np.vstack(deepcopy(tile).T))))
        hash_to_tile[_hash] = deepcopy(tile)

        if _hash not in tile_hash_to_frequencies:
            tile_hash_to_frequencies[_hash] = 1
        else:
            tile_hash_to_frequencies[_hash] += 1

    for i, tup in enumerate(hash_to_tile.items()):
        _hash, tile = tup
        unique_tiles[i] = tile
        tile_frequencies[i] = tile_hash_to_frequencies[_hash]
        tile_top_left[i] = tile[0][0]

    # print(unique_tiles)

    adjacency_rules = []
    for i, i_tile in unique_tiles.items():
        for j, j_tile in unique_tiles.items():
            for d in [direction.LEFT, direction.RIGHT, direction.UP, direction.DOWN]:
                if compatible(i_tile, j_tile, d):
                    adjacency_rules.append((i, j, d))

    return unique_tiles, adjacency_rules, tile_frequencies, tile_top_left


def are_arrays_equal(arr1, arr2):
    return np.array_equal(arr1, arr2)


def compatible(tile_one, tile_two, _direction):
    match _direction:
        case direction.LEFT:
            tile_one_left = [[row[:2] for row in layer] for layer in tile_one]
            tile_two_right = [[row[-2:] for row in layer] for layer in tile_two]
            return are_arrays_equal(tile_one_left, tile_two_right)

        case direction.RIGHT:
            tile_one_right = [[row[-2:] for row in layer] for layer in tile_one]
            tile_two_left = [[row[:2] for row in layer] for layer in tile_two]
            return are_arrays_equal(tile_one_right, tile_two_left)

        case direction.UP:
            tile_one_up = [layer[:2] for layer in tile_one]
            tile_two_down = [layer[-2:] for layer in tile_two]
            return are_arrays_equal(tile_one_up, tile_two_down)

        case direction.DOWN:
            tile_one_down = [layer[-2:] for layer in tile_one]
            tile_two_up = [layer[:2] for layer in tile_two]
            return are_arrays_equal(tile_one_down, tile_two_up)
