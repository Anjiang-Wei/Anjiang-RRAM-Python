import datetime
import subprocess
import math
import tuning_float
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

repeated = 1

def run(fin, fout, R, base, p, a0, f, spec_ber, raw_ber, scale):
    subprocess.run(["./bin_fix_mutate", fin, fout,
                    str(R), str(base),
                    str(p), str(a0), str(f),
                    str(spec_ber), str(raw_ber),
                    str(scale)])
def fft():
    subprocess.run(["./bin_fft", 4096, "output0"])
    return diff_compute.diff()

def testonce(R, base, p, a0, f, spec_ber, raw_ber, scale):
    run("input", "input0", R, base, p, a0, f, spec_ber, raw_ber, scale)
    res = fft()
    if res <= 0.1:
        return True
    else:
        return False

def test(R, base, p, a0, f, spec_ber, raw_ber, scale):
    for i in range(repeated):
        if testonce(R, base, p, a0, f, spec_ber, raw_ber, scale) == False:
            return False
    return True

def tune(R, base, mini, spec_ber, raw_ber):
    best_a0 = math.floor(mini / base)
    best_p, best_f = 0, mini - best_a0 * base
    while test(R, base, best_p, best_a0, best_f, spec_ber, raw_ber, 1) == False:
        # first identify the minimum best_p
        best_p += 1
        best_a0 = math.floor((mini - best_p) / base)
        best_f = mini - best_p - best_a0 * base
    res = [best_p, best_a0, best_f, 1]
    while test(R, base, best_p, best_a0, best_f, spec_ber, raw_ber, 1) == True:
        res = [best_p, best_a0, best_f, 1]
        if best_a0 == 0:
            break
        best_a0 -= 1
        best_f = mini - best_p - best_a0 * base
    return res

def autotune(q_rber, mini, spec_ber, binary):
    res = {}
    for R, raw_ber in q_rber.items():
        base = math.floor(math.log(R, 2)) # R levels can at most store 'base' bits
        if binary and 2 ** base != R:
            continue
        p, a0, f, pre_scale = tune(R, base, mini, spec_ber, raw_ber)
        res[R] = [base, raw_ber, p, a0, f, pre_scale]
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

tune_ours = {}
tune_sba = {}

def best_ecc_config(base, spec_ber, raw_ber, maxk_bit, maxn_cell):
    return search.bestcode(search.allcode(), spec_ber, raw_ber, maxk_bit, maxn_cell * base)

def ecc_search(tuning_result, spec_ber, maxk_bit, maxn_cell):
    best_overhead = 1e3
    best_config = []
    for R in tuning_result.keys():
        base, raw_ber, pbits, acells, _, __ = tuning_result[R]
        if pbits > 0:
            config = best_ecc_config(base, spec_ber, raw_ber, maxk_bit, maxn_cell)
            tag, ecc_overhead, n, k, d, base, uber = config
            total_overhead = (ecc_overhead * pbits) / base + acells
            total_config = [R, total_overhead, pbits, acells, tag, ecc_overhead, n, k, d, base, raw_ber, uber]
        else:
            total_overhead = acells
            total_config = [R, total_overhead, pbits, acells, raw_ber]
        if total_overhead < best_overhead:
            best_overhead = total_overhead
            best_config = total_config
    print(best_config)

if __name__ == "__main__":
    tune_result()
    # print("R, total_overhead, pbits, acells, tag, ecc_overhead, n, k, d, base, raw_ber, uber")
    # ecc_search(tune_ours, 1e-13, 1e10, 1e10)
    # ecc_search(tune_sba, 1e-13, 1e10, 1e10)