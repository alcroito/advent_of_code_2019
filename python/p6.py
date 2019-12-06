import unittest
import os
import typing
from collections import deque


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d6.txt")
    with open(file_path, "r") as f:
        lines = f.read()
        return lines


class OrbitGraph(object):
    def __init__(self):
        self.edges: typing.Dict[str, typing.List[str]] = {}

    @staticmethod
    def create_graph_from_input_string(s: str):
        g = OrbitGraph()
        for line in s.splitlines(keepends=False):
            if line:
                central_object, orbiter = line.split(")")
                g.add_edge(central_object, orbiter)
        return g

    def add_edge(self, central_object: str, orbiter: str):
        if central_object not in self.edges:
            self.edges[central_object] = []
        if orbiter not in self.edges:
            self.edges[orbiter] = []
        self.edges[central_object].append(orbiter)
        self.edges[orbiter].append(central_object)

    def __str__(self):
        s = ""
        for center, orbiters in self.edges.items():
            s += "{} {}\n".format(center, orbiters)
        return s

    def bfs(self,
            start_object: str,
            end_object: str,
            on_visit) -> typing.Any:
        visited = set()
        to_visit = deque([(start_object, 0)])
        while to_visit:
            current_object, steps = to_visit.popleft()
            visited.add(current_object)

            if on_visit(current_object, steps, end_object):
                return

            if current_object in self.edges:
                for child in self.edges[current_object]:
                    if child not in visited:
                        to_visit.append((child, steps + 1))

    def count_number_of_orbits(self) -> int:
        total_number_of_orbits = 0

        def on_visit(_, current_steps: int, __) -> bool:
            nonlocal total_number_of_orbits
            total_number_of_orbits += current_steps
            return False

        self.bfs("COM", "", on_visit)

        return total_number_of_orbits

    def get_minimum_transfers(self, start_object: str, end_object: str) -> int:
        min_transfers = -1

        def on_visit(current_object: str, current_steps: int, end_goal: str) -> bool:
            nonlocal min_transfers
            if current_object == end_goal:
                min_transfers = current_steps - 2
                return True

        self.bfs(start_object, end_object, on_visit)
        return min_transfers


class Tests(unittest.TestCase):
    def test_samples(self):
        g = OrbitGraph.create_graph_from_input_string("COM)B\nB)C\nC)D")
        self.assertEqual(g.count_number_of_orbits(), 6)

        sample_input = """
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L"""
        g = OrbitGraph.create_graph_from_input_string(sample_input)
        self.assertEqual(g.count_number_of_orbits(), 42)

        sample_input = """
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN"""
        g = OrbitGraph.create_graph_from_input_string(sample_input)
        min_transfers = g.get_minimum_transfers("YOU", "SAN")
        self.assertEqual(min_transfers, 4)


def part1():
    contents = get_file_contents()
    g = OrbitGraph.create_graph_from_input_string(contents)
    count = g.count_number_of_orbits()
    print(count)
    assert count == 110190


def part2():
    contents = get_file_contents()
    g = OrbitGraph.create_graph_from_input_string(contents)
    count = g.get_minimum_transfers("YOU", "SAN")
    print(count)
    assert count == 343


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
