import os
import collections
import enum
import time

use_curses = False
try:
    use_curses = False
    import curses
except ImportError:
    curses = None

try:
    from python.utils.intcode import VM
except ImportError:
    try:
        from utils.intcode import VM
    except ImportError:
        VM = None


if use_curses:
    std_scr = curses.initscr()
    curses.resizeterm(50, 50)


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d13.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


class Tile(enum.IntEnum):
    Empty = 0
    Wall = 1
    Block = 2
    Paddle = 3
    Ball = 4


def print_map(m, max_x: int, max_y: int, passed_std_scr):
    passed_std_scr.clear()
    d = {Tile.Wall: "X", Tile.Empty: " ", Tile.Block: "b", Tile.Paddle: "-", Tile.Ball: "o"}
    for y in range(max_y):
        passed_std_scr.move(y, 0)

        for x in range(max_x):
            c = d[m[x, y]]
            passed_std_scr.addstr("{}".format(c))
    passed_std_scr.refresh()


def compute_bounds(m):
    min_x = min(x for x, _ in m.keys())
    assert min_x == 0
    min_y = min(y for _, y in m.keys())
    assert min_y == 0
    max_x = max(x for x, _ in m.keys())
    max_y = max(y for _, y in m.keys())
    return max_x, max_y


def solve(passed_std_scr):
    m = collections.defaultdict(lambda: 0)
    vm = VM(get_file_contents())
    vm.write_memory(0, 2)  # Insert coins.
    current_score = -999
    paddle_pos = None
    ball_pos = None

    max_x = 0
    max_y = 0

    while True:
        i = 0
        paddle_action = [0]
        if paddle_pos and ball_pos:
            paddle_x, _ = paddle_pos
            ball_x, _ = ball_pos
            if ball_x < paddle_x:
                paddle_action = [-1]
            elif ball_x > paddle_x:
                paddle_action = [1]

        output_values = vm.resume(paddle_action)
        output_len = len(output_values)
        for j in range(0, output_len // 3):
            x, y, tile = output_values[j * 3:j * 3 + 3]
            if x == -1 and y == 0:
                current_score = tile
            else:
                m[(x, y)] = Tile(tile)
                if tile == Tile.Paddle:
                    paddle_pos = x, y
                elif tile == Tile.Ball:
                    ball_pos = x, y

        if vm.halted():
            break

        if use_curses:
            if i == 0:
                max_x, max_y = compute_bounds(m)
            print_map(m, max_x, max_y, passed_std_scr)
        i += 1
    return current_score


def part1():
    m = collections.defaultdict(lambda: 0)
    vm = VM(get_file_contents())
    output_values = collections.deque(vm.run())
    block_tile_count = 0
    while output_values:
        x, y, tile = (output_values.popleft() for _ in range(3))
        m[(x, y)] = Tile(tile)
        if tile == Tile.Block:
            block_tile_count += 1
    print(block_tile_count)
    assert block_tile_count == 361


def part2():
    if use_curses:
        std_scr.clear()
        curses.curs_set(False)
        curses.noecho()
        curses.cbreak()
        start = time.time()
        score = curses.wrapper(solve)
        elapsed = time.time() - start
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    else:
        start = time.time()
        score = solve("")
        elapsed = time.time() - start

    print("Score: {} Elapsed: {}".format(score, elapsed))
    assert score == 17590


if __name__ == '__main__':
    part1()
    part2()
