from scipy import stats
import numpy as np
import sys
sys.path.append("..")
import collect_analyze
from utils.TinyLevel import Tiny_Level
from math import lcm
import random

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    print(p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True



class WriteModel(object):
    def __init__(self):
        pass

    def data_init():
        collect_analyze.dead_cell_init("../log/")
        print(f"Write data init from {collect_analyze.logfile}")
        fname = "../testlog/14collect_data_" + collect_analyze.logfile
        collect_analyze.data_init(fname)
        print("Write data init finished")

    def distr(Wctr, width, max_attempts, Write_N=-1):
        levels = Tiny_Level.filter_levels(lambda x: x.width == width and x.max_attempts == max_attempts)
        center_vals = Tiny_Level.filter_properties(lambda x: x.center, levels)
        if len(levels) == 0:
            assert False, f"No satisfied levels for width={width}, max_attempts={max_attempts}, unable to do simulation"
        left_ctr, right_ctr = WriteModel.get_adjacent_values(Wctr, center_vals)
        if left_ctr == right_ctr:
            left_level = Tiny_Level.filter_levels(lambda x: x.center == left_ctr, levels)
            assert len(left_level) == 1, f'No left level at all'
            return WriteModel.transfer_distr(left_level[0].finals, left_level[0].center, Wctr, Write_N)
        assert left_ctr <= Wctr and Wctr <= right_ctr, f'{left_ctr}, {Wctr}, {right_ctr}'
        left_wgt, right_wgt = WriteModel.get_adjacent_weight(left_ctr, right_ctr, Wctr)
        left_level = Tiny_Level.filter_levels(lambda x: x.center == left_ctr, levels)
        right_level = Tiny_Level.filter_levels(lambda x: x.center == right_ctr, levels)
        assert len(left_level) == 1 and len(right_level) == 1, f'{len(left_level)}, {len(right_level)}'
        return WriteModel.simulate_mix(left_level[0].finals, right_level[0].finals, left_wgt, right_wgt, Write_N)

    def sigma(Wctr, width, max_attempts):
        levels = Tiny_Level.filter_levels(lambda x: x.width == width and x.max_attempts == max_attempts)
        center_vals = Tiny_Level.filter_properties(lambda x: x.center, levels)
        if len(levels) == 0:
            assert False, f"No satisfied levels for width={width}, max_attempts={max_attempts}, unable to do simulation"
        left_ctr, right_ctr = WriteModel.get_adjacent_values(Wctr, center_vals)
        if left_ctr == right_ctr:
            left_level = Tiny_Level.filter_levels(lambda x: x.center == left_ctr, levels)
            assert len(left_level) == 1, f'No left level at all'
            return np.std(left_level[0].finals)
        assert left_ctr <= Wctr and Wctr <= right_ctr, f'{left_ctr}, {Wctr}, {right_ctr}'
        left_wgt, right_wgt = WriteModel.get_adjacent_weight(left_ctr, right_ctr, Wctr)
        left_level = Tiny_Level.filter_levels(lambda x: x.center == left_ctr, levels)
        right_level = Tiny_Level.filter_levels(lambda x: x.center == right_ctr, levels)
        assert len(left_level) == 1 and len(right_level) == 1, f'{len(left_level)}, {len(right_level)}'
        # print(len(left_level[0].finals))
        return left_wgt * np.std(left_level[0].finals) + right_wgt * np.std(right_level[0].finals)

    def get_adjacent_values(val, value_list):
        sorted_list = sorted(value_list)
        if val <= sorted_list[0]:
            return sorted_list[0], sorted_list[0]
        if val >= sorted_list[-1]:
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
        a_dis = WriteModel.simulate(vals1, N)
        b_dis = WriteModel.simulate(vals2, N)
        return [w1 * a_dis[i] + w2 * b_dis[i] for i in range(len(a_dis))]

    def simulate(vals, N):
        # print(f"original: {len(vals)}, simulate: {N}")
        if N == -1:
            N = len(vals)
        res = []
        for i in range(N // len(vals)):
            res += vals
        while len(res) < N:
            idx = random.randint(0, len(vals) - 1)
            res.append(vals[idx])
        return res

    def transfer_distr(vals, old_center, new_center, Write_N):
        new_vals = [i - old_center + new_center for i in vals]
        return WriteModel.simulate(new_vals, Write_N)

    def stats_testing(Wctr, width, max_attempts):
        level = Tiny_Level.filter_levels(lambda x: (x.width == width and x.center == Wctr) and x.max_attempts == max_attempts)
        assert len(level) == 1
        return normal_test(level[0].finals)

def Test_WriteModel():
    WriteModel.data_init()
    import numpy as np
    max_attempts = 100
    Rmin, Rmax = 8000, 40000
    Nctr = 100
    for Wctr in range(Rmin, Rmax, (Rmax-Rmin)//Nctr):
        width_mean = {}
        width_std = {}
        for width in range(50, 1000, 100): # pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 1000
            try:
                WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
                mean, std = np.mean(WriteDistr), np.std(WriteDistr)
                # print(Wctr, width, ":", mean, std)
                width_mean[width] = float(abs(mean - Wctr))
                width_std[width] = float(std)
            except Exception as e:
                print(f'{e}')
        std_best_width = min(width_std, key=width_std.get)
        mean_best_width = min(width_mean, key=width_mean.get)
        print(Wctr, std_best_width, mean_best_width)

def normal_testing():
    WriteModel.data_init()
    import numpy as np
    max_attempts = 100
    lowest_target = 7812.5
    w_centers = list(range(7800, 10000, 200)) # 11
    w_centers += list(range(10000, 20000, 1000)) # 10
    w_centers += list(range(20000, 42000, 2000)) # 11
    non_normal = 0
    total = 0
    for w_center in w_centers:
        for width in range(50, 1000, 100):
            if w_center-width/2 < lowest_target:
                continue
            if w_center < 14000 and width > 500:
                continue
            try:
                res = WriteModel.stats_testing(w_center, width, max_attempts)
                if res == False:
                    non_normal += 1
                total += 1
            except Exception as e:
                print(f'{e}')
    print(non_normal, total, non_normal / total)

if __name__ == "__main__":
    normal_testing()
