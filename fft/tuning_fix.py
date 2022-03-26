import datetime
import subprocess
import math
import sys
sys.path.append("../ecc")
import search
import diff_compute


# q: rber
ours = {4: 0.003750000000000031,
 5: 0.006249999999999978,
 6: 0.012499999999999956,
 7: 0.02749999999999997,
 8: 0.043749999999999956,
 9: 0.043749999999999956,
 10: 0.09999999999999998,
 11: 0.15749999999999997,
 12: 0.21250000000000002,
 13: 0.16749999999999998,
 14: 0.15874999999999995,
 15: 0.23375,
 16: 0.25125
}

sba = {4: 0.125,
 5: 0.16500000000000004,
 6: 0.13249999999999995,
 7: 0.14,
 8: 0.2234848484848485,
 9: 0.25,
 10: 0.16625,
 11: 0.21375,
 12: 0.24624999999999997,
 13: 0.25,
 14: 0.26875000000000004,
 15: 0.38749999999999996,
 16: 0.33875
}

repeated = 10

def run(fin, fout, R, base, p, a0, f, spec_ber, raw_ber, scale):
    subprocess.run(["./bin_fix_mutate", fin, fout,
                    str(R), str(base),
                    str(p), str(a0), str(f),
                    str(spec_ber), str(raw_ber),
                    str(scale)])
def fft():
    subprocess.run(["./bin_fft", "4096", "output0"])
    return diff_compute.diff()

def testonce(R, base, p, a0, f, spec_ber, raw_ber, scale):
    run("input", "input0", R, base, p, a0, f, spec_ber, raw_ber, scale)
    res = fft()
    print("diff = ", res, flush=True)
    if res <= 0.1:
        return True
    else:
        return False

def test(R, base, p, a0, f, spec_ber, raw_ber, scale):
    for i in range(repeated):
        if testonce(R, base, p, a0, f, spec_ber, raw_ber, scale) == False:
            return False
    return True

def reduce_a0(R, base, p, a0, f, spec_ber, raw_ber, scale):
    # we assume p is fixed
    assert(a0 >= 0)
    if a0 == 0:
        return a0
    a0 -= 1
    f = mini - p - a0 * base
    assert f >= 0
    while test(R, base, p, a0, f, spec_ber, raw_ber, scale) == True:
        a0 -= 1
        if a0 < 0:
            break
        f = mini - p - a0 * base
    return a0 + 1

def get_a0_f(base, mini, p):
    a0 = math.floor((mini - p) / base)
    f = mini - p - a0 * base
    assert a0 >= 0
    assert f >= 0
    return a0, f

def get_f(base, mini, p, a0):
    f = mini - p - a0 * base
    return f

def tune(R, base, mini, spec_ber, raw_ber):
    res = set() # return as set of candidates
    p = 0
    a0, f = get_a0_f(base, mini, p)
    while test(R, base, p, a0, f, spec_ber, raw_ber, 1) == False:
        # first identify the minimum p
        p += 1
        a0, f = get_a0_f(base, mini, p)
    a0 = reduce_a0(R, base, p, a0, f, spec_ber, raw_ber, 1)
    f = get_f(base, mini, p, a0)
    res.add((base, raw_ber, p, a0, f, 0))
    best_a0 = a0
    while p < mini and a0 > 0:
        p += 1
        a0, f = get_a0_f(base, mini, p)
        a0 = reduce_a0(R, base, p, a0, f, spec_ber, raw_ber, scale)
        f = get_f(base, mini, p, a0)
        if a0 < best_a0:
            best_a0 = a0
            res.add((base, raw_ber, p, a0, f, 0))
    return res

def autotune(q_rber, mini, spec_ber, binary):
    res = {}
    for R, raw_ber in q_rber.items():
        base = math.floor(math.log(R, 2)) # R levels can at most store 'base' bits
        if binary and 2 ** base != R:
            continue
        candidate = tune(R, base, mini, spec_ber, raw_ber)
        print(candidate, flush=True)
        res[R] = candidate
    return res

def tune_result():
    print(datetime.datetime.now(), flush=True)
    # data range (0, 4095) * pre_scale (1) --> 2**12, need at most 12 bits
    res1 = autotune(ours, 12, 1e-13, True)
    res2 = autotune(sba, 12, 1e-13, True)
    print(datetime.datetime.now(), flush=True)
    print(res1, flush=True)
    print(res2, flush=True)

# R: [base, raw_ber, p_bits, a_cells, f(neglect_bits), pre_scale]
tune_ours = {4: [2, 0.003750000000000031, 6, 3, 0, 1],
             8: [3, 0.043749999999999956, 7, 0, 5, 1],
             16: [4, 0.25125, 7, 0, 5, 1]}

tune_sba = {4: [2, 0.125, 9, 0, 3, 1],
            8: [3, 0.2234848484848485, 8, 0, 4, 1],
            16: [4, 0.33875, 8, 0, 4, 1]}

def best_ecc_config(base, spec_ber, raw_ber, maxk_bit, maxn_cell):
    return search.bestcode(search.allcode(), spec_ber, raw_ber, maxk_bit, maxn_cell * base)

def ecc_search(tuning_result, spec_ber, maxk_bit, maxn_cell):
    print(datetime.datetime.now(), flush=True)
    best_overhead = 1e3
    best_config = []
    for R in tuning_result.keys():
        base, raw_ber, pbits, acells, _, __ = tuning_result[R]
        if pbits > 0:
            config = best_ecc_config(base, spec_ber, raw_ber, maxk_bit, maxn_cell)
            tag, ecc_overhead, n, k, d, base_ecc, uber = config
            total_overhead = (ecc_overhead * pbits) / base + acells
            total_config = [R, total_overhead, pbits, acells, tag, ecc_overhead, n, k, d, base_ecc, raw_ber, uber]
        else:
            total_overhead = acells
            total_config = [R, total_overhead, pbits, acells, raw_ber]
        if total_overhead < best_overhead:
            best_overhead = total_overhead
            best_config = total_config
    print(datetime.datetime.now(), flush=True)
    print(best_config, flush=True)


if __name__ == "__main__":
    tune_result()
    # print("R, total_overhead, pbits, acells, tag, ecc_overhead, n, k, d, base, raw_ber, uber")
    # ecc_search(tune_ours, 1e-13, 1e10, 1e10)
    # ecc_search(tune_sba, 1e-13, 1e10, 1e10)
