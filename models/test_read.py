from scipy import stats
import sys
sys.path.append("..")
from scheme.level import Level
from write import WriteModel
from relax import RelaxModel

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    print(len(x), p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True

def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def test():
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts
    T: time for relaxation
    BER: bit error rate specification
    '''
    init()
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
            Write_N = 100
            Read_N = 1000
            T = 1
            WriteDistr = WriteModel.distr(w_center, width, max_attempts, Write_N)
            RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
            res = normal_test(RelaxDistr)
            if res == False:
                non_normal += 1
            total += 1
    print(non_normal, total, non_normal / total)


if __name__ == "__main__":
    test()
