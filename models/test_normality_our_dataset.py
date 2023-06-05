from scipy import stats
import sys
sys.path.append("..")
from scheme.level import Level
from write import WriteModel
from relax import RelaxModel
import numpy as np

def normal_test(x):
    # x is a set of values
    k2, p = stats.normaltest(x)
    # print(len(x), p)
    alpha = 1e-3
    if p < alpha:
        return False
    else:
        return True

def lognormal_test(x):
    # x is a set of values
    # avoid negative values
    y = np.abs(np.min(x)) + 1e-3
    k2, p = stats.normaltest(np.log(np.array(x) + y))
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
            f"{non_normal} / {total} = {non_normal / total}",
            "normal percentage", f"{(1 - non_normal / total) * 100}%")

def test_diff2(reciprocal, skew=False):
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
                res = lognormal_test(numbers)
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
            "non-lognormal percentage",
            f"{non_normal} / {total} = {non_normal / total}",
            "lognormal percentage", f"{(1 - non_normal / total) * 100}%")

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
           f"{non_normal} / {total} = {non_normal / total}",
           f"normal percentage", f"{(1 - non_normal / total) * 100}%")

def test2(only_write, reciprocal, skew=False):
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
                res = lognormal_test(RelaxDistr)
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
            "non-lognormal percentage",
           f"{non_normal} / {total} = {non_normal / total}",
           f"lognormal percentage", f"{(1 - non_normal / total) * 100}%")

def normality_test():
    test(True, False) # only write
    test_diff(False) # only relaxation
    test(False, False) # write+relaxation
    # using conductance
    test(True, True)
    test_diff(True)
    test(False, True)

    # for log-normality test
    test2(True, False) # only write
    test_diff2(False) # only relaxation
    test2(False, False) # write+relaxation
    # using conductance
    test2(True, True)
    test_diff2(True)
    test2(False, True)

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
    # skew_compute()
'''
Resistance T=0 (only_write) non-normal percentage 235 / 239 = 0.9832635983263598 normal percentage 1.673640167364021%
Resistance Drift_diff non-normal percentage 31 / 31 = 1.0 normal percentage 0.0%
Resistance T=1 (write+drift) non-normal percentage 239 / 239 = 1.0 normal percentage 0.0%
Conductance T=0 (only_write) non-normal percentage 239 / 239 = 1.0 normal percentage 0.0%
Conductance Drift_diff non-normal percentage 31 / 31 = 1.0 normal percentage 0.0%
Conductance T=1 (write+drift) non-normal percentage 239 / 239 = 1.0 normal percentage 0.0%
Resistance T=0 (only_write) non-lognormal percentage 239 / 239 = 1.0 lognormal percentage 0.0%
Resistance Drift_diff non-lognormal percentage 31 / 31 = 1.0 lognormal percentage 0.0%
Resistance T=1 (write+drift) non-lognormal percentage 239 / 239 = 1.0 lognormal percentage 0.0%
Conductance T=0 (only_write) non-lognormal percentage 239 / 239 = 1.0 lognormal percentage 0.0%
Conductance Drift_diff non-lognormal percentage 31 / 31 = 1.0 lognormal percentage 0.0%
Conductance T=1 (write+drift) non-lognormal percentage 239 / 239 = 1.0 lognormal percentage 0.0%
'''