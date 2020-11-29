#[macro_use]
extern crate more_asserts;

pub mod helpers {
    use std::fs;
    pub fn get_data_from_file(name: &str) -> Option<String> {
        let path = format!("data/{}.txt", name);

        let contents = match fs::read_to_string(path) {
            Ok(s) => Some(s),
            Err(e) => {
                println!("Error reading data: {}", e);
                None
            }
        };
        contents
    }

    pub fn lines_to_ints(contents: &str) -> Vec<i32> {
        let mut ints = Vec::new();
        for s in contents.split_ascii_whitespace() {
            ints.push(s.parse::<i32>().unwrap());
        }
        ints
    }

    pub fn ints_to_longs(ints: &Vec<i32>) -> Vec<i64> {
        let longs: Vec<i64>;
        longs = ints.iter().map(|&x| x as i64).collect();
        longs
    }

    pub fn csv_string_to_ints(contents: &str) -> Vec<i32> {
        let mut ints = Vec::new();
        for s in contents.split(",") {
            ints.push(s.trim().parse::<i32>().unwrap());
        }
        ints
    }
}

pub mod int_code_computer {
    use std::collections::VecDeque;

    #[derive(Debug)]
    enum InstrResult {
        Halt,
        AdvanceIP(i64),
    }

    #[derive(PartialEq, Debug)]
    enum ParamMode {
        Position,
        Immediate,
    }

    #[derive(PartialEq, Debug)]
    enum Instr {
        Add(ParamMode, ParamMode, ParamMode),
        Multiply(ParamMode, ParamMode, ParamMode),
        Input,
        Output(ParamMode),
        JumpIfTrue(ParamMode, ParamMode),
        JumpIfFalse(ParamMode, ParamMode),
        LessThan(ParamMode, ParamMode),
        Equals(ParamMode, ParamMode),
        Halt,
    }

    #[derive(Debug)]
    pub struct Computer {
        memory: Vec<i64>,
        input_values: VecDeque<i64>,
        output_values: Vec<i64>,
        ip: i64,
        debug: bool,
    }

    impl Computer {
        pub fn new(m: &[i64]) -> Computer {
            Computer {
                memory: m.to_vec(),
                input_values: VecDeque::new(),
                output_values: Vec::new(),
                ip: 0,
                debug: false,
            }
        }

        pub fn add_input_values(&mut self, input: &[i64]) {
            self.input_values.extend(input);
        }

        pub fn get_output_values(&self) -> &[i64] {
            &self.output_values
        }

        pub fn run(&mut self) {
            loop {
                debug_assert_ge!(self.ip, 0);
                debug_assert_lt!(self.ip as usize, self.memory.len());

                let op_code = self.get_next_instr();
                let result = self.run_instruction(op_code);
                if self.debug {
                    println!("Op result is: {:?}", result);
                }
                match result {
                    InstrResult::AdvanceIP(delta) => self.ip += delta,
                    InstrResult::Halt => break,
                }
            }
        }

        fn get_next_instr(&self) -> Instr {
            Instr::from(self.memory[self.ip as usize]).unwrap()
        }

        pub fn get_value_at_address(&self, address: i64) -> i64 {
            self.memory[address as usize]
        }

        pub fn set_value_at_address(&mut self, address: i64, value: i64) {
            self.memory[address as usize] = value
        }

        fn get_value_for_operand(&self, addr: i64, mode: &ParamMode) -> i64 {
            match mode {
                ParamMode::Position => {
                    let address_to_read = self.get_value_at_address(addr);
                    self.get_value_at_address(address_to_read)
                }
                ParamMode::Immediate => self.get_value_at_address(addr),
            }
        }

        fn get_addr_for_memory_write(&self, addr: i64) -> usize {
            self.get_value_at_address(addr) as usize
        }

        fn take_one_input_value(&mut self) -> i64 {
            self.input_values.pop_front().unwrap()
        }

        fn add_output_value(&mut self, value: i64) {
            self.output_values.push(value);
        }

        #[allow(dead_code)]
        fn get_memory(&self) -> &Vec<i64> {
            &self.memory
        }

