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
}
