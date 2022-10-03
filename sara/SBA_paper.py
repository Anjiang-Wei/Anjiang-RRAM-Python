import rram
import numpy as np
# to correctly setup SBA:
# 1) deltaI=0.01; 2) given m and the sigma-R graph, compute the R(n) [get_R_range]
# Rmax(n) - Rmin(n) = R_range(n) = (1/2) * m * sigma
# Approximation assumption in SBA: sigma to be the function of Rmin(n)
def sigma_R(R):
    '''
    given a R value, return its corresponding sigma (based on the curve / figure)
    '''
    return np.std(rram.R_distr(R,500))
    '''
    if 3000 < R < 6000:
        return 1000
    if 6000 <= R < 25000:
        return 5000
    if R >= 25000:
        return 10000
    '''

def get_R_range(m, R):
   return m * sigma_R(R)


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
    return m, res

if __name__ == "__main__":
    print(search_m(8, 3200, 39902, [0] + [0.20] * 7, 1e-6, 0.001, 0.300))

