import os
import functools
import operator
import typing
import enum
import collections


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d11.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


def get_int_code_instructions(line: str) -> typing.Dict[int, int]:
    return collections.defaultdict(int, {i: int(x) for i, x in enumerate(line.strip().split(","))})


class Operation(enum.IntEnum):
    Halt = 99
    Add = 1
    Multiply = 2
    Input = 3
    Output = 4
    JumpIfTrue = 5
    JumpIfFalse = 6
    LessThan = 7
    Equals = 8
    AdjustRelativeBase = 9


class ParameterType(enum.Enum):
    Read = 1
    Write = 2


operation_param_types = {
    Operation.Halt: [],
    Operation.Add: [ParameterType.Read, ParameterType.Read, ParameterType.Write],
    Operation.Multiply: [ParameterType.Read, ParameterType.Read, ParameterType.Write],
    Operation.Input: [ParameterType.Write],
    Operation.Output: [ParameterType.Read],
    Operation.JumpIfTrue: [ParameterType.Read, ParameterType.Read],
    Operation.JumpIfFalse: [ParameterType.Read, ParameterType.Read],
    Operation.LessThan: [ParameterType.Read, ParameterType.Read, ParameterType.Write],
    Operation.Equals: [ParameterType.Read, ParameterType.Read, ParameterType.Write],
    Operation.AdjustRelativeBase: [ParameterType.Read],
}


def decode_instruction(instruction: int) -> typing.Tuple[Operation, typing.List[int]]:
    op = Operation(instruction % 100)
    instruction //= 100

    p_modes = []
    param_count = len(operation_param_types[op])
    while param_count > 0:
        p_modes.append(instruction % 10)
        instruction //= 10
        param_count -= 1

    return op, p_modes


operators = {
    Operation.Add: operator.add,
    Operation.Multiply: operator.mul,
    Operation.JumpIfTrue: operator.ne,
    Operation.JumpIfFalse: operator.eq,
    Operation.LessThan: operator.lt,
    Operation.Equals: operator.eq
}


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
        self._relative_base = None

    def __str__(self):
        s = "ip {} s {} m {}".format(self.ip, self.state, self.memory)
        return s

    @staticmethod
    def create(memory: typing.Dict[int, int],
               ip: int,
               relative_base: int = 0,
               state_type: ProgramStateType = ProgramStateType.Created):
        s = ProgramState()
        s._state_type = state_type
        s._memory = memory
        s._ip = ip
        s._relative_base = relative_base
        return s

    @property
    def state(self) -> ProgramStateType:
        return self._state_type

    @state.setter
    def state(self, value):
        self._state_type = value

    @property
    def memory(self) -> typing.Dict[int, int]:
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

    @property
    def relative_base(self) -> int:
        return self._relative_base

    @relative_base.setter
    def relative_base(self, value):
        self._relative_base = value


class ParameterMode(enum.IntEnum):
    Position = 0
    Immediate = 1
    RelativeToBase = 2


def read_memory_value(p: ProgramState,
                      value: int,
                      mode: int) -> int:
    if mode == ParameterMode.Position:
        return p.memory[value]
    elif mode == ParameterMode.Immediate:
        return value
    elif mode == ParameterMode.RelativeToBase:
        return p.memory[p.relative_base + value]
    raise RuntimeError("Invalid read parameter mode: {}.".format(mode))


def get_write_address(p: ProgramState,
                      value: int,
                      mode: int) -> int:
    if mode == ParameterMode.Position:
        return value
    elif mode == ParameterMode.RelativeToBase:
        return p.relative_base + value
    raise RuntimeError("Can't write to {} in immediate mode.".format(value))


param_type_to_function = {
    ParameterType.Read: read_memory_value,
    ParameterType.Write: get_write_address
}


def get_params(p: ProgramState,
               op: Operation,
               p_modes: typing.List[int],
               ) -> typing.List[int]:
    params = [param_type_to_function[operation_param_types[op][i]](p,
                                                                   p.memory[p.ip + 1 + i],
                                                                   p_mode)
              for i, p_mode in enumerate(p_modes)]
    return params


