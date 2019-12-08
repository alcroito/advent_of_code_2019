import unittest
import os
import typing
import collections


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d8.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


def digits_to_layers(d: str, width: int, height: int) -> typing.List[typing.List[int]]:
    d = [int(e) for e in d]
    size = width * height
    layers = [d[i:i+size] for i in range(0, len(d), size)]
    return layers


def find_layer_with_fewest_digit_count(digit_to_search: int, layers: typing.List[typing.List[int]]) -> int:
    counters = [collections.Counter(l) for l in layers]
    digit_counts = [c[digit_to_search] for c in counters]
    index_with_min_counts = min(range(len(digit_counts)), key=digit_counts.__getitem__)
    return index_with_min_counts


def count_digit_in_layer(layer: typing.List[int], digit: int) -> int:
    return collections.Counter(layer)[digit]


def image_checksum(d: str, width: int, height: int) -> int:
    layers = digits_to_layers(d, width, height)
    min_layer = find_layer_with_fewest_digit_count(0, layers)
    ones = count_digit_in_layer(layers[min_layer], 1)
    twos = count_digit_in_layer(layers[min_layer], 2)
    return ones * twos


def render_pixel(layered_pixels: typing.List[int]) -> int:
    # 0'th is front pixel, 1'th is the pixel behind the front one, etc.
    r = layered_pixels[0]
    for i in range(1, len(layered_pixels)):
        if r == 2:
            r = layered_pixels[i]
        else:
            break

    return r


def render_image(d: str, width: int, height: int) -> typing.List[int]:
    layers = digits_to_layers(d, width, height)
    rendered_image = [render_pixel(list(pixels)) for pixels in zip(*layers)]
    return rendered_image


def part1():
    checksum = image_checksum(get_file_contents(), 25, 6)
    print(checksum)


def part2():
    width, height = 25, 6
    image = render_image(get_file_contents(), width, height)
    image_rows = [image[i:i+width] for i in range(0, len(image), width)]

    for row in image_rows:
        for col in row:
            if col == 1:
                print("#", end="")
            else:
                print(" ", end="")
        print("")


class Tests(unittest.TestCase):
    def test_samples(self):
        self.assertEqual(image_checksum("123456789012", 3, 2), 1)

        self.assertEqual(render_pixel([0, 1, 2]), 0)
        self.assertEqual(render_pixel([2, 1, 0]), 1)

        self.assertEqual(render_image("0222112222120000", 2, 2), [0, 1, 1, 0])


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
