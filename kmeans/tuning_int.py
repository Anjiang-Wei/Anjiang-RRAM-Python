import pprint
import time
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

repeated = 3

def run(fin, fout, R, base, p, a0, f, spec_ber, raw_ber, scale):
    subprocess.run(["./bin_fix_mutate", fin, fout,
                    str(R), str(base),
                    str(p), str(a0), str(f),
                    str(spec_ber), str(raw_ber),
                    str(scale)])
def kmeans():
    subprocess.run(["./bin_kmeans", "1_input0", "1_output0"])
    subprocess.run(["./bin_kmeans", "2_input0", "2_output0"])
    subprocess.run(["./bin_kmeans", "3_input0", "3_output0"])
    diff1 = diff_compute.diff("1_output", "1_output0")
    diff2 = diff_compute.diff("2_output", "2_output0")
    diff3 = diff_compute.diff("3_output", "3_output0")
    return (diff1 + diff2 + diff3) / 3

def testonce(R, base, p, a0, f, spec_ber, raw_ber, scale):
    run("1_input", "1_input0", R, base, p, a0, f, spec_ber, raw_ber, scale)
    run("2_input", "2_input0", R, base, p, a0, f, spec_ber, raw_ber, scale)
    run("3_input", "3_input0", R, base, p, a0, f, spec_ber, raw_ber, scale)
    res = kmeans()
    print("diff = ", res, flush=True)
    if res <= 0.1 * 255:
        return True
    else:
        return False

def test(R, base, p, a0, f, spec_ber, raw_ber, scale):
    for i in range(repeated):
        if testonce(R, base, p, a0, f, spec_ber, raw_ber, scale) == False:
            return False
    return True


def get_a0_max(base, mini, p):
    a0 = math.floor((mini - p) / base)
    assert a0 >= 0
    return a0

def get_f(base, mini, p, a0):
    f = mini - p - base * a0
    assert f >= 0
    return f

def tune(R, base, mini, spec_ber, raw_ber):
    res = []
    for p in range(0, mini + 1):
        a0max = get_a0_max(base, mini, p)
        for a0 in range(0, a0max + 1):
            f = get_f(base, mini, p, a0)
            if test(R, base, p, a0, f, spec_ber, raw_ber, 1) == True:
                res.append((p, a0, f))
    return res

def autotune(q_rber, mini, spec_ber, binary):
    res = {}
    time_overhead = {}
    for R, raw_ber in q_rber.items():
        base = math.floor(math.log(R, 2)) # R levels can at most store 'base' bits
        if binary and 2 ** base != R:
            continue
        pre_time = time.time()
        candidate = tune(R, base, mini, spec_ber, raw_ber)
        print(candidate, flush=True)
        res[R] = candidate
        post_time = time.time()
        time_overhead[R] = post_time - pre_time
    return res, time_overhead

def tune_result():
    # data range (0, 255) * pre_scale (1) --> 2**8, need at most 8 bits
    res1, time1 = autotune(ours, 8, 1e-13, True)
    res2, time2 = autotune(sba, 8, 1e-13, True)
    print("tune_ours = ", end='')
    pprint.pprint(res1)
    print("tune_sba = ", end='')
    pprint.pprint(res2)
    print("time_ours = ", end='')
    pprint.pprint(time1)
    print("time_sba = ", end='')
    pprint.pprint(time2)

# R: [p_bits, a_cells, f(scale)]

