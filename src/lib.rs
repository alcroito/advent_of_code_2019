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
            },
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
    #[derive(Debug)]
    enum OpResult {
        Halt,
        AdvanceIP(i64)
    }

    enum OpCode {
        Add,
        Multiply,
        Halt,
    }

    #[derive(Debug)]
    pub struct Computer {
        memory: Vec<i64>,
        ip: i64,
        debug: bool,
    }

    impl Computer {
        pub fn new(m: &[i64]) -> Computer {
            Computer {
                memory: m.to_vec(),
                ip: 0,
                debug: false,
            }
        }

        pub fn run(&mut self) {
            loop {
                debug_assert_ge!(self.ip, 0);
                debug_assert_lt!(self.ip as usize, self.memory.len());

                let op_code = self.get_next_op();
                let result = self.run_instruction(op_code);
                if self.debug {
                    println!("Op result is: {:?}", result);
                }
                match result {
                    OpResult::AdvanceIP(delta) => self.ip += delta,
                    OpResult::Halt => break,
                }
            }
        }

        fn get_next_op(&self) -> OpCode {
            OpCode::from(self.memory[self.ip as usize] as i8).unwrap()
        }

        pub fn get_value_at_address(&self, address: i64) -> i64 {
            self.memory[address as usize]
        }

        pub fn set_value_at_address(&mut self, address: i64, value: i64) {
            self.memory[address as usize] = value
        }

        fn read_input_value(&self, addr: i64) -> i64 {
            let address_to_read = self.get_value_at_address(addr) as usize;
            self.memory[address_to_read]
        }

        fn read_output_address(&self, addr: i64) -> usize {
            self.get_value_at_address(addr) as usize
        }

        #[allow(dead_code)]
        fn get_memory(&self) -> &Vec<i64> {
            &self.memory
        }

        fn run_instruction(&mut self, op_code: OpCode) -> OpResult {
            match op_code {
                OpCode::Add => {
                    let in1 = self.read_input_value(self.ip + 1);
                    let in2 = self.read_input_value(self.ip + 2);
                    let out_addr = self.read_output_address(self.ip + 3);
                    let result = in1 + in2;
                    self.memory[out_addr] = result;
                    if self.debug {
                        println!("Adding {}+{}={} at address {}", in1, in2, result, out_addr);
                    }
                    OpResult::AdvanceIP(4)
                },
                OpCode::Multiply => {
                    let in1 = self.read_input_value(self.ip + 1);
                    let in2 = self.read_input_value(self.ip + 2);
                    let out_addr = self.read_output_address(self.ip + 3);
                    let result = in1 * in2;
                    self.memory[out_addr] = result;
                    if self.debug {
                        println!("Multiplying {}+{}={} at address {}", in1, in2, result, out_addr);
                    }
                    OpResult::AdvanceIP(4)
                },
                OpCode::Halt => { 
                    if self.debug {
                        println!("Halting!");
                    }
                    OpResult::Halt
                },
            }
        }
    }

    impl OpCode {
        fn from(op_code: i8) -> Option<OpCode> {
            match op_code {
                1 => Some(OpCode::Add),
                2 => Some(OpCode::Multiply),
                99 => Some(OpCode::Halt),
                _ => None
            }
        }

        #[allow(dead_code)]
        fn to_int(&self) -> i8 {
            match self {
                OpCode::Add => 1,
                OpCode::Multiply => 2,
                OpCode::Halt => 99,
            }
        }
    }

    #[allow(dead_code)]
    fn check_run_program(input_memory: &[i64], output_memory: &[i64]) {
        let mut c = Computer::new(input_memory);
        c.run();
        assert_eq!(*c.get_memory(), output_memory);
    }

    #[test]
    fn test_computer_p2() {
        check_run_program(
            &[1,9,10,3,2,3,11,0,99,30,40,50],
            &[3500,9,10,70,2,3,11,0,99,30,40,50]
        );
        check_run_program(
            &[1,0,0,0,99],
            &[2,0,0,0,99]
        );
        check_run_program(
            &[2,3,0,3,99],
            &[2,3,0,6,99]
        );
        check_run_program(
            &[2,4,4,5,99,0],
            &[2,4,4,5,99,9801]
        );
        check_run_program(
            &[1,1,1,4,99,5,6,0,99],
            &[30,1,1,4,2,5,6,0,99]
        );
    }
}
