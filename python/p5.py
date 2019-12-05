import unittest
import os
import functools
import operator
import typing


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d5.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


def get_numbers(line: str) -> typing.List[int]:
    return [int(x) for x in line.strip().split(",")]


def decode_instruction(instruction: int) -> typing.Tuple[int, typing.List[int]]:
    op = instruction % 100
    instruction //= 100
    p1_mode = instruction % 10
    instruction //= 10
    p2_mode = instruction % 10
    instruction //= 10
    p3_mode = instruction % 10

    return op, [p1_mode, p2_mode, p3_mode]


def get_memory_value(memory: typing.List[int], value: int, mode: int) -> int:
    if mode == 0:
        return memory[memory[value]]
    # mode == 1
    return memory[value]


operators = {1: operator.add, 2: operator.mul, 5: operator.ne, 6: operator.eq, 7: operator.lt, 8: operator.eq}


def run_instruction(ip: int,
                    memory: typing.List[int],
                    input_values: typing.List[int],
                    output_values: typing.List[int]
                    ) -> typing.Optional[int]:
    op, p_modes = decode_instruction(memory[ip])

    def get_params(param_count: int) -> typing.List[int]:
        params = [get_memory_value(memory, ip + 1 + i,
                                   # Output param is kinda in immediate mode.
                                   p_modes[i] if i != 2 else 1)
                  for i in range(param_count)]
        return params

    if op == 99:  # Halt
        return None
    elif op == 1 or op == 2:  # Add or multiply x, y into z
        input_1, input_2, output_address = get_params(3)
        memory[output_address] = functools.reduce(operators[op], [input_1, input_2])
        return 4
    elif op == 3:  # Input into x
        output_address = memory[ip + 1]
        memory[output_address] = input_values.pop(0)
        return 2
    elif op == 4:  # Output into x
        output_values.append(get_memory_value(memory, ip + 1, p_modes[0]))
        return 2
    elif op == 5 or op == 6:  # If x != 0 or x == 0, jump to y address
        input_1, input_2 = get_params(2)

        if operators[op](input_1, 0):
            return input_2 - ip
        return 3
    elif op == 7 or op == 8:  # If x < y or x == y, z = 1, otherwise z = 0
        input_1, input_2, output_address = get_params(3)

        if operators[op](input_1, input_2):
            memory[output_address] = 1
        else:
            memory[output_address] = 0
        return 4


def run_program(memory: typing.List[int],
                input_values: typing.List[int],
                output_values: typing.List[int]
                ) -> typing.List[int]:
    ip = 0
    while ip < len(memory):
        advance = run_instruction(ip, memory, input_values, output_values)
        if advance is None:
            break
        else:
            ip += advance
    return memory


def run_program_str(input_str: str,
                    input_values: typing.List[int],
                    output_values: typing.List[int]
                    ) -> typing.List[int]:
    return run_program(get_numbers(input_str), input_values, output_values)


def part1():
    memory = get_numbers(get_file_contents())
    output_values = []
    run_program(memory, [1], output_values)
    print(output_values)


def part2():
    memory = get_numbers(get_file_contents())
    output_values = []
    run_program(memory, [5], output_values)
    print(output_values)


class Tests(unittest.TestCase):
    def run_program_check_output(self: unittest.TestCase,
                                 input_str: str,
                                 input_values: typing.List[int],
                                 expected_output_values: typing.List[int]):
        output_values = []
        run_program_str(input_str, input_values, output_values)
        self.assertEqual(output_values, expected_output_values)

    def test_samples(self):
        self.assertEqual(decode_instruction(1002), (2, [0, 1, 0]))
        self.assertEqual(decode_instruction(99), (99, [0, 0, 0]))
        self.assertEqual(decode_instruction(11103), (3, [1, 1, 1]))

        self.run_program_check_output("3,0,4,0,99", [12], [12])
        self.run_program_check_output("3,9,8,9,10,9,4,9,99,-1,8", [8], [1])
        self.run_program_check_output("3,9,8,9,10,9,4,9,99,-1,8", [9], [0])
        self.run_program_check_output("3,9,7,9,10,9,4,9,99,-1,8", [7], [1])
        self.run_program_check_output("3,3,1108,-1,8,3,4,3,99", [8], [1])
        self.run_program_check_output("3,3,1107,-1,8,3,4,3,99", [10], [0])

        self.run_program_check_output("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [12], [1])
        self.run_program_check_output("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [0], [0])
        self.run_program_check_output("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [12], [1])
        self.run_program_check_output("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [0], [0])

        self.run_program_check_output("3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,"
                                      "125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99",
                                      [7], [999])

        self.run_program_check_output("3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,"
                                      "125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99",
                                      [8], [1000])

        self.run_program_check_output("3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,"
                                      "125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99",
                                      [20], [1001])


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
