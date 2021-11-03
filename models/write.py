import collect_analyze
from utils.TinyLevel import Tiny_Level
import random
class WriteModel(object):
    def __init__(self):
        pass

    def data_init():
        print(f"Write data init from {collect_analyze.logfile}")
        fname = "../testlog/collect_data_" + collect_analyze.logfile
        collect_analyze.data_init(fname)
        print("Write data init finished")
    
    def distr(Wctr, width, max_attempts, Write_N):
        center_vals = Tiny_Level.filter_properties(lambda x: x.center)
        levels = Tiny_Level.filter_levels(lambda x: x.width == width and x.max_attempts == max_attempts)
        if len(levels) == 0:
            print("No satisfied levels, unable to do simulation")
        left_ctr, right_ctr = WriteModel.get_adjacent_values(Wctr, center_vals)
        left_wgt, right_wgt = WriteModel.get_adjacent_weight(left_ctr, right_ctr, width)
        left_level = Tiny_Level.filter_levels(lambda x: x.center == left_ctr, levels)
        right_level = Tiny_Level.filter_levels(lambda x: x.center == right_ctr, levels)
        assert len(left_level) == 1 and len(right_level) == 1
        return WriteModel.simulate_mix(left_level.finals, right_level.finals, left_wgt, right_wgt, Write_N)

    def get_adjacent_values(val, value_list):
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
        if x1 == x2:
            return 0.5, 0.5
        a, b = x2 - v, v - x1
        return a / (a + b), b / (a + b)
    
    def simulate_mix(vals1, vals2, w1, w2, N):
        '''
        Input: values and their weight
        Invariant: w1 + w2 == 1
        Return: a list of N values of distribution
        '''
        assert len(vals1) >= N
        assert len(vals2) >= N
        a_dis = WriteModel.simulate(vals1, N)
        b_dis = WriteModel.simulate(vals2, N)
        return [w1 * a_dis[i] + w2 * b_dis[i] for i in range(len(a_dis))]

    def simulate(vals, N):
        res = []
        for i in range(len(vals) // N):
            res += vals
        while len(res) < N:
            idx = random.randint(0, len(vals) - 1)
            res.append(vals[idx])
        return res
