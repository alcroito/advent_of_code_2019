import os
import itertools
import typing
import unittest
import math
import copy
import functools


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d12.txt")
    with open(file_path, "r") as f:
        lines = f.read()
    return lines


Pos = typing.List[int]
Positions = typing.List[Pos]
Velocity = typing.List[int]
Velocities = typing.List[Velocity]


def str_to_moon_pos(s: str) -> Positions:
    return lines_to_moon_pos([l.strip() for l in s.strip().splitlines()])


def lines_to_moon_pos(lines: typing.List[str]) -> Positions:
    positions: Positions = []
    for line in lines:
        pos = list(int(piece.strip(" ")[2:])
                   for piece in line.strip("<>").split(","))[0:3]
        positions.append(pos)
    return positions


def gravity_delta(x1, x2):
    if x1 > x2:
        return -1, 1
    elif x1 < x2:
        return 1, -1
    return 0, 0


def dump(positions: Positions, v: Velocities, t: int):
    print(f"After {t} steps")
    for i, p in enumerate(positions):
        print("pos=<x={:>3}, y={:>3}, z={:>3}>, ".format(p[0], p[1], p[2]), end="")
        print("vel=<x={:>3}, y={:>3}, z={:>3}>".format(v[i][0], v[i][1], v[i][2]))
    print()


def solve(contents: str, will_dump: bool = False, steps: int = 10, return_cycle_step_count: bool = False) -> int:
    positions = str_to_moon_pos(contents)
    initial_positions = copy.deepcopy(positions)
    velocities = [[0] * 3 for _ in positions]
    t = 0

    if will_dump:
        dump(positions, velocities, t)

    cycle_times = [0] * 3
    if return_cycle_step_count:
        steps = 10000000

    for t in range(1, steps + 1):
        positions_with_i = [(i, p) for i, p in enumerate(positions)]
        position_pairs = list(itertools.combinations(positions_with_i, 2))
        for (i, p1), (j, p2) in position_pairs:
            deltas = [gravity_delta(x1, x2) for x1, x2 in zip(p1, p2)]
            for axis, (x1, x2) in enumerate(deltas):
                velocities[i][axis] += x1
                velocities[j][axis] += x2

        for i, (x, y, z) in enumerate(velocities):
            positions[i][0] += x
            positions[i][1] += y
            positions[i][2] += z

        if return_cycle_step_count:
            for axis in range(3):
                cur_pos = list(map(lambda p: p[axis], positions))
                init_pos = list(map(lambda p: p[axis], initial_positions))
                if cur_pos == init_pos and cycle_times[axis] == 0:
                    cycle_times[axis] = t + 1

            if all(cycle_times):
                cycle_steps = functools.reduce(lcm, cycle_times, 1)
                return cycle_steps

        if will_dump:
            dump(positions, velocities, t)

    # Compute energy
    energy = 0
    for i in range(len(positions)):
        potential = sum(map(abs, positions[i]))
        kinetic = sum(map(abs, velocities[i]))

        if will_dump:
            print("i: {} sum: {}".format(i, potential))
            print("i: {} sum: {}".format(i, kinetic))

        p_total = potential * kinetic
        energy += p_total

    return energy


def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


def part1():
    contents = get_file_contents()
    energy = solve(contents, steps=1000)
    print(energy)
    assert energy == 6220


def part2():
    contents = get_file_contents()
    cycle_step_count = solve(contents, return_cycle_step_count=True)
    print(cycle_step_count)
    assert cycle_step_count == 548525804273976


class Tests(unittest.TestCase):
    def test_samples(self):
        contents = """
            <x=-1, y=0, z=2>
            <x=2, y=-10, z=-7>
            <x=4, y=-8, z=8>
            <x=3, y=5, z=-1>    
                """

        energy = solve(contents, steps=10)
        self.assertEqual(energy, 179)

        contents = """
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>"""

        energy = solve(contents, steps=100)
        self.assertEqual(energy, 1940)

        contents = """
<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>"""

        step_count = solve(contents, return_cycle_step_count=True)
        self.assertEqual(step_count, 2772)

        contents = """
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>"""

        step_count = solve(contents, return_cycle_step_count=True)
        self.assertEqual(step_count, 4686774924)


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
