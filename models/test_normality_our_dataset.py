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

def test_diff(reciprocal):
    non_normal = 0
    total = 0
    with open('confC14') as f:
        for line in f.readlines()[1:]:
            l = line.strip().split(',')
            t = float(l[0])
            if t != 1:
                continue
            # x.append(float(l[1]))
            # y.append(sqrt(statistics.variance(map(float, l[2:]))))
            numbers = list(map(float, l[2:]))
            if reciprocal:
                for i in range(len(numbers)):
                    if numbers[i] == 0: # avoid divide by 0
                        numbers[i] = numbers[i-1]
                    else:
                        numbers[i] = 1 / numbers[i]
            res = normal_test(numbers)
            if res == False:
                non_normal += 1
            total += 1
    print("Conductance" if reciprocal else "Resistance",
          "Drift_diff", non_normal, total, non_normal / total)

def test(only_write, reciprocal):
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts
    T: time for relaxation
    BER: bit error rate specification
    '''
    init()
    max_attempts = 25
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
            Write_N = -1
            Read_N = -1
            T = 1
            WriteDistr = WriteModel.distr(w_center, width, max_attempts, Write_N)
            if only_write:
                RelaxDistr = WriteDistr
            else:
                RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
            if reciprocal:
                for i in range(len(RelaxDistr)):
                    if RelaxDistr[i] == 0: # avoid divide by 0
                        RelaxDistr[i] = RelaxDistr[i-1]
                    else:
                        RelaxDistr[i] = 1 / RelaxDistr[i]
            res = normal_test(RelaxDistr)
            if res == False:
                non_normal += 1
            total += 1
    print("Conductance" if reciprocal else "Resistance",
          "T=0 (only_write)" if only_write else "T=1 (write+drift)",
          non_normal, total, non_normal / total)


if __name__ == "__main__":
    # test(True, False) # only write
    # test_diff(False) # only relaxation
    # test(False, False) # write+relaxation
    # using conductance
    # test(True, True)
    # test_diff(True)
    test(False, True)
'''
171 2.5580087545667636e-21
Resistance T=0 (only_write) 234 239 0.9790794979079498
-----------
1760 1.5323776033510897e-08
Resistance Drift_diff 31 31 1.0
-----------
149600 0.0
Resistance T=1 (write+drift) 239 239 1.0
===========================================
do condunctance normality test
171 4.4905104460966616e-21
Conductance T=0 (only_write) 234 239 0.9790794979079498
-----------
1760 0.0
Conductance Drift_diff 31 31 1.0
-----------
149600 0.0
Conductance T=1 (write+drift) 239 239 1.0
'''