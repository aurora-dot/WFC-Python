import numpy as np
from PIL import Image

def wfc_pre_process_image(input_image: Image, tile_size: int) -> list:
    tiles = []
    data = np.asarray(input_image)
    for x in range(input_image.size[0]):
        for y in range(input_image.size[1]):
            print("top left position: ", x, y)

            arr = []
            for xx in range(tile_size):
                sub_arr = []
                for yy in range(tile_size):
                    sub_arr.append(data[(x + xx) % input_image.size[0]][(y + yy)  % input_image.size[1]])
                arr.append(sub_arr)
                        
            tiles.append(np.asarray(arr))
    
    print(len(tiles))
    for im in tiles:
        print('---')
        print(im)
        imm = Image.fromarray(im)
        imm.show()
    pass

with Image.open("tile.png") as im:
    im.load()
    wfc_pre_process_image(im, 3)