tune_ours = {4: [(0, 2, 4),
     (0, 3, 2),
     (0, 4, 0),
     (1, 2, 3),
     (1, 3, 1),
     (2, 1, 4),
     (2, 2, 2),
     (2, 3, 0),
     (3, 1, 3),
     (3, 2, 1),
     (4, 0, 4),
     (4, 1, 2),
     (4, 2, 0),
     (5, 0, 3),
     (5, 1, 1),
     (6, 0, 2),
     (6, 1, 0),
     (7, 0, 1),
     (8, 0, 0)],
 8: [(0, 2, 2),
     (1, 1, 4),
     (1, 2, 1),
     (2, 1, 3),
     (2, 2, 0),
     (3, 1, 2),
     (4, 0, 4),
     (4, 1, 1),
     (5, 0, 3),
     (5, 1, 0),
     (6, 0, 2),
     (7, 0, 1),
     (8, 0, 0)],
 16: [(0, 1, 4),
      (0, 2, 0),
      (1, 1, 3),
      (2, 1, 2),
      (3, 1, 1),
      (4, 0, 4),
      (4, 1, 0),
      (5, 0, 3),
      (6, 0, 2),
      (7, 0, 1),
      (8, 0, 0)]}

tune_sba = {4: [(1, 2, 3),
     (1, 3, 1),
     (2, 1, 4),
     (2, 2, 2),
     (2, 3, 0),
     (3, 1, 3),
     (3, 2, 1),
     (4, 0, 4),
     (4, 1, 2),
     (4, 2, 0),
     (5, 0, 3),
     (5, 1, 1),
     (6, 0, 2),
     (6, 1, 0),
     (7, 0, 1),
     (8, 0, 0)],
 8: [(0, 2, 2),
     (1, 1, 4),
     (1, 2, 1),
     (2, 1, 3),
     (2, 2, 0),
     (3, 1, 2),
     (4, 0, 4),
     (4, 1, 1),
     (5, 0, 3),
     (5, 1, 0),
     (6, 0, 2),
     (7, 0, 1),
     (8, 0, 0)],
 16: [(0, 1, 4),
      (0, 2, 0),
      (1, 1, 3),
      (2, 1, 2),
      (3, 1, 1),
      (4, 0, 4),
      (4, 1, 0),
      (5, 0, 3),
      (6, 0, 2),
      (7, 0, 1),
      (8, 0, 0)]}


def best_ecc_config(spec_ber, raw_ber, maxk_bit, maxn_bit):
    return search.bestcode(search.allcode(), spec_ber, raw_ber, maxk_bit, maxn_bit)

def ecc_search(tuning_result, ber_dict, spec_ber, maxk_bit, maxn_bit):
    R_best_config = {}
    R_best_detail = {}
    R_runtime = {}
    for R in tuning_result.keys():
        pre_time = time.time()
        best_overhead = 1e10
        best_config = []
        best_detail = []
        raw_ber = ber_dict[R]
        ecc_config = best_ecc_config(spec_ber, raw_ber, maxk_bit, maxn_bit)
        tag, ecc_overhead, n, k, d, alpha_base, uber = ecc_config
        base = math.log(R, 2)
        for item in tuning_result[R]:
            pbits, acells, f = item
            total_overhead = (ecc_overhead * pbits) / base + acells
            total_config = [R, base, "float/Rfix", pbits, acells, f, raw_ber, tag, n, k, ecc_overhead, total_overhead]
            detail_config = [R, base, raw_ber, uber, tag, n, k, d, 2**alpha_base]
            if total_overhead < best_overhead:
                best_overhead = total_overhead
                best_config = total_config
                best_detail = detail_config
        R_best_config[R] = best_config
        R_best_detail[R] = best_detail
        post_time = time.time()
        R_runtime[R] = post_time - pre_time
    print("R, base, category, pbits, acells, f, raw_ber, tag, n, k, ecc_overhead, total_cells", flush=True)
    print("R_best_config = ", end='', flush=True)
    print(R_best_config, flush=True)
    print("R, base, raw_ber, uber, tag, n, k, d, alpha_size", flush=True)
    print("R_best_detail = ", end='', flush=True)
    print(R_best_detail, flush=True)
    print("R_runtime = ", end='', flush=True)
    print(R_runtime, flush=True)

if __name__ == "__main__":
    # tune_result()
    ecc_search(tune_ours, ours, 1e-13, 1e10, 1e10)
    ecc_search(tune_sba, sba, 1e-13, 1e10, 1e10)