def run_instruction(p: ProgramState,
                    input_values: typing.List[int],
                    output_values: typing.List[int]
                    ) -> InstructionResult:
    instruction = p.memory[p.ip]
    op, p_modes = decode_instruction(instruction)

    if op == Operation.Halt:  # Halt
        return InstructionResult.halt()
    elif op == Operation.Add or op == Operation.Multiply:  # Add or multiply x, y into z
        input_1, input_2, output_address = get_params(p, op, p_modes)
        p.memory[output_address] = functools.reduce(operators[op], [input_1, input_2])
        return InstructionResult.advance_ip(4)
    elif op == Operation.Input:  # Input into x
        # No input values, interrupt program, save state, allow to resume
        # later.
        if not input_values:
            return InstructionResult.interrupt()
        output_address, = get_params(p, op, p_modes)
        p.memory[output_address] = input_values.pop(0)
        return InstructionResult.advance_ip(2)
    elif op == Operation.Output:  # Output into x
        output_value, = get_params(p, op, p_modes)
        output_values.append(output_value)
        return InstructionResult.advance_ip(2)
    elif op == Operation.JumpIfTrue or op == Operation.JumpIfFalse:  # If x != 0 or x == 0, jump to y address
        input_1, input_2 = get_params(p, op, p_modes)

        if operators[op](input_1, 0):
            return InstructionResult.advance_ip(input_2 - p.ip)
        return InstructionResult.advance_ip(3)
    elif op == Operation.LessThan or op == Operation.Equals:  # If x < y or x == y, z = 1, otherwise z = 0
        input_1, input_2, output_address = get_params(p, op, p_modes)

        if operators[op](input_1, input_2):
            p.memory[output_address] = 1
        else:
            p.memory[output_address] = 0
        return InstructionResult.advance_ip(4)
    elif op == Operation.AdjustRelativeBase:  # Adjust relative base by + x
        input_1, = get_params(p, op, p_modes)
        p.relative_base += input_1
        return InstructionResult.advance_ip(2)


def resume_program_helper(p: ProgramState,
                          input_values: typing.List[int],
                          output_values: typing.List[int]
                          ) -> ProgramState:

    p.state = ProgramStateType.Running
    while p.ip < len(p.memory):
        result = run_instruction(p, input_values, output_values)
        result_type = result.type()
        if result_type == InstructionResultType.AdvanceIP:
            p.ip += result.value()
        elif result_type == InstructionResultType.Halt:
            p.state = ProgramStateType.Halted
            break
        elif result_type == InstructionResultType.Interrupt:
            p.state = ProgramStateType.Interrupted
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


class Direction(enum.IntEnum):
    U = 0
    R = 1
    D = 2
    L = 3


direction_dict = {
    Direction.U: (0, 1),
    Direction.R: (1, 0),
    Direction.D: (0, -1),
    Direction.L: (-1, 0),
}


def move(location: typing.Tuple[int, int], direction: typing.Tuple[int, int]) -> typing.Tuple[int, int]:
    l_x, l_y = location
    d_x, d_y = direction
    return l_x + d_x, l_y + d_y


def output_to_rotation(o: int) -> int:
    if o == 0:
        return -1
    elif o == 1:
        return 1
    else:
        raise Exception("Invalid direction.")


def count_paints(starting_color: int) -> typing.Tuple[int, typing.List[typing.Tuple]]:
    d = collections.defaultdict(lambda: 0)
    d[(0, 0)] = starting_color
    robot_location = (0, 0)

    current_direction = Direction.U
    visited_panels = set()
    input_program = get_file_contents()
    vm = create_program_str(input_program)

    while True:
        input_values = [d[robot_location]]
        output_values = []
        resume_program(vm, input_values, output_values)

        if vm.state == ProgramStateType.Halted:
            break

        visited_panels.add(robot_location)

        new_color = output_values[0]
        d[robot_location] = new_color

        new_direction = (current_direction + output_to_rotation(output_values[1])) % 4
        current_direction = new_direction
        robot_location = move(robot_location, direction_dict[current_direction])

    return len(visited_panels), list([coords for coords, color in d.items() if color == 1])


def part1():
    r, _ = count_paints(0)
    assert r == 1686


def part2():
    visited_count, coords = count_paints(1)
    print(visited_count)
    min_x = min([x for x, y in coords])
    min_y = min([y for x, y in coords])
    coords_adjusted = [(x - min_x, y - min_y) for x, y in coords]
    max_x = max([x for x, y in coords_adjusted])
    max_y = max([y for x, y in coords_adjusted])
    coords_set = set(coords_adjusted)

    for r in range(max_y + 1, -1, - 1):
        for c in range(0, max_x + 1):
            if (c, r) in coords_set:
                print("#", end="")
            else:
                print(" ", end="")
        print("")


if __name__ == '__main__':
    part1()
    part2()
