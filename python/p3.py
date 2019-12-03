import unittest
import os


def get_file_contents():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d3.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines


def split_entries(line: str):
    return [(x[0], int(x[1:])) for x in line.split(",")]


def delta(letter: str):
    if letter == "L":
        return -1, 0
    if letter == "R":
        return 1, 0
    if letter == "U":
        return 0, 1
    if letter == "D":
        return 0, -1


def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def find_closest_intersection(wire1, wire2, count_steps=False):
    def compute_points(wire, points):
        x, y = 0, 0
        steps = 0
        for direction, steps_to_take in wire:
            x_delta, y_delta = delta(direction)
            for i in range(steps_to_take):
                x += x_delta
                y += y_delta
                steps += 1
                if (x,y) not in points:
                    points[(x,y)] = steps

    wire1_points = {}
    wire2_points = {}
    compute_points(wire1, wire1_points)
    compute_points(wire2, wire2_points)

    wire1_points_set = set(wire1_points)
    wire2_points_set = set(wire2_points)
    common_points = wire1_points_set & wire2_points_set

    if count_steps:
        min_distance = min([wire1_points[(x,y)] + wire2_points[(x,y)] for x, y in common_points])
    else:
        min_distance = min([distance((0,0), (x,y)) for x, y in common_points])

    return min_distance


def find_closest_intersection_str(wire1_str, wire2_str, count_steps=False):
    wire1 = split_entries(wire1_str)
    wire2 = split_entries(wire2_str)
    return find_closest_intersection(wire1, wire2, count_steps)


def part1():
    contents = get_file_contents()
    print(find_closest_intersection_str(contents[0], contents[1]))


def part2():
    contents = get_file_contents()
    print(find_closest_intersection_str(contents[0], contents[1], count_steps=True))


class Tests(unittest.TestCase):
    def test_samples(self):
        self.assertEqual(find_closest_intersection_str(
            "R75,D30,R83,U83,L12,D49,R71,U7,L72",
            "U62,R66,U55,R34,D71,R55,D58,R83"),
            159)

        self.assertEqual(find_closest_intersection_str(
            "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
            "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7"),
            135)

        self.assertEqual(find_closest_intersection_str(
            "R75,D30,R83,U83,L12,D49,R71,U7,L72",
            "U62,R66,U55,R34,D71,R55,D58,R83", count_steps=True),
            610)

        self.assertEqual(find_closest_intersection_str(
            "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
            "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", count_steps=True),
            410)


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()

