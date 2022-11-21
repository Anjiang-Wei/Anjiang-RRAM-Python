from scipy import stats
import sys
sys.path.append("..")
from scheme.level import Level
from write import WriteModel
from relax import RelaxModel

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    # print(len(x), p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True

def compute_skew(x):
    return stats.skew(x)

def init():
    WriteModel.data_init(False)
    RelaxModel.data_init(False)

def test_diff(reciprocal, skew=False):
    non_normal = 0
    total = 0
    skew_sum = 0
    skew_cnt = 0
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
            if skew:
                skew_sum += compute_skew(numbers)
                skew_cnt += 1
            else:
                res = normal_test(numbers)
                if res == False:
                    non_normal += 1
                total += 1
    if skew:
        print("Conductance" if reciprocal else "Resistance",
            "Drift_diff",
            "average skewness",
            f"{skew_sum} / {skew_cnt} = {skew_sum / skew_cnt}")
    else:
        print("Conductance" if reciprocal else "Resistance",
            "Drift_diff",
            "non-normal percentage",
            f"{non_normal} / {total} = {non_normal / total}")

def test(only_write, reciprocal, skew=False):
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
    skew_sum = 0
    skew_cnt = 0
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
            if skew:
                skew_sum += compute_skew(RelaxDistr)
                skew_cnt += 1
            else:
                res = normal_test(RelaxDistr)
                if res == False:
                    non_normal += 1
                total += 1
    if skew:
        print("Conductance" if reciprocal else "Resistance",
            "T=0 (only_write)" if only_write else "T=1 (write+drift)",
            "average skewness",
            f"{skew_sum} / {skew_cnt} = {skew_sum / skew_cnt}")
    else:
        print("Conductance" if reciprocal else "Resistance",
            "T=0 (only_write)" if only_write else "T=1 (write+drift)",
            "non-normal percentage",
           f"{non_normal} / {total} = {non_normal / total}")

def normality_test():
    test(True, False) # only write
    test_diff(False) # only relaxation
    test(False, False) # write+relaxation
    # using conductance
    test(True, True)
    test_diff(True)
    test(False, True)

def skew_compute():
    test(True, False, True) # only write
    test_diff(False, True) # only relaxation
    test(False, False, True) # write+relaxation
    # using conductance
    test(True, True, True)
    test_diff(True, True)
    test(False, True, True)

if __name__ == "__main__":
    normality_test()
    skew_compute()
'''
Resistance T=0 (only_write) non-normal percentage 234 / 239 = 0.9790794979079498
Resistance Drift_diff non-normal percentage 31 / 31 = 1.0
Resistance T=1 (write+drift) non-normal percentage 239 / 239 = 1.0
Conductance T=0 (only_write) non-normal percentage 239 / 239 = 1.0
Conductance Drift_diff non-normal percentage 31 / 31 = 1.0
Conductance T=1 (write+drift) non-normal percentage 239 / 239 = 1.0
Resistance T=0 (only_write) average skewness 3.8722099042942797 / 239 = 0.016201715080729203
Resistance Drift_diff average skewness 92.04771660959518 / 31 = 2.9692811809546833
Resistance T=1 (write+drift) average skewness 493.54384845347744 / 239 = 2.065037022817897
Conductance T=0 (only_write) average skewness -0.004917618950183715 / 239 = -2.0575811507044833e-05
Conductance Drift_diff average skewness 5.280182700101353 / 31 = 0.17032847419681782
Conductance T=1 (write+drift) average skewness -84.42995517618506 / 239 = -0.353263410779017
'''

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
171 4.4905104460966616e-21
Conductance T=0 (only_write) 234 239 0.9790794979079498
-----------
1760 0.0
Conductance Drift_diff 31 31 1.0
-----------
149600 0.0
Conductance T=1 (write+drift) 239 239 1.0
===================
Resistance T=0 (only_write) average skewness 4.293700272487429 / 239 = 0.017965273106641963
Resistance Drift_diff average skewness 92.04771660959518 / 31 = 2.9692811809546833
Resistance T=1 (write+drift) average skewness 493.488274528943 / 239 = 2.064804495937
Conductance T=0 (only_write) average skewness -0.1494571107437333 / 239 = -0.0006253435595972105
Conductance Drift_diff average skewness 5.280182700101353 / 31 = 0.17032847419681782
'''