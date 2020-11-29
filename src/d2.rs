use advent::helpers;
use advent::int_code_computer::Computer;

fn solve_p1() {
    let data = helpers::get_data_from_file("d2").unwrap();
    let ints = helpers::csv_string_to_ints(&data);

    let mut c = Computer::new(&helpers::ints_to_longs(&ints));
    c.set_value_at_address(1, 12);
    c.set_value_at_address(2, 2);
    c.run();
    let result = c.get_value_at_address(0);
    println!("Part 1 result is: {:?}", result);
    assert_eq!(result, 4570637);
}

fn solve_p2() {
    let data = helpers::get_data_from_file("d2").unwrap();
    let ints = helpers::csv_string_to_ints(&data);

    let output_to_look_for: i64 = 19690720;
    for noun in 0..99 {
        for verb in 0..99 {
            let mut c = Computer::new(&helpers::ints_to_longs(&ints));
            c.set_value_at_address(1, noun);
            c.set_value_at_address(2, verb);
            c.run();
            let result = c.get_value_at_address(0);
            if result == output_to_look_for {
                let final_result = 100 * noun + verb;
                println!("Part 2 result is: {}", final_result);
                assert_eq!(final_result, 5485);
                return;
            }
        }
    }
}

fn main() {
    solve_p1();
    solve_p2();
}
