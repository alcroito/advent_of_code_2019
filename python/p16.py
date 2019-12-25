import os
import unittest
import typing


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d16.txt")
    with open(file_path, "r") as f:
        lines = f.read()
    return lines


Numbers = typing.List[int]
PatternGenerator = typing.Generator[int, None, None]
Patterns = typing.List[PatternGenerator]


def make_pattern(position: int, input_len: int) -> PatternGenerator:
    yielded = 0  # source = [0, 1, 0, -1]

    yielded += position
    while True:
        for i in range(0, position + 1):
            if yielded >= input_len:
                return
            yield (yielded, 1)
            yielded += 1
        yielded += position + 1
        for i in range(0, position + 1):
            if yielded >= input_len:
                return
            yield (yielded, -1)
            yielded += 1
        yielded += position + 1


def compute_next_phase(input_numbers: Numbers,
                       patterns: Patterns) -> Numbers:
    numbers_len = len(input_numbers)
    new_phase = [0] * numbers_len
    for pos in range(numbers_len):
        s = 0

        for i, sign in patterns[pos]:
            s += input_numbers[i] * sign

        digit = abs(s) % 10
        new_phase[pos] = digit
    return new_phase


def print_numbers(numbers: Numbers):
    print("".join(str(n) for n in numbers))


def compute_fft_phase(input_str: str, phase_count: int = 1):
    numbers = [int(n) for n in input_str.strip()]

    for i in range(phase_count):
        patterns = [make_pattern(i, len(numbers))
                    for i in range(len(numbers))]
        numbers = compute_next_phase(numbers, patterns)

    return "".join(str(n) for n in numbers)


def compute_offset_fft_phase(input_str: str, phase_count: int = 1, repeat: int = 1) -> int:
    numbers = [int(n) for n in input_str.strip()]
    if repeat > 1:
        numbers = numbers * repeat
    numbers_len = len(numbers)

    offset = int("".join([str(v) for v in numbers[:7]]))

    for _ in range(phase_count):
        new_phase = [0] * numbers_len

        s = 0
        for pos in range(numbers_len - 1, offset - 1, -1):
            val = numbers[pos]
            s = (s + val) % 10
            new_phase[pos] = s
        numbers = list(new_phase)
    return int("".join(str(n) for n in numbers[offset:offset+8]))


def part1():
    numbers = compute_fft_phase(get_file_contents(), 100)
    assert numbers[:8] == "28430146"


def part2():
    offset_message = compute_offset_fft_phase(get_file_contents(), phase_count=100, repeat=10000)
    print(offset_message)
    assert offset_message == 12064286


class Tests(unittest.TestCase):
    def test_samples(self):
        numbers = compute_fft_phase("12345678", 4)
        self.assertEqual(numbers, "01029498")

        numbers = compute_fft_phase("80871224585914546619083218645595", 100)
        self.assertEqual(numbers[:8], "24176176")

        numbers = compute_fft_phase("19617804207202209144916044189917", 100)
        self.assertEqual(numbers[:8], "73745418")

        numbers = compute_fft_phase("69317163492948606335995924319873", 100)
        self.assertEqual(numbers[:8], "52432133")

        message = compute_offset_fft_phase("03036732577212944063491565474664", 100, repeat=10000)
        self.assertEqual(message, 84462026)

        message = compute_offset_fft_phase("02935109699940807407585447034323", 100, repeat=10000)
        self.assertEqual(message, 78725270)

        message = compute_offset_fft_phase("03081770884921959731165446850517", 100, repeat=10000)
        self.assertEqual(message, 53553731)


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
