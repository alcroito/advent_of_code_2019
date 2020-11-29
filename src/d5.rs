use advent::helpers;
use advent::int_code_computer::Computer;

fn solve_p1() {
    let data = helpers::get_data_from_file("d5").unwrap();
    let ints = helpers::csv_string_to_ints(&data);

    let mut c = Computer::new(&helpers::ints_to_longs(&ints));
    c.add_input_values(&[1]);
    c.run();
    let output = c.get_output_values();
    println!("Part 1 result is: {:?}", output);
    for i in 0..8 {
        assert_eq!(output[i], 0);
    }

    assert_eq!(output[9], 13547311);
}

fn solve_p2() {
    let data = helpers::get_data_from_file("d5").unwrap();
    let ints = helpers::csv_string_to_ints(&data);

    let mut c = Computer::new(&helpers::ints_to_longs(&ints));
    c.add_input_values(&[5]);
    c.run();
    let output = c.get_output_values();
    println!("Part 2 result is: {:?}", output);

    assert_eq!(output[0], 236453);
}

fn main() {
    solve_p1();
    solve_p2();
}
