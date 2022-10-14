# import rram
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append("..")
from models.write import WriteModel
from models.relax import RelaxModel
from scheme.level import Level
from statistics import variance
from math import sqrt
# to correctly setup SBA:
# 1) deltaI=0.01; 2) given m and the sigma-R graph, compute the R(n) [get_R_range]
# Rmax(n) - Rmin(n) = R_range(n) = (1/2) * m * sigma
# Approximation assumption in SBA: sigma to be the function of Rmin(n)
def sigma_R(R):
    '''
    given a R value, return its corresponding sigma (based on the curve / figure)
    '''
    # return np.std(rram.R_distr(R,500))
    # use width 250
    return np.std(WriteModel.distr(R, 250, 100, 100))

def get_R_range(m, R):
   return m * sigma_R(R)

def draw(Rs):
    init()
    sigmas = [ sigma_R(R) for R in Rs ]
    plt.plot(Rs, sigmas)
    plt.show()

def compute(num_level, Rpre_max, Rfinal_min, V_BL, delta_I, m, return_result=False):
    res = [[0, Rpre_max]]
    for i in range(1, num_level):
        premax = res[-1][1]
        # V_BL[i] / premax - V_BL[i] / Rcur_min = 2*delta_I
        Rcur_min = V_BL[i] / (V_BL[i] / premax - 2*delta_I)
        Rcur_max = Rcur_min + get_R_range(m, Rcur_min)
        res.append([Rcur_min, Rcur_max])
    res[-1][1] = 1e6
    overflow = False
    if res[-1][0] > Rfinal_min:
        overflow = True
    if return_result:
        return overflow, res
    return overflow

def search_m(num_level, Rpre_max, Rfinal_min, V_BL, delta_I, delta_m, init_m):
    m = init_m
    while compute(num_level, Rpre_max, Rfinal_min, V_BL, delta_I,m) == False:
        m += delta_m
    # after finishing the while loop, overflow must be True
    m -= delta_m # back off a bit to let overflow be False
    overflow, res = compute(num_level, Rpre_max, Rfinal_min, V_BL, delta_I, m, True)
    assert(overflow == False)
    # return m, res
    levels = []
    for i in range(len(res)):
        Wlow, Whigh = res[i][0], res[i][1]
        Rlow = 0 if i == 0 else (V_BL[i] / (V_BL[i]/res[i][0] + delta_I))
        Rhigh = res[i][1]+1 if i == len(res) - 1 else (V_BL[i] / (V_BL[i]/res[i][1] - delta_I))
        levels.append(Level(Rlow, Rhigh, Wlow, Whigh))
    return m, levels

def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def main():
    init()
    for num_level in range(4, 9):
        m, levels = search_m(num_level, 3200, 39902, [0.20] * num_level, 1e-6, 0.001, 0.300)
        print(f"Solved for {num_level}: m={m}")
        file_tag = "C14_SBA_" +  str(num_level) + ".json"
        Level.export_to_file(levels, fout="../scheme/" + file_tag)

if __name__ == "__main__":
    # print(search_m(8, 3200, 39902, [0] + [0.20] * 7, 1e-6, 0.001, 0.300))
    # main()
    draw(range(3200, 39902, 20))
