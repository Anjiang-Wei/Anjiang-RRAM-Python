import numpy as np
import pprint
import scipy.stats as stats
# names = ['addr', 'nreads', 'nsets', 'nresets', 'rf', 'if', 'rlo', 'rhi', 'success', 'attempts1', 'attempts2']

# 0 addr
# 4 rf (write final)
# 6 rlo (range low)
# 7 rhi (range high)
# 8 success

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    # print(len(x), p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True

def init(filename, reverse):
    data = []
    addr_list = []
    with open(filename, "r") as fin:
        lines = fin.readlines()
        for i in range(1, len(lines)):
            splitted = lines[i].split()
            addr, write_final, write_low, write_high = int(float(splitted[0])), float(splitted[4]), float(splitted[6]), float(splitted[7])
            if reverse:
                write_final = 1 / write_final
            addr_list.append(addr)
            data.append([write_final, write_low, write_high])
    return data, len(list(set(addr_list)))

def bin(filename, reverse):
    data, cell_num = init(filename, reverse)
    res = {}
    for item in data:
        final, low, high = item
        key_tuple = (low, high)
        if key_tuple not in res.keys():
            res[key_tuple] = []
        res[key_tuple].append(final)
    return res, cell_num

def report_normality(filename, reverse):
    non_normal = 0
    total = 0
    distr_dict, cell_num = bin(filename, reverse)
    for k in distr_dict.keys():
        distribution = distr_dict[k]
        res = normal_test(distribution)
        if res == False:
            non_normal += 1
        total += 1
    print("Resistance" if reverse else "Conductance",
        f"cell_num={cell_num}", f"{non_normal}/{total}={non_normal / total}")


if __name__ == "__main__":
    # obtained from https://github.com/Anjiang-Wei/pin/tree/main/data
    filename = "sdr-4wl-eval-chip2-8k-8-9-20.csv"
    report_normality(filename, True)
    report_normality(filename, False)
