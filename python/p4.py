import unittest
import typing


def is_valid_password(p: str, p_range: typing.Tuple[int, int],
                      strict_doubles: bool = False) -> bool:
    if len(p) != 6:
        return False

    p_int = int(p)
    if (p_int < p_range[0]) or (p_int > p_range[1]):
        return False

    has_double_digits = False

    same_digit_count = 1
    prev_digit = int(p[0])

    def check_if_has_double_digits():
        nonlocal has_double_digits
        if strict_doubles and same_digit_count == 2:
            has_double_digits = True
        elif not strict_doubles and same_digit_count > 1:
            has_double_digits = True

    for i in range(1, 6):
        p_i_int = int(p[i])

        if p_i_int < prev_digit:
            return False

        if prev_digit != p_i_int:
            check_if_has_double_digits()
            same_digit_count = 0

        prev_digit = p_i_int
        same_digit_count += 1

    check_if_has_double_digits()
    if not has_double_digits:
        return False

    return True


def count_valid_passwords(p_range: typing.Tuple[int, int], strict_doubles: bool = False):
    valid_passwords_count = 0
    for p in range(p_range[0], p_range[1]):
        if is_valid_password(str(p), p_range, strict_doubles):
            valid_passwords_count += 1

    return valid_passwords_count


class Tests(unittest.TestCase):
    def test_samples(self):
        self.assertEqual(is_valid_password("111111", (100000, 200000)), True)
        self.assertEqual(is_valid_password("122345", (100000, 200000)), True)
        self.assertEqual(is_valid_password("111123", (100000, 200000)), True)
        self.assertEqual(is_valid_password("135679", (100000, 200000)), False)
        self.assertEqual(is_valid_password("111121", (100000, 200000)), False)
        self.assertEqual(is_valid_password("223450", (100000, 500000)), False)
        self.assertEqual(is_valid_password("222222", (100000, 200000)), False)
        self.assertEqual(is_valid_password("123789", (100000, 200000)), False)

        self.assertEqual(is_valid_password("112233", (100000, 200000), strict_doubles=True), True)
        self.assertEqual(is_valid_password("123444", (100000, 200000), strict_doubles=True), False)
        self.assertEqual(is_valid_password("111122", (100000, 200000), strict_doubles=True), True)


def part1():
    count = count_valid_passwords((124075, 580769))
    print(count)
    assert count == 2150


def part2():
    count = count_valid_passwords((124075, 580769), strict_doubles=True)
    print(count)
    assert count == 1462


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
