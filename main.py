from collections import Counter
import random
import string
import numpy as np
from PIL import Image

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
                    sub_arr.append(data[(x + xx) % input_image.size[0]][(y + yy)  % input_image.size[1]])
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
    frequencies = []

    for tile in tiles_all:
        _hash = hash(tuple(map(tuple, np.vstack(tile.T))))
        hash_to_tile[_hash] = tile

        if _hash not in tile_hash_to_frequencies:
            tile_hash_to_frequencies[_hash] = 1
        else:
            tile_hash_to_frequencies[_hash] += 1

    for _hash, tile in hash_to_tile.items():
        frequencies.append((tile, tile_hash_to_frequencies[_hash]))

    return tiles_all, tile_hash_to_frequencies



with Image.open("tile.png") as im:
    im.load()
    tiles = wfc_pre_process_image(im, 3)
    for im in tiles:
        imm = Image.fromarray(im)
        imm.save("images/" + ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) + ".png")
