import numpy as np
import random
import matplotlib.pyplot as plt
import math

model_char = "C14"
diffs = {}
timestamps = []
fixed_timept = 1.0
mini, maxi = 0, 0

def load_param():
    global timestamps, mini, maxi
    with open("../models/conf" + model_char, "r") as fin:
        lines = fin.readlines()
        mini, maxi = map(float, lines[0].split(","))
        for line in lines[1:]:
            # 0.01,8000.0,-81.51795324993691,51.73266256181705,3.450787552253132, ...
            line = list(map(float, line.split(",")))
            t, w_center, diff_list = line[0], line[1], line[2:]
            if t not in diffs.keys():
                diffs[t] = {}
            diffs[t][w_center] = diff_list
        timestamps = sorted(list(diffs.keys()))

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)

def get_distribution(r0, t, N):
    '''
    Initial value (t=0) is r0, after time=t elapses
    Return the N values (by simulation)
    '''
    if t == 0:
        # return [r0] * N
        assert False
    assert t in timestamps, f"{t} not in {timestamps}"
    return interpolate(r0, list(diffs[t].keys()), diffs[t], N)

def interpolate(r0, key_list, dict_val, N):
    '''
    Given the initial value r0, find the adjacent write_centers
    Then interpolate the diffs
    '''
    left_val, right_val = get_adjacent_values(r0, key_list)
    if left_val == right_val:
        return list(map(lambda x: x + r0, simulate(dict_val[left_val], N)))
    w1, w2 = get_adjacent_weight(left_val, right_val, r0)
    mixed_diff = simulate_mix(dict_val[left_val], dict_val[right_val], w1, w2, N)
    return list(map(lambda x: x + r0, mixed_diff))

def simulate_mix(vals1, vals2, w1, w2, N):
    '''
    Input: values and their weight
    Invariant: w1 + w2 == 1
    Return: a list of N values of distribution
    '''
    if N == -1:
        N = lcm(len(vals1), len(vals2))
    assert len(vals1) <= N, f'{len(vals1)} > {N}'
    assert len(vals2) <= N, f'{len(vals2)} > {N}'
    a_dis = simulate(vals1, N)
    b_dis = simulate(vals2, N)
    return [w1 * a_dis[i] + w2 * b_dis[i] for i in range(len(a_dis))]

def simulate(vals, N):
    # print(f"original: {len(vals)}, simulate: {N}")
    res = []
    for i in range(N // len(vals)):
        res += vals
    while len(res) < N:
        idx = random.randint(0, len(vals) - 1)
        res.append(vals[idx])
    return res

def get_adjacent_values(val, value_list):
    '''
    May return the same value! Please check.
    '''
    sorted_list = sorted(value_list)
    if val < sorted_list[0]:
        return sorted_list[0], sorted_list[0]
    if val > sorted_list[-1]:
        return sorted_list[-1], sorted_list[-1]
    idx = 0
    for i in range(0, len(sorted_list) - 1):
        if sorted_list[i] <= val and val < sorted_list[i+1]:
            idx = i
            break
    return sorted_list[idx], sorted_list[idx+1]

def get_adjacent_weight(x1, x2, v):
    '''
    Return normalized sum == 1
    '''
    a, b = x2 - v, v - x1
    assert a >= 0 and b >= 0, f'x1:{x1}, x2:{x2}, v:{v}'
    return a / (a + b), b / (a + b)

def test_drift():
    eps = (maxi - mini) / 100
    start = mini
    rs = []
    sigs = []
    means = []
    while start < maxi:
        res = get_distribution(start, fixed_timept, 1000)
        sigs.append(np.std(res))
        means.append(np.mean(res) - start)
        rs.append(start)
        start += eps
    plt.plot(rs, means)
    plt.show()

    plt.plot(rs, sigs)
    plt.show()


if __name__ == "__main__":
    load_param()
    print(timestamps)
    test_drift()
