import math
import unittest
import os
from itertools import takewhile, chain
from functional import seq
from fn import _
from fn.iters import iterate as fn_iterate


def compute_module_fuel(module_mass):
    fuel = math.floor((module_mass / 3)) - 2
    return fuel


def compute_module_fuel_realistic(module_mass):
    fuel = compute_module_fuel(module_mass)
    total_fuel = fuel

    while True:
        fuel = compute_module_fuel(fuel)
        if fuel <= 0:
            break
        total_fuel += fuel
    return total_fuel


def compute_sum_of_module_fuel():
    fuel_sum = 0
    lines = get_file_contents()
    for line in lines:
        fuel_sum += compute_module_fuel(int(line))
    return fuel_sum


def compute_sum_of_module_fuel_realistic():
    fuel_sum = 0
    lines = get_file_contents()
    for line in lines:
        fuel_sum += compute_module_fuel_realistic(int(line))
    return fuel_sum


def get_file_contents():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d1.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines


def module_fuel():
    lines = get_file_contents()
    fuel = sum(int(l) // 3 - 2 for l in lines)
    return fuel


def module_fuel_overall():
    lines = get_file_contents()

    def poor_man_iterate(seed, func):
        while True:
            seed = func(seed)
            yield seed

    def poor_man_flat_map(i):
        return chain.from_iterable(i)

    r = sum(
        poor_man_flat_map(
            takewhile(lambda x: x > 0,
                      poor_man_iterate(int(module_mass), lambda x: x // 3 - 2))
            for module_mass in lines)
    )
    return r


def module_fuel_overall_2():
    r = (seq(get_file_contents())
         .map(int)
         .flat_map(lambda mass: seq(fn_iterate(_ // 3 - 2, mass))
                   .take_while(_ > 0)
                   .drop(1))
         .sum())
    return r


class Tests(unittest.TestCase):
    def test_fuel(self):
        self.assertEqual(compute_module_fuel(12), 2)
        self.assertEqual(compute_module_fuel(14), 2)
        self.assertEqual(compute_module_fuel(1969), 654)
        self.assertEqual(compute_module_fuel(100756), 33583)

    def test_fuel_realistic(self):
        self.assertEqual(compute_module_fuel_realistic(14), 2)
        self.assertEqual(compute_module_fuel_realistic(1969), 966)
        self.assertEqual(compute_module_fuel_realistic(100756), 50346)


if __name__ == '__main__':
    print(module_fuel())
    print(compute_sum_of_module_fuel())

    print(module_fuel_overall())
    print(module_fuel_overall_2())
    print(compute_sum_of_module_fuel_realistic())
    unittest.main()
