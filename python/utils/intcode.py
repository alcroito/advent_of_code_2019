import functools
import operator
import typing
import enum
import collections
import unittest


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


class VM(object):
    def __init__(self, input_program: str):
        self._program = create_program_str(input_program)
        self._input_values = []
        self._output_values = []

    def run(self, input_values=None):
        return self.resume(input_values)

    def resume(self, input_values=None):
        if input_values is None:
            self._input_values = []
        else:
            self._input_values = input_values
        self._output_values = []
        resume_program(self._program, self._input_values, self._output_values)
        return self.output()

    def write_memory(self, i: int, value: int):
        self._program.memory[i] = value

    def output(self):
        return self._output_values

    def state(self):
        return self._program.state

    def halted(self):
        return self._program.state == ProgramStateType.Halted

    def interrupted(self):
        return self._program.state == ProgramStateType.Interrupted

    def program(self):
        return self._program


class Tests(unittest.TestCase):
    def run_program_check_output(self: unittest.TestCase,
                                 input_program: str,
                                 input_values: typing.List[int],
                                 expected_output_values: typing.List[int]):
        output_values = []
        run_program_str(input_program, input_values, output_values)
        self.assertEqual(output_values, expected_output_values)

    def test_samples(self):
        self.assertEqual(decode_instruction(1002), (2, [0, 1, 0]))
        self.assertEqual(decode_instruction(99), (99, []))
        self.assertEqual(decode_instruction(103), (3, [1]))
        self.assertEqual(decode_instruction(3), (3, [0]))
        self.assertEqual(decode_instruction(4), (4, [0]))

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

        self.run_program_check_output("109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99",
                                      [],
                                      [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99])

        self.run_program_check_output("1102,34915192,34915192,7,4,7,99,0",
                                      [],
                                      [1219070632396864])

        self.run_program_check_output("104,1125899906842624,99",
                                      [],
                                      [1125899906842624])


if __name__ == '__main__':
    unittest.main()
