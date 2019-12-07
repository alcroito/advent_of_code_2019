import unittest
import os
import functools
import operator
import typing
import itertools
import enum


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d7.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


def get_int_code_instructions(line: str) -> typing.List[int]:
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


class InstructionResultType(enum.Enum):
    Halt = 1
    Interrupt = 2
    AdvanceIP = 3


class InstructionResult(object):
    def __init__(self):
        self._result_type = None
        self._value = None

    @staticmethod
    def create(result_type: InstructionResultType, value: typing.Any):
        r = InstructionResult()
        r._result_type = result_type
        r._value = value
        return r

    @staticmethod
    def advance_ip(value: int):
        return InstructionResult.create(InstructionResultType.AdvanceIP, value)

    @staticmethod
    def halt():
        return InstructionResult.create(InstructionResultType.Halt, None)

    @staticmethod
    def interrupt():
        return InstructionResult.create(InstructionResultType.Interrupt, None)

    def type(self) -> InstructionResultType:
        return self._result_type

    def value(self) -> typing.Any:
        return self._value


class ProgramStateType(enum.Enum):
    Created = 1
    Running = 2
    Interrupted = 3
    Halted = 4


class ProgramState(object):
    def __init__(self):
        self._state_type = None
        self._memory = None
        self._ip = None

    def __str__(self):
        s = "ip {} s {} m {}".format(self.ip, self.state, self.memory)
        return s

    @staticmethod
    def create(memory: typing.List[int], ip: int, state_type: ProgramStateType = ProgramStateType.Created):
        s = ProgramState()
        s._state_type = state_type
        s._memory = memory
        s._ip = ip
        return s

    @property
    def state(self) -> ProgramStateType:
        return self._state_type

    @state.setter
    def state(self, value):
        self._state_type = value

    @property
    def memory(self) -> typing.List[int]:
        return self._memory

    @memory.setter
    def memory(self, value):
        self._memory = value

    @property
    def ip(self) -> int:
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value


def run_instruction(ip: int,
                    memory: typing.List[int],
                    input_values: typing.List[int],
                    output_values: typing.List[int]
                    ) -> InstructionResult:
    op, p_modes = decode_instruction(memory[ip])

    def get_params(param_count: int) -> typing.List[int]:
        params = [get_memory_value(memory, ip + 1 + i,
                                   # Output param is kinda in immediate mode.
                                   p_modes[i] if i != 2 else 1)
                  for i in range(param_count)]
        return params

    if op == 99:  # Halt
        return InstructionResult.halt()
    elif op == 1 or op == 2:  # Add or multiply x, y into z
        input_1, input_2, output_address = get_params(3)
        memory[output_address] = functools.reduce(operators[op], [input_1, input_2])
        return InstructionResult.advance_ip(4)
    elif op == 3:  # Input into x
        # No input values, interrupt program, save state, allow to resume
        # later.
        if not input_values:
            return InstructionResult.interrupt()
        output_address = memory[ip + 1]
        memory[output_address] = input_values.pop(0)
        return InstructionResult.advance_ip(2)
    elif op == 4:  # Output into x
        output_values.append(get_memory_value(memory, ip + 1, p_modes[0]))
        return InstructionResult.advance_ip(2)
    elif op == 5 or op == 6:  # If x != 0 or x == 0, jump to y address
        input_1, input_2 = get_params(2)

        if operators[op](input_1, 0):
            return InstructionResult.advance_ip(input_2 - ip)
        return InstructionResult.advance_ip(3)
    elif op == 7 or op == 8:  # If x < y or x == y, z = 1, otherwise z = 0
        input_1, input_2, output_address = get_params(3)

        if operators[op](input_1, input_2):
            memory[output_address] = 1
        else:
            memory[output_address] = 0
        return InstructionResult.advance_ip(4)


def resume_program_helper(p: ProgramState,
                          input_values: typing.List[int],
                          output_values: typing.List[int]
                          ) -> ProgramState:

    ip = p.ip
    memory = p.memory
    p.state = ProgramStateType.Running
    while ip < len(memory):
        result = run_instruction(ip, memory, input_values, output_values)
        result_type = result.type()
        if result_type == InstructionResultType.AdvanceIP:
            ip += result.value()
        elif result_type == InstructionResultType.Halt:
            p.ip = ip
            p.state = ProgramStateType.Halted
            break
        elif result_type == InstructionResultType.Interrupt:
            p.state = ProgramStateType.Interrupted
            p.ip = ip
            break

    return p


def resume_program(p: ProgramState,
                   input_values: typing.List[int],
                   output_values: typing.List[int]) -> ProgramState:
    p = resume_program_helper(p, input_values, output_values)
    return p


def create_program_str(input_program: str) -> ProgramState:
    memory = get_int_code_instructions(input_program)
    p = ProgramState.create(memory, 0)
    return p


def run_program_str(input_program: str,
                    input_values: typing.List[int],
                    output_values: typing.List[int]
                    ) -> ProgramState:
    p = create_program_str(input_program)
    return resume_program(p, input_values, output_values)


def run_program_for_amplifiers(input_program: str,
                               phases_list: typing.List[int]) -> int:
    last_signal_output = 0
    amplifier_programs = [create_program_str(input_program) for _ in range(5)]
    program_interrupted = True
    resumes_count = 0
    while program_interrupted:
        program_interrupted = False
        for i in range(5):
            output_values = []
            input_values = []
            if resumes_count == 0:
                input_values.insert(0, phases_list[i])
            input_values.append(last_signal_output)
            p = resume_program(amplifier_programs[i], input_values, output_values)
            if p.state == ProgramStateType.Interrupted:
                program_interrupted = True
            last_signal_output = output_values[0]
        resumes_count += 1
    return last_signal_output


def get_max_thruster_signal(input_program: str,
                            initial_phase_permutation: str) -> int:
    phase_permutations = itertools.permutations(initial_phase_permutation)

    def to_phase_list(phase: typing.Tuple[typing.Any]) -> typing.List[int]:
        return [int(e) for e in phase]

    max_signal = max(run_program_for_amplifiers(input_program, to_phase_list(phase))
                     for phase in phase_permutations)
    return max_signal


class Tests(unittest.TestCase):
    def run_program_check_output(self: unittest.TestCase,
                                 input_program: str,
                                 input_values: typing.List[int],
                                 expected_output_values: typing.List[int]):
        output_values = []
        run_program_str(input_program, input_values, output_values)
        self.assertEqual(output_values, expected_output_values)

    def assert_max_thrust(self,
                          input_program: str,
                          max_thrust: int,
                          initial_phase_permutation: str = "01234"):
        signal = get_max_thruster_signal(input_program, initial_phase_permutation)
        self.assertEqual(signal, max_thrust)

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

        self.assert_max_thrust("3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0", 43210)
        self.assert_max_thrust("3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0", 54321)
        self.assert_max_thrust("3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,"
                               "31,4,31,99,0,0,0", 65210)

        self.assert_max_thrust("3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5",
                               139629729,
                               initial_phase_permutation="56789")

        self.assert_max_thrust("3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,"
                               "53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,"
                               "0,10",
                               18216,
                               initial_phase_permutation="56789")


def part1():
    input_program = get_file_contents()
    max_signal = get_max_thruster_signal(input_program, initial_phase_permutation="01234")
    print(max_signal)
    assert max_signal == 99376


def part2():
    input_program = get_file_contents()
    max_signal = get_max_thruster_signal(input_program, initial_phase_permutation="56789")
    print(max_signal)
    assert max_signal == 8754464


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
