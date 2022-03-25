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
    assert all_error >= 0 and all_error <= 1
    return all_error

def getnumbers(filename):
    real_num = []
    imag_num = []
    with open(filename, "r") as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            real, imag = map(float, line.split(" "))
            real_num.append(real)
            imag_num.append(imag)
    return real_num, imag_num

def diff():
    golden1, golden2 = getnumbers("output")
    mutate1, mutate2 = getnumbers("output0")
    rel_diff1 = relative_diff(golden1, mutate1)
    rel_diff2 = relative_diff(golden2, mutate2)
    return (rel_diff1 + rel_diff2) / 2

if __name__ == "__main__":
    print(diff())
