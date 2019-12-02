import unittest
import os
import functools
import operator


def get_file_contents():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d2.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines


def get_numbers(lines):
    return [int(x) for x in ",".join(lines).strip().split(",")]


def run_instruction(ip, memory):
    op = memory[ip]
    if op == 99:
        return -1
    elif op == 1 or op == 2:
        if op == 1:
            func = operator.add
        elif op == 2:
            func = operator.mul
        memory[memory[ip + 3]] = functools.reduce(func, [memory[memory[ip + 1]], memory[memory[ip + 2]]])
        return 4


def run_program(memory):
    ip = 0
    while ip < len(memory):
        advance = run_instruction(ip, memory)
        if advance == -1:
            break
        else:
            ip += advance
    return memory


def run_program_str(input_str):
    return run_program(get_numbers(input_str))


class Tests(unittest.TestCase):
    def test_samples(self):
        self.assertEqual(run_program(
            [1,9,10,3,2,3,11,0,99,30,40,50]),
            [3500,9,10,70,2,3,11,0,99,30,40,50])

        self.assertEqual(run_program(
            [1,0,0,0,99]),
            [2,0,0,0,99])

        self.assertEqual(run_program_str(
            ["1, 0, 0, 0, 99"]),
            [2, 0, 0, 0, 99])

        self.assertEqual(run_program(
            [2,3,0,3,99]),
            [2,3,0,6,99])

        self.assertEqual(run_program(
            [2,4,4,5,99,0]),
            [2,4,4,5,99,9801])

        self.assertEqual(run_program(
            [1,1,1,4,99,5,6,0,99]),
            [30,1,1,4,2,5,6,0,99])


def restore_gravity_assist_program():
    memory = get_numbers(get_file_contents())
    memory[1] = 12
    memory[2] = 2
    run_program(memory)
    print(memory[0])


def get_the_answer_to_life_the_universe_and_everything(noun, verb):
    print(100 * int(noun) + int(verb))


def restore_gravity_assist_program_real():
    memory = get_numbers(get_file_contents())
    memory_backup = list(memory)

    for noun in range(0, 100):
        for verb in range(0, 100):
            memory[1] = noun
            memory[2] = verb
            run_program(memory)
            if memory[0] == 19690720:
                get_the_answer_to_life_the_universe_and_everything(noun, verb)
                return
            memory = list(memory_backup)


if __name__ == '__main__':
    # unittest.main()
    restore_gravity_assist_program()
    restore_gravity_assist_program_real()

