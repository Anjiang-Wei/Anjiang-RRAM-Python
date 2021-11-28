import numpy as np
import pprint
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.interpolate import make_interp_spline
from scipy.ndimage import gaussian_filter1d

logfile = "testlog/13collect_data_100_1_0"

# R[timept][R_0] -> R_t
R = {}
times = [] # [0.0, 0.01, 0.1, 1.0, 2.0]

# write_center: (w_low + w_high) / 2 --> list of R_0
write_centers = {}

# d[timept][R_0] -> R_t - R_0
d = {}

# s[timept][R_0] -> sigma(R_t - R_0)
s = {}

# m[timept][R_0] -> mean(R_t - R_0)
m = {}

model_char = "C13"
config = {
    # maxi, mini of resistance range
    "C13": [40 * 1e3, 8000]
}
dead_cells = []
# the number of times for read --> corresponding timestamps
read2time = {0: 0.0, 1: 0.01, 2: 0.1, 3: 1, 4: 2}

def dead_cell_init(logdir=""):
    '''
    Consider two log files to initialize the dead cell tracking
    Output -> dead_cells (a global variable)
    '''
    if logdir == "":
        logdir = 'log/'
    global dead_cells
    with open(logdir + "13dead_test.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    with open(logdir + "13new_dead.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    dead_cells = sorted(set(dead_cells))
    print(f'Dead cell initialization finished: {len(dead_cells)} are dead')

def init(fname=""):
    if fname == "":
        fname = logfile
    with open(fname, "r") as fin:
        lines = fin.readlines()
        read_cnt = 0
        resistance_0 = 0
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            if line[0] == "Init":
                read_cnt = 0
                continue
            if line[0] == "Write":
                assert read_cnt == 0, read_cnt
                action, low, high, addr, t, final, _, max_attempts = line
                resistance, addr = float(final), int(addr)
                low, high = float(low), float(high)
                if addr in dead_cells:
                    continue
                if 0 not in R.keys():
                    R[0] = {}
                R[0][resistance] = resistance
                resistance_0 = resistance
                read_cnt += 1
                w_center = (low + high) / 2
                if w_center not in write_centers:
                    write_centers[w_center] = []
                write_centers[w_center].append(resistance_0)
            else:
                action, low, high, addr, t, final, _ = line
                resistance_t, addr = float(final), int(addr)
                timept = read2time[read_cnt]
                read_cnt += 1
                if addr in dead_cells:
                    continue
                if timept not in R.keys():
                    R[timept] = {}
                R[timept][resistance_0] = resistance_t
    global times
    times = sorted(list(R.keys()))

def compute_d():
    '''
    Compute the difference w.r.t time, given the same address [same initial g0]
    '''
    for t in times[1:]:
        if t not in d.keys():
            d[t] = {}
        for r_0 in R[t].keys():
            assert R[0][r_0] == r_0
            d[t][r_0] = R[t][r_0] - R[0][r_0]

# good = 0
# total = 0
# last_normal_value = 0.0
# def compute_std_old(dic, keys):
#     global last_normal_value
#     global good, total
#     res = []
#     for k in keys:
#         res.append(dic[k])
#     assert len(res) >= 1, res
#     try:
#         test = stats.normaltest(res)
#         print(test)
#         if test.pvalue > 1e-3:
#             good = good + 1
#         else:
#             sns.distplot(res, kde=True,bins=100)
#             plt.show()
#             # pass
#         total += 1
#     except:
#         print("Exception occurs")
#         return last_normal_value
#     last_normal_value = np.std(res)
#     return np.std(res)

def compute_mean_std(dic, keys):
    res = []
    for k in keys:
        res.append(dic[k])
    assert len(res) >= 1, res
    return np.mean(res), np.std(res)

# def find_index(vals, low_val):
#     for i in range(len(vals)):
#         if vals[i] >= low_val:
#             return i
#     assert False, "Not Found, low_val is too high!"

def export(vals, append=True):
    vals_ = list(map(str, vals))
    with open("models/conf" + model_char, "a" if append else "w") as fout:
        fout.write(",".join(vals_) + "\n")

# def old_compute_sigma(bins = 30):
#     '''
#     Given the number of bins (to segment [min_g, max_g]), compute the sigma for each bin
#     Output: s1, s2
#     '''
#     global total, good
#     # all_g_t = sorted(list(d1[times[-1]].keys()))
#     max_val, min_val = config[model_char] # max(all_g_t), min(all_g_t)
#     interval = (max_val - min_val) / bins
#     export([max_val, min_val, bins], False)
#     for t in times[1:]:
#         if t not in s.keys():
#             s[t] = {}
#         all_g = sorted(list(d[t].keys()))
#         print(f"len(all_g) = {len(all_g)}")
#         for idx in range(0, bins):
#             low_idx = find_index(all_g, min_val + idx * interval)
#             high_idx = find_index(all_g, min_val + (idx + 1) * interval)
#             high_idx = max(low_idx + 1, high_idx)
#             if t == 0.01:
#                 print(idx, high_idx - low_idx)
#             std = compute_std(d[t], all_g[low_idx:high_idx])
#             s[t][idx] = std

#             export([t, idx, std])

#             if idx not in s.keys():
#                 s[idx] = {}
#             s[idx][t] = std
#         print("good normal: ", good, total, good / total)
#         good = total = 0

def compute_sigma():
    '''
    Compute the sigmas for a whole bunch of write_centers
    '''
    w_smallest, w_biggest = min(write_centers.keys()), max(write_centers.keys())
    export([w_smallest, w_biggest], append=False)
    for t in times[1:]:
        for w_center in write_centers.keys():
            mean, sigma = compute_mean_std(d[t], write_centers[w_center])
            if t not in m.keys():
                m[t] = {}
            m[t][w_center] = mean
            if t not in s.keys():
                s[t] = {}
            s[t][w_center] = sigma
            export([t, w_center, mean, sigma])

def figure_d_r():
    y, z = [], []
    print(min(d.keys()), max(d.keys()))
    for yy in list(d[0.1].keys()):
        y.append(yy)
        z.append(d[0.1][yy])
    y_, z_ = np.array(y), np.array(z)
    plt.plot(y_, z_, 'ro')
    plt.show()

def figure_s_r():
    y, z = [], []
    print(min(s.keys()), max(s.keys()))
    for tt in s.keys():
        print(tt)
        for yy in s[tt].keys():
            y.append(yy)
            z.append(s[tt][yy])
            y_, z_ = np.array(y), np.array(z)
        plt.plot(y_, z_)
        plt.show()
        break

def figure_m_g():
    y, z = [], []
    print(min(m.keys()), max(m.keys()))
    for tt in m.keys():
        print(tt)
        for yy in m[tt].keys():
            y.append(yy)
            z.append(m[tt][yy])
            y_, z_ = np.array(y), np.array(z)
        plt.plot(y_, z_)
        plt.show()
        break

def compute_t():
    for t in s.keys():
        vals = list(s[t].values())
        print(t, sum(vals) / len(vals))

def figure_s_r_smooth():
    y, z = [], []
    print(min(s.keys()), max(s.keys()))
    for tt in s.keys():
        print(tt)
        for yy in s[tt].keys():
            y.append(yy)
            z.append(s[tt][yy])
            y_, z_ = np.array(y), np.array(z)
        model=make_interp_spline(y_, z_)
        ys=np.linspace(min(y),max(y),50)
        zs=model(ys)
        z_smoothed = gaussian_filter1d(zs, sigma=3)
        plt.plot(ys, z_smoothed)
        plt.show()
        break


def figure_m_r_smooth():
    y, z = [], []
    print(min(m.keys()), max(m.keys()))
    for tt in m.keys():
        print(tt)
        for yy in m[tt].keys():
            y.append(yy)
            z.append(m[tt][yy])
            y_, z_ = np.array(y), np.array(z)
        model=make_interp_spline(y_, z_)
        ys=np.linspace(min(y),max(y),50)
        zs=model(ys)
        z_smoothed = gaussian_filter1d(zs, sigma=3)
        plt.plot(ys, z_smoothed)
        plt.show()
        break


if __name__ == "__main__":
    dead_cell_init()
    init()
    compute_d()
    compute_sigma()
    # figure_d_r()
    # figure_s_r()
    # figure_m_g()
    # compute_t()
    figure_s_r_smooth()
    figure_m_r_smooth()
