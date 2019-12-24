import os

try:
    from python.utils.intcode import VM
except ImportError:
    try:
        from utils.intcode import VM
    except ImportError:
        VM = None


def get_file_contents() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "..", "data", "easter_egg.txt")
    with open(file_path, "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return lines[0]


def easter_egg():
    vm = VM(get_file_contents())
    while not vm.halted():
        vm.resume()
        for c in vm.output():
            print(chr(c), end="")


if __name__ == '__main__':
    easter_egg()
