def relative_diff(golden, mutated):
    assert len(golden) == len(mutated)
    all_error = 0
    for i in range(len(golden)):
        err = golden[i] - mutated[i]
        if golden[i] == 0: # avoid division by 0
            continue
        rel_err = abs(err / golden[i])
        all_error += rel_err
    all_error = all_error / len(golden)
    return all_error

def get_max_min(all_num):
    maxnum, minnum = -1e10, 1e10
    for item in all_num:
        maxnum = max(maxnum, item)
        minnum = min(minnum, item)
    return maxnum, minnum

def get_double_numbers(filename):
    all_num = []
    with open(filename, "r") as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            num1, num2 = map(float, line.split())
            all_num.append(num1)
            all_num.append(num2)
    return all_num

def getnumbers(filename):
    all_num = []
    with open(filename, "r") as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            num = float(line)
            all_num.append(num)
    return all_num

def diff():
    num1 = getnumbers("output")
    num2 = getnumbers("output0")
    diff = relative_diff(num1, num2)
    return diff

if __name__ == "__main__":
    print(diff())
    print(get_max_min(get_double_numbers("input")))
