from PIL import Image

from wfc.core import wfc_core
from wfc.postprocess import wfc_post_process_image
from wfc.preprocess import wfc_pre_process_image


def wfc_image(image: Image, tile_size: int, output_size: (int, int)) -> Image:
    (
        unique_tiles,
        adjacency_rules,
        frequency_hints,
        top_left_pixel_of_each_tile,
    ) = wfc_pre_process_image(image, tile_size)
    tile_index_grid = wfc_core(adjacency_rules, frequency_hints, output_size)
    return wfc_post_process_image(tile_index_grid, top_left_pixel_of_each_tile)


def main():
    print("running...")
    with Image.open("tile.png") as im:
        im.load()
        wfc_image(im, 3, (300, 300))
    print("done!")


if __name__ == "__main__":
    main()
