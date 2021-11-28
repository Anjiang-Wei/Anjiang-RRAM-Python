import numpy as np
import matplotlib.pyplot as plt

model_char = "C13"
sigma = {}
mean = {}
timestamps = []
fixed_timept = 1.0
mini, maxi = 0, 0

def load_param():
    global timestamps, mini, maxi
    with open("../models/conf" + model_char, "r") as fin:
        lines = fin.readlines()
        mini, maxi = map(float, lines[0].split(","))
        for line in lines[1:]:
            # 0.01,8000.0,7.657536078066175,37.904362208317515
            t, w_center, avg, std = map(float, line.split(","))
            if t not in sigma.keys():
                mean[t] = {}
                sigma[t] = {}
            mean[t][w_center] = avg
            sigma[t][w_center] = std
        timestamps = sorted(list(sigma.keys()))

def get_mean_sigma(r0, t):
    assert t in timestamps, f"{t} not in {timestamps}"
    interpolate_mean = interpolate(r0, list(mean[t].keys()), mean[t])
    interpolate_sigma = interpolate(r0, list(sigma[t].keys()), sigma[t])
    return interpolate_mean, interpolate_sigma

def interpolate(r0, key_list, dict_val):
    left_val, right_val = get_adjacent_values(r0, key_list)
    if left_val == right_val:
        return dict_val[left_val]
    w1, w2 = get_adjacent_weight(left_val, right_val, r0)
    return w1 * dict_val[left_val] + w2 * dict_val[right_val]

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

def drift(r0, t):
    avg, sig = get_mean_sigma(r0, t)
    diff = np.random.normal(avg, sig)
    return r0 + diff

def test_drift():
    eps = (maxi - mini) / 100
    start = mini
    rs = []
    sigs = []
    means = []
    while start < maxi:
        res = []
        for t in range(1000):
            res.append(drift(start, fixed_timept))
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
    # r0 = float(input("Write r0 between " + str(mini) + ", " + str(maxi) + "\n"))
    r0 = 9000
    print(drift(r0, 1))
    test_drift()
