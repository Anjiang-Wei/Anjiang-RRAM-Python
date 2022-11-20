import numpy as np
import pprint
import scipy.stats as stats

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    # print(len(x), p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True

def compute_skew(x):
    return stats.skew(x)

# header:
# addr	timept	g (conductance)  range

def init(model_char, reverse):
    data = []
    basetime_data = {}
    with open("model_" + model_char + ".tsv", "r") as fin:
        lines = fin.readlines()
        for i in range(1, len(lines)):
            addr, timept, conductance, r = lines[i].split()
            addr, timept, conductance, r = int(addr), float(timept), float(conductance), int(r)
            if reverse:
                conductance = 1 / conductance
            data.append([addr, timept, conductance, r])
            if timept == 0:
                basetime_data[addr] = [conductance, r]
    return data, basetime_data

def diff(model_char, reverse):
    data, basetime_data = init(model_char, reverse)
    cell_num = len(list(set(map(lambda x: x[0], data))))
    res = {} # r, timept -> [conductance_diff, ...]
    for item in data:
        addr, timept, conductance, r = item
        if timept == 0:
            continue
        base_conductance, base_r = basetime_data[addr]
        assert base_r == r
        conductance_diff = conductance - base_conductance
        if r not in res.keys():
            res[r] = {}
        if timept not in res[r].keys():
            res[r][timept] = []
        res[r][timept].append(conductance_diff)
    # pprint.pprint(res)
    return res, cell_num

def report_normality(model_char, reverse):
    non_normal = 0
    total = 0
    diff_res, cell_num = diff(model_char, reverse)
    for k1 in diff_res.keys():
        for k2 in diff_res[k1].keys():
            distribution = diff_res[k1][k2]
            if len(distribution) < 8:
                continue
            res = normal_test(distribution)
            if res == False:
                non_normal += 1
            total += 1
    print(f"Model_{model_char}", "Resistance" if reverse else "Conductance",
        f"cell_num={cell_num}", f"{non_normal}/{total}={non_normal / total}")

def report_skew(model_char, reverse):
    diff_res, _ = diff(model_char, reverse)
    total = 0
    number = 0
    for k1 in diff_res.keys():
        for k2 in diff_res[k1].keys():
            distribution = diff_res[k1][k2]
            res = compute_skew(distribution)
            total += res
            number += 1
    print(f"Model_{model_char}", "Resistance" if reverse else "Conductance", "Average Skewness",  total / number)

if __name__ == "__main__":
    report_normality("A", True)
    report_normality("A", False)
    report_normality("B", True)
    report_normality("B", False)
    report_normality("C", True)
    report_normality("C", False)
    print("=========================")
    report_skew("A", True)
    report_skew("A", False)
    report_skew("B", True)
    report_skew("B", False)
    report_skew("C", True)
    report_skew("C", False)
'''
Model_A Resistance cell_num=16384 212/231=0.9177489177489178
Model_A Conductance cell_num=16384 211/231=0.9134199134199135
Model_B Resistance cell_num=32768 189/198=0.9545454545454546
Model_B Conductance cell_num=32768 185/198=0.9343434343434344
Model_C Resistance cell_num=16292 164/165=0.9939393939393939
Model_C Conductance cell_num=16292 159/165=0.9636363636363636
=========================
Model_A Resistance Average Skewness 2.2799583322769856
Model_A Conductance Average Skewness 0.29452399015241554
Model_B Resistance Average Skewness 2.9501168306345167
Model_B Conductance Average Skewness -0.6273118495727644
Model_C Resistance Average Skewness 4.570113122585145
Model_C Conductance Average Skewness -0.10483631263440152
'''