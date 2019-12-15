import os
import collections
import enum
import heapq

try:
    from python.utils.intcode import VM
except ImportError:
    try:
        from utils.intcode import VM
    except ImportError:
        VM = None


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d15.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


class MoveResult(enum.IntEnum):
    Wall = 0
    Moved = 1
    OxygenFound = 2


class Tile(enum.IntEnum):
    Wall = 0
    Undiscovered = 1
    Empty = 2
    Oxygen = 3
    Robot = 4


move_command = {"N": 1, "S": 2, "W": 3, "E": 4}
move_pos_delta = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
move_command_backtrack = {"N": "S", "S": "N", "W": "E", "E": "W"}
move_result_to_tile = {MoveResult.Moved: Tile.Empty, MoveResult.OxygenFound: Tile.Oxygen, MoveResult.Wall: Tile.Wall}


def translate(pos, direction: str):
    delta = move_pos_delta[direction]
    return pos[0] + delta[0], pos[1] + delta[1]


def print_map(m, max_x: int, max_y: int, robot_pos):
    d = {Tile.Wall: "#", Tile.Empty: " ", Tile.Oxygen: "o", Tile.Undiscovered: ".", Tile.Robot: "*"}
    print()
    for y in range(max_y):
        for x in range(max_x):
            cur_pos = x, y
            if cur_pos == robot_pos:
                c = d[Tile.Robot]
            elif cur_pos in m:
                c = d[m[x, y]]
            else:
                c = d[Tile.Undiscovered]
            print("{}".format(c), end="")
        print()
    print()


def explore_map():
    m = collections.defaultdict(lambda: Tile.Undiscovered.value)
    vm = VM(get_file_contents())

    max_x, max_y = 50, 46

    robot_pos = (max_x // 2, max_y // 2)
    m[robot_pos] = Tile.Empty

    def move_robot(direction):
        nonlocal robot_pos
        move_result, = vm.resume([move_command[direction]])
        if move_result == MoveResult.Wall:
            m[translate(robot_pos, direction)] = Tile.Wall
            return False
        elif move_result in [MoveResult.Moved, MoveResult.OxygenFound]:
            m[translate(robot_pos, direction)] = move_result_to_tile[move_result]
            robot_pos = translate(robot_pos, direction)
            return True

    def move_robot_backtrack(directions):
        for d in reversed(directions):
            move_robot(move_command_backtrack[d])
            current_path.pop()

    def move_robot_to_pos(target_directions):
        # noinspection PyTypeChecker
        common_len = len(os.path.commonprefix([list(target_directions), current_path]))
        # Don't back-track when both current and target directions have a common
        # prefix path.
        move_robot_backtrack(list(current_path)[common_len:])
        for d in target_directions[common_len:]:
            moved = move_robot(d)
            if moved:
                current_path.append(d)

    def add_next_candidates(cur_pos, cur_path):
        candidates = ((translate(cur_pos, str(d)),
                       tuple(list(cur_path) + [str(d)]))
                      for d in move_command.keys())
        for new_pos, new_path in candidates:
            if new_pos not in visited:
                unexplored.append((new_pos, new_path))

    oxygen_pos = None
    i = 0
    visited = set()
    starting_pos = robot_pos
    current_path = []
    unexplored = []
    add_next_candidates(starting_pos, [])

    # Explore map.
    while unexplored:
        next_pos, path_from_origin = unexplored.pop()

        move_robot_to_pos(path_from_origin)
        visited.add(next_pos)

        if m[robot_pos] == Tile.Oxygen:
            oxygen_pos = robot_pos
        if m[next_pos] != Tile.Wall:
            add_next_candidates(next_pos, path_from_origin)

        i += 1
        if (i % 50) == 0:
            print("Iteration: {}".format(i))
            print_map(m, max_x, max_y, robot_pos)

    print("Iteration: {}".format(i))
    print_map(m, max_x, max_y, robot_pos)
    print("Oxygen location: {}".format(oxygen_pos))
    return m, starting_pos, oxygen_pos


def a_star(m, starting_pos, end_pos):
    # Find shortest path using A star.

    def distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    unexplored = []
    pos_costs_so_far = {starting_pos: 0}
    current_cost = -1

    heapq.heappush(unexplored, (0, starting_pos))
    while unexplored:
        current_cost, current_pos = heapq.heappop(unexplored)

        if current_pos == end_pos:
            break

        candidates = (translate(current_pos, str(d))
                      for d in move_command.keys())
        candidates = (c
                      for c in candidates
                      if m[c] not in [Tile.Wall, Tile.Undiscovered])
        for new_pos in candidates:
            new_cost = pos_costs_so_far[current_pos] + distance(current_pos, new_pos)
            if new_pos not in pos_costs_so_far or new_cost < pos_costs_so_far[new_pos]:
                pos_costs_so_far[new_pos] = new_cost
                heapq.heappush(unexplored, (new_cost, new_pos))

    return current_cost


def map_fill(m, starting_pos):
    unprocessed = {starting_pos}
    visited = set()

    minutes = 0
    while unprocessed:
        to_process = list(unprocessed)

        candidates = []
        for p in to_process:
            visited.add(p)
            m[p] = Tile.Oxygen

            p_candidates = (translate(p, str(d))
                            for d in move_command.keys())
            p_candidates = (c
                            for c in p_candidates
                            if m[c] not in [Tile.Wall, Tile.Oxygen, Tile.Undiscovered]
                            and c not in visited)
            candidates.extend(p_candidates)
        unprocessed = set(candidates)

        print("Iteration: {}".format(minutes))
        print_map(m, 50, 46, (-1, -1))

        minutes += 1
    return minutes - 1


def part1():
    m, starting_pos, oxygen_pos = explore_map()
    cost = a_star(m, starting_pos, oxygen_pos)
    print("Shortest step count to goal: {}".format(cost))
    assert cost == 210


def part2():
    m, _, oxygen_pos = explore_map()
    minutes = map_fill(m, oxygen_pos)
    print("Map filled after '{}' minutes.".format(minutes))
    assert minutes == 290


if __name__ == '__main__':
    # part1()
    part2()
