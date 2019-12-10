import unittest
import os
import heapq
import math
import collections


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d10.txt")
    with open(file_path, "r") as f:
        lines = f.read()
    return lines


class Map(object):
    def __init__(self, map_str: str):
        self.m = []
        self.d = {}

        lines = map_str.strip().splitlines()
        self.r = len(lines)
        self.c = len(lines[0])
        for r, line in enumerate(lines):
            for c, ch in enumerate(line.strip()):
                self.m.append(ch)
                if ch == "#":
                    self.d[(c, r)] = c, r

    def __str__(self):
        s = ""
        for r in range(self.r):
            for c in range(self.c):
                s += self.get(r, c)
            s += "\n"
        return s

    def get(self, r, c):
        return self.m[r * self.c + c]


def unit_vector(v):
    magnitude = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2))
    return v[0] / magnitude, v[1] / magnitude


def unit_vector_direction(p1, p2):
    return unit_vector((p2[0] - p1[0], p2[1] - p1[1]))


def vector_equal(d_origin, d_other):
    if math.isclose(d_origin[0], d_other[0]) and math.isclose(d_origin[1], d_other[1]):
        return True
    return False


def dist(p1, p2):
    d = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    return d


def solve(map_str: str):
    m = Map(map_str)
    print(m)

    max_sighted = 0
    chosen_coords = None

    for origin_point in m.d.keys():
        sighted = set()
        sighted_ordered = []
        directions = []
        p_queue = []

        for p in m.d.keys():
            if p != origin_point:
                heapq.heappush(p_queue, [dist(origin_point, p), p])

        while p_queue:
            _, p = heapq.heappop(p_queue)
            if p not in sighted:
                d_other = unit_vector_direction(origin_point, p)

                intersected = any(vector_equal(d_origin, d_other) for d_origin in directions)
                if not intersected:
                    directions.append(d_other)
                    sighted.add(p)
                    sighted_ordered.append(p)

        if len(sighted) > max_sighted:
            max_sighted = len(sighted)
            chosen_coords = origin_point

    return max_sighted, chosen_coords


def angle(u1, u2):
    u1_a = math.atan2(u1[1], u1[0])
    u2_a = math.atan2(u2[1], u2[0])
    r_a = u2_a - u1_a
    if r_a < 0:
        r_a += 2 * math.pi

    return r_a


def vaporize(map_str: str, starting_point=None, interested_asteroid=None):
    if starting_point:
        origin_point = starting_point
    else:
        max_seen, origin_point = solve(map_str)
        print(max_seen, origin_point)

    m = Map(map_str)

    up = (0, -1)

    angle_distance_and_coords = []
    for p in m.d.keys():
        if p != origin_point:
            direction = unit_vector_direction(origin_point, p)
            distance = dist(origin_point, p)
            p_angle = angle(up, direction)
            angle_distance_and_coords.append((p_angle, distance, p))

    angle_distance_and_coords_sorted = collections.deque(sorted(angle_distance_and_coords, key=lambda k: (k[0], k[1])))

    asteroid_vaporized_count = 0
    current_angle = None
    rotations = 1
    tries = 0
    break_the_eternal_loop = False
    interested_asteroid_coords = None
    while angle_distance_and_coords_sorted:
        p_angle, distance, p = angle_distance_and_coords_sorted.popleft()
        if current_angle is None or not math.isclose(current_angle, p_angle, rel_tol=1e-10) or break_the_eternal_loop:
            asteroid_vaporized_count += 1
            prev_angle = current_angle
            current_angle = p_angle
            if prev_angle is not None and current_angle < prev_angle:
                rotations += 1
                print("Next rotation: {}".format(rotations))

            print("Vaporizing asteroid n: {} coords: {} angle: {}".format(asteroid_vaporized_count, p, p_angle))
            if interested_asteroid is not None and interested_asteroid == asteroid_vaporized_count:
                interested_asteroid_coords = p
            tries = 0
            break_the_eternal_loop = False
        else:
            angle_distance_and_coords_sorted.append((p_angle, distance, p))
            tries += 1
            if tries >= 500:
                break_the_eternal_loop = True

    print("Rotations: {} Vaporized {}".format(rotations + 1, asteroid_vaporized_count))
    return interested_asteroid_coords


def part1():
    input_map = get_file_contents()
    r, _ = solve(input_map)
    print(r)
    assert r == 347


def part2():
    input_map = get_file_contents()
    interested_asteroid_coords = vaporize(input_map, interested_asteroid=200)
    print(">> interested asteroid number: {} coords: {}".format(200, interested_asteroid_coords))
    final_result = interested_asteroid_coords[0] * 100 + interested_asteroid_coords[1]
    print(final_result)


class Tests(unittest.TestCase):
    def check_max_sighted(self, map_str: str, expected_sighted: int):
        max_sighted, station_coords = solve(map_str)
        print(station_coords)
        self.assertEqual(max_sighted, expected_sighted)

    def test_samples(self):
        self.check_max_sighted("""
.#..#
.....
#####
....#
...##        
        """, 8)

        self.check_max_sighted("""
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####        
        """, 33)

        self.check_max_sighted("""
#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.     
        """, 35)

        self.check_max_sighted("""
.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..     
        """, 41)

        self.check_max_sighted("""
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##   
        """, 210)

        vaporize("""
.#....#####...#..
##...##.#####..##
##...#...#.#####.
..#.....X...###..
..#.#.....#....##
    """, starting_point=(8, 3))

        interested_asteroid_coords = vaporize("""
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##""", starting_point=(11, 13), interested_asteroid=200)
        print(">>>> coords: ", interested_asteroid_coords)


if __name__ == '__main__':
    # part1()
    part2()
    # unittest.main()