        fn run_instruction(&mut self, instr: Instr) -> InstrResult {
            match &instr {
                Instr::Add(p1, p2, _) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let out_addr = self.get_addr_for_memory_write(self.ip + 3);
                    let result = in1 + in2;
                    self.set_value_at_address(out_addr as i64, result);
                    if self.debug {
                        println!("Adding {}+{}={} to address {}", in1, in2, result, out_addr);
                    }
                    instr.result(None)
                }
                Instr::Multiply(p1, p2, _) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let out_addr = self.get_addr_for_memory_write(self.ip + 3);
                    let result = in1 * in2;
                    self.set_value_at_address(out_addr as i64, result);
                    if self.debug {
                        println!(
                            "Multiplying {}+{}={} to address {}",
                            in1, in2, result, out_addr
                        );
                    }
                    instr.result(None)
                }
                Instr::Input => {
                    let out_addr = self.get_addr_for_memory_write(self.ip + 1);
                    let value = self.take_one_input_value();
                    self.set_value_at_address(out_addr as i64, value);
                    if self.debug {
                        println!("Adding new input {} to address {}", value, out_addr);
                    }
                    instr.result(None)
                }
                Instr::Output(p1) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    self.add_output_value(in1);
                    if self.debug {
                        println!("Adding new output {}", in1);
                    }
                    instr.result(None)
                }
                Instr::JumpIfTrue(p1, p2) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let mut ip_delta = 3;
                    if in1 != 0 {
                        ip_delta = in2 - self.ip;
                    }
                    if self.debug {
                        println!("Jumping, advancing IP by {}", ip_delta);
                    }
                    instr.result(Some(ip_delta))
                }
                Instr::JumpIfFalse(p1, p2) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let mut ip_delta = 3;
                    if in1 == 0 {
                        ip_delta = in2 - self.ip;
                    }
                    if self.debug {
                        println!("Jumping, advancing IP by {}", ip_delta);
                    }
                    instr.result(Some(ip_delta))
                }
                Instr::LessThan(p1, p2) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let out_addr = self.get_addr_for_memory_write(self.ip + 3);
                    let mut value = 0;
                    if in1 < in2 {
                        value = 1;
                    }
                    self.set_value_at_address(out_addr as i64, value);
                    if self.debug {
                        println!(
                            "Conditional assignment, setting address {} to {}",
                            out_addr, value
                        );
                    }
                    instr.result(None)
                }
                Instr::Equals(p1, p2) => {
                    let in1 = self.get_value_for_operand(self.ip + 1, p1);
                    let in2 = self.get_value_for_operand(self.ip + 2, p2);
                    let out_addr = self.get_addr_for_memory_write(self.ip + 3);
                    let mut value = 0;
                    if in1 == in2 {
                        value = 1;
                    }
                    if self.debug {
                        println!(
                            "Conditional assignment, setting address {} to {}",
                            out_addr, value
                        );
                    }
                    self.set_value_at_address(out_addr as i64, value);
                    instr.result(None)
                }
                Instr::Halt => {
                    if self.debug {
                        println!("Halting!");
                    }
                    instr.result(None)
                }
            }
        }
    }

    impl ParamMode {
        fn from(i: i64) -> Option<ParamMode> {
            match i {
                0 => Some(ParamMode::Position),
                1 => Some(ParamMode::Immediate),
                _ => None,
            }
        }
    }

    impl Instr {
        fn from(instruction: i64) -> Option<Instr> {
            let op_code = instruction % 100;
            let instruction = instruction / 100;

            let mode = instruction % 10;
            let instruction = instruction / 10;
            let p1_mode = ParamMode::from(mode).unwrap();

            let mode = instruction % 10;
            let instruction = instruction / 10;
            let p2_mode = ParamMode::from(mode).unwrap();

            let mode = instruction % 10;
            let p3_mode = ParamMode::from(mode).unwrap();

            match op_code {
                1 => Some(Instr::Add(p1_mode, p2_mode, p3_mode)),
                2 => Some(Instr::Multiply(p1_mode, p2_mode, p3_mode)),
                3 => Some(Instr::Input),
                4 => Some(Instr::Output(p1_mode)),
                5 => Some(Instr::JumpIfTrue(p1_mode, p2_mode)),
                6 => Some(Instr::JumpIfFalse(p1_mode, p2_mode)),
                7 => Some(Instr::LessThan(p1_mode, p2_mode)),
                8 => Some(Instr::Equals(p1_mode, p2_mode)),
                99 => Some(Instr::Halt),
                _ => None,
            }
        }

        fn result(&self, ip_delta: Option<i64>) -> InstrResult {
            match self {
                Instr::Add(..) => InstrResult::AdvanceIP(4),
                Instr::Multiply(..) => InstrResult::AdvanceIP(4),
                Instr::Input => InstrResult::AdvanceIP(2),
                Instr::Output(..) => InstrResult::AdvanceIP(2),
                Instr::JumpIfTrue(..) => InstrResult::AdvanceIP(ip_delta.unwrap()),
                Instr::JumpIfFalse(..) => InstrResult::AdvanceIP(ip_delta.unwrap()),
                Instr::LessThan(..) => InstrResult::AdvanceIP(4),
                Instr::Equals(..) => InstrResult::AdvanceIP(4),
                Instr::Halt => InstrResult::Halt,
            }
        }
    }

    #[allow(dead_code)]
    fn check_run_program(input_memory: &[i64], output_memory: &[i64]) {
        let mut c = Computer::new(input_memory);
        c.run();
        assert_eq!(*c.get_memory(), output_memory);
    }

    #[allow(dead_code)]
    fn check_decoded_instruction(i: i64, expected_i: Instr) {
        let constructed_i = Instr::from(i).unwrap();
        assert_eq!(constructed_i, expected_i);
    }

    #[allow(dead_code)]
    fn check_run_program_output(input_memory: &[i64], input_values: &[i64], output_values: &[i64]) {
        let mut c = Computer::new(input_memory);
        c.add_input_values(input_values);
        c.run();
        assert_eq!(c.get_output_values(), output_values);
    }

    #[test]
    fn test_computer_d2() {
        check_run_program(
            &[1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
            &[3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50],
        );
        check_run_program(&[1, 0, 0, 0, 99], &[2, 0, 0, 0, 99]);
        check_run_program(&[2, 3, 0, 3, 99], &[2, 3, 0, 6, 99]);
        check_run_program(&[2, 4, 4, 5, 99, 0], &[2, 4, 4, 5, 99, 9801]);
        check_run_program(
            &[1, 1, 1, 4, 99, 5, 6, 0, 99],
            &[30, 1, 1, 4, 2, 5, 6, 0, 99],
        );
    }

    #[test]
    fn test_computer_d5() {
        let a = Instr::Multiply(
            ParamMode::Position,
            ParamMode::Immediate,
            ParamMode::Position,
        );
        check_decoded_instruction(1002, a);

        check_decoded_instruction(99, Instr::Halt);

        let a = Instr::Input;
        check_decoded_instruction(11103, a);

        // Comparison tests.
        check_run_program_output(&[3, 0, 4, 0, 99], &[12], &[12]);
        check_run_program_output(&[3, 9, 8, 9, 10, 9, 4, 9, 99, -1, 8], &[8], &[1]);
        check_run_program_output(&[3, 9, 8, 9, 10, 9, 4, 9, 99, -1, 8], &[9], &[0]);
        check_run_program_output(&[3, 9, 7, 9, 10, 9, 4, 9, 99, -1, 8], &[7], &[1]);
        check_run_program_output(&[3, 3, 1108, -1, 8, 3, 4, 3, 99], &[8], &[1]);
        check_run_program_output(&[3, 3, 1107, -1, 8, 3, 4, 3, 99], &[10], &[0]);

        // Jump tests.
        check_run_program_output(
            &[3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, -1, 0, 1, 9],
            &[12],
            &[1],
        );
        check_run_program_output(
            &[3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, -1, 0, 1, 9],
            &[0],
            &[0],
        );
        check_run_program_output(
            &[3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1],
            &[12],
            &[1],
        );
        check_run_program_output(
            &[3, 3, 1105, -1, 9, 1101, 0, 0, 12, 4, 12, 99, 1],
            &[0],
            &[0],
        );

        // Larger example.
        check_run_program_output(
            &[
                3, 21, 1008, 21, 8, 20, 1005, 20, 22, 107, 8, 21, 20, 1006, 20, 31, 1106, 0, 36,
                98, 0, 0, 1002, 21, 125, 20, 4, 20, 1105, 1, 46, 104, 999, 1105, 1, 46, 1101, 1000,
                1, 20, 4, 20, 1105, 1, 46, 98, 99,
            ],
            &[7],
            &[999],
        );

        check_run_program_output(
            &[
                3, 21, 1008, 21, 8, 20, 1005, 20, 22, 107, 8, 21, 20, 1006, 20, 31, 1106, 0, 36,
                98, 0, 0, 1002, 21, 125, 20, 4, 20, 1105, 1, 46, 104, 999, 1105, 1, 46, 1101, 1000,
                1, 20, 4, 20, 1105, 1, 46, 98, 99,
            ],
            &[8],
            &[1000],
        );

        check_run_program_output(
            &[
                3, 21, 1008, 21, 8, 20, 1005, 20, 22, 107, 8, 21, 20, 1006, 20, 31, 1106, 0, 36,
                98, 0, 0, 1002, 21, 125, 20, 4, 20, 1105, 1, 46, 104, 999, 1105, 1, 46, 1101, 1000,
                1, 20, 4, 20, 1105, 1, 46, 98, 99,
            ],
            &[20],
            &[1001],
        );
    }
}
