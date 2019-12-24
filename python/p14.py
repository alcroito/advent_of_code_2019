import os
import unittest
import typing
import math
import collections


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "d14.txt")
    with open(file_path, "r") as f:
        lines = f.read()
    return lines


ChemicalName = str
ProductionAmount = int
AmountAndChemical = typing.Tuple[int, ChemicalName]
Requirements = typing.List[AmountAndChemical]
Reaction = typing.Tuple[ProductionAmount, Requirements]
Reactions = typing.Dict[ChemicalName, Reaction]
CurrentChemicalAmounts = typing.MutableMapping[ChemicalName, int]


def str_to_chemical_amount(s: str) -> AmountAndChemical:
    s_split = s.split(" ")
    return int(s_split[0]), s_split[1]


def get_fuel_amount_to_be_produced(r: Reactions) -> typing.Optional[AmountAndChemical]:
    for chemical in r.keys():
        if chemical == "FUEL":
            return r[chemical][0], chemical
    return None


def str_ro_reactions(reactions_input_str: str) -> Reactions:
    reactions: Reactions = {}

    reaction_lines = reactions_input_str.strip().splitlines(keepends=False)
    for reaction_line in reaction_lines:
        requirements_str, produces_chemical_str = reaction_line.strip().split(" => ")
        produces_chemical = str_to_chemical_amount(produces_chemical_str)

        requirements_split = requirements_str.split(", ")
        requirements = [str_to_chemical_amount(r) for r in requirements_split]
        reaction = produces_chemical[0], requirements
        reactions[produces_chemical[1]] = reaction

    return reactions


def get_chemical_requirements(r: Reactions,
                              unused_chemicals: CurrentChemicalAmounts,
                              chemical_amount: AmountAndChemical) -> CurrentChemicalAmounts:
    needed_amount, chemical = chemical_amount
    if chemical == "ORE":
        return {}

    unused_amount = unused_chemicals[chemical]
    if unused_amount >= needed_amount:
        unused_chemicals[chemical] -= needed_amount
        return {}

    production_amount, reaction_requirements = r[chemical]

    reaction_multiplier = 1
    if (production_amount + unused_amount) < needed_amount:
        reaction_multiplier = math.ceil((needed_amount - unused_amount) / production_amount)
    reaction_requirements = {r_chemical: r_amount * reaction_multiplier
                             for r_amount, r_chemical in reaction_requirements}

    unused_chemicals[chemical] = (production_amount * reaction_multiplier + unused_amount) - needed_amount
    return reaction_requirements


def merge_chemical_requirements(current_requirements: CurrentChemicalAmounts, new_requirements: CurrentChemicalAmounts):
    for chemical, amount in new_requirements.items():
        if chemical in current_requirements:
            current_requirements[chemical] += amount
        else:
            current_requirements[chemical] = amount


def get_next_non_ore_chemical(current_chemicals: CurrentChemicalAmounts) -> typing.Optional[ChemicalName]:
    for k in current_chemicals.keys():
        if k != "ORE":
            return k
    return None


def get_ore_for_fuel(reactions_str: str) -> int:
    r = str_ro_reactions(reactions_str)
    return get_ore_for_fuel_helper(r)


def get_ore_for_fuel_helper(r: Reactions) -> int:
    fuel_amount, fuel_key = get_fuel_amount_to_be_produced(r)
    assert fuel_key
    unused_chemicals = collections.defaultdict(lambda: 0)
    current_chemical_amounts = get_chemical_requirements(r, unused_chemicals, (fuel_amount, fuel_key))
    while len(current_chemical_amounts) != 1:
        chemical = get_next_non_ore_chemical(current_chemical_amounts)
        amount = current_chemical_amounts[chemical]
        del current_chemical_amounts[chemical]
        new_requirements = get_chemical_requirements(r, unused_chemicals, (amount, chemical))
        merge_chemical_requirements(current_chemical_amounts, new_requirements)

    needed_ore = current_chemical_amounts[next(iter(current_chemical_amounts))]
    return needed_ore


def set_fuel_requirement(r: Reactions, fuel_amount: int) -> Reactions:
    chemical = "FUEL"
    new_reactions = dict(r)
    amount, requirements = r[chemical]
    new_requirements = [(r_amount * fuel_amount, r_chemical)
                        for r_amount, r_chemical in requirements]
    new_reactions[chemical] = (fuel_amount, new_requirements)
    return new_reactions


def bisect_max_fuel(reactions_str: str) -> int:
    r = str_ro_reactions(reactions_str)

    available_ore = 1000000000000
    max_fuel_heuristic = available_ore

    low = 1
    high = max_fuel_heuristic

    max_fuel = 1

    while low <= high:
        mid = math.floor((low + high) / 2)
        new_reactions = set_fuel_requirement(r, mid)
        needed_ore = get_ore_for_fuel_helper(new_reactions)
        if needed_ore > available_ore:
            high = mid - 1
        elif mid > max_fuel:
            low = mid + 1
            max_fuel = mid

    return max_fuel


def part1():
    input_reactions = get_file_contents()
    ore_amount = get_ore_for_fuel(input_reactions)
    assert ore_amount == 783895


def part2():
    input_reactions = get_file_contents()
    max_fuel = bisect_max_fuel(input_reactions)
    print(max_fuel)
    assert max_fuel == 1896688


class Tests(unittest.TestCase):
    def test_samples(self):
        ore_amount = get_ore_for_fuel("""
10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL""")
        self.assertEqual(ore_amount, 31)

        ore_amount = get_ore_for_fuel("""
9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL""")
        self.assertEqual(ore_amount, 165)

        ore_amount = get_ore_for_fuel("""
10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL""")
        self.assertEqual(ore_amount, 31)

        ore_amount = get_ore_for_fuel("""
157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""")
        self.assertEqual(ore_amount, 13312)

        ore_amount = get_ore_for_fuel("""
2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF""")
        self.assertEqual(ore_amount, 180697)

        ore_amount = get_ore_for_fuel("""
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX""")
        self.assertEqual(ore_amount, 2210736)

        max_fuel = bisect_max_fuel("""
157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""")
        self.assertEqual(max_fuel, 82892753)

        max_fuel = bisect_max_fuel("""
2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF""")
        self.assertEqual(max_fuel, 5586022)

        max_fuel = bisect_max_fuel("""
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX""")
        self.assertEqual(max_fuel, 460664)


if __name__ == '__main__':
    part1()
    part2()
    unittest.main()
