use std::fs;

fn get_data_from_file(name: &str) -> Option<String> {
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

fn lines_to_ints(contents: &str) -> Vec<i32> {
    let mut ints = Vec::new();
    for s in contents.split_ascii_whitespace() {
        ints.push(s.parse::<i32>().unwrap());
    }
    ints
}

fn compute_module_fuel(module_mass: i32) -> i32 {
    (module_mass as f64 / 3.0).floor() as i32 - 2
}

fn compute_module_fuel_realistic(module_mass: i32) -> i32 {
    let mut fuel = compute_module_fuel(module_mass);
    let mut total_fuel: i32 = fuel;
    while fuel > 0 {
        fuel = compute_module_fuel(fuel);
        if fuel > 0 {
            total_fuel += fuel;
        }
    }
    total_fuel
}

fn compute_module_fuel_realistic_with_wizardry(ints: &Vec<i32>) -> i32 {
    let result = ints
        .iter()
        .flat_map(|&mass| {
            std::iter::successors(Some(mass), |&m| Some(compute_module_fuel(m)))
                .take_while(|&m| m > 0)
                .skip(1)
        })
        .sum();
    result
}

fn solve_p1() {
    let data = get_data_from_file("d1").unwrap();
    let ints = lines_to_ints(&data);
    let sum: i32 = ints.iter().map(|&x| compute_module_fuel(x)).sum();
    println!("Part 1 result is: {}", sum);
    assert_eq!(sum, 3358992);
}

fn solve_p2() {
    let data = get_data_from_file("d1").unwrap();
    let ints = lines_to_ints(&data);
    let sum: i32 = ints.iter().map(|&x| compute_module_fuel_realistic(x)).sum();
    println!("Part 2 result is: {}", sum);
    assert_eq!(sum, 5035632);

    let sum: i32 = compute_module_fuel_realistic_with_wizardry(&ints);
    println!("Part 2 result with wizardry is: {}", sum);
    assert_eq!(sum, 5035632);
}

#[test]
fn test_fuel_p1() {
    assert_eq!(compute_module_fuel(12), 2);
    assert_eq!(compute_module_fuel(14), 2);
    assert_eq!(compute_module_fuel(1969), 654);
    assert_eq!(compute_module_fuel(100756), 33583);
}

#[test]
fn test_fuel_p2() {
    assert_eq!(compute_module_fuel_realistic(14), 2);
    assert_eq!(compute_module_fuel_realistic(1969), 966);
    assert_eq!(compute_module_fuel_realistic(100756), 50346);
}

fn main() {
    solve_p1();
    solve_p2();
}
