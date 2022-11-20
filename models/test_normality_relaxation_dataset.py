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
    return res

def report_normality(model_char, reverse):
    non_normal = 0
    total = 0
    diff_res = diff(model_char, reverse)
    for k1 in diff_res.keys():
        for k2 in diff_res[k1].keys():
            distribution = diff_res[k1][k2]
            if len(distribution) < 8:
                continue
            res = normal_test(distribution)
            if res == False:
                non_normal += 1
            total += 1
    print(f"Model_{model_char}", "Resistance" if reverse else "Conductance", non_normal, total, non_normal / total)

if __name__ == "__main__":
    report_normality("A", True)
    report_normality("A", False)
    report_normality("B", True)
    report_normality("B", False)
    report_normality("C", True)
    report_normality("C", False)
'''
Model_A Resistance 212 231 0.9177489177489178
Model_A Conductance 211 231 0.9134199134199135
Model_B Resistance 189 198 0.9545454545454546
Model_B Conductance 185 198 0.9343434343434344
Model_C Resistance 164 165 0.9939393939393939
Model_C Conductance 159 165 0.9636363636363636
'''