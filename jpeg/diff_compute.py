def root_mean_square(a1, a2):
    assert len(a1) == len(a2)
    res = 0
    for i in range(0, len(a1)):
        res += (a1[i] - a2[i]) * (a1[i] - a2[i])
    res = res / len(a1)
    return res ** 0.5

def getnumbers(filename):
    all_num = []
    with open(filename, "r") as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            num = int(line)
            all_num.append(num)
    return all_num

def diff(f1, f2):
    num1 = getnumbers(f1)
    num2 = getnumbers(f2)
    diff = root_mean_square(num1, num2)
    return diff

if __name__ == "__main__":
    print(diff("1_output", "1_output0"))
