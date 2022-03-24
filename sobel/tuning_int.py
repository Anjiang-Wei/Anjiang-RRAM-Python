import datetime
import subprocess
import pprint
import math
import compute_diff

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

def run(fin, fout, R, base, p, a0, f, spec_ber, raw_ber, scale):
    subprocess.run(["./bin_fix_mutate", fin, fout,
                    str(R), str(base),
                    str(p), str(a0), str(f),
                    str(spec_ber), str(raw_ber),
                    str(scale)])

def test(R, base, p, a0, f, spec_ber, raw_ber, scale, only3):
    # f1s: intermediate/1.rgb, f2s: mutated/1.rgb, fout: mutated/1.out
    f1s, f2s = compute_diff.all_files("rgb")
    _, fout = compute_diff.all_files("out")
    if only3:
        f1s, f2s = f1s[:3], f2s[:3]
        fout = fout[:3]
    for i in range(len(f1s)):
        run(f1s[i], f2s[i], R, base, p, a0, f, spec_ber, raw_ber, scale)
        subprocess.run(["python3", "reverse_intermediate.py", f2s[i]])
    for i in range(len(f2s)):
        subprocess.run(["./sobel", f2s[i], fout[i]])
        subprocess.run(["python3", "create_intermediate.py", fout[i]])
    res = compute_diff.diffall(only3)
    print("image diff:", res, flush=True)
    if res < 0.1 * 255:
        return True
    else:
        return False

def tune(R, base, mini, spec_ber, raw_ber):
    a0 = math.ceil(mini / base)
    best_p, best_a0, best_f = 0, a0, 0
    res = []
    while test(R, base, best_p, best_a0, best_f, spec_ber, raw_ber, 1, True) == False:
        # first identify the minimum best_p
        best_p += 1
        best_a0 = math.floor((mini - best_p) / base)
        best_f = mini - best_p - best_a0 * base
    while test(R, base, best_p, best_a0, best_f, spec_ber, raw_ber, 1, True) == True:
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
    res1 = autotune(ours, 8, 1e-13, True)
    res2 = autotune(sba, 8, 1e-13, True)
    print(datetime.datetime.now(), flush=True)
    print(res1, flush=True)
    print(res2, flush=True)

# R: [base, raw_ber, p_bits, a_cells, f(neglect_bits), pre_scale]
tune_ours = {4: [2, 0.003750000000000031, 0, 2, 4, 1],
             8: [3, 0.043749999999999956, 1, 1, 4, 1],
             16: [4, 0.25125, 1, 1, 3, 1]}

tune_sba = {4: [2, 0.125, 2, 1, 4, 1],
            8: [3, 0.2234848484848485, 2, 1, 3, 1],
            16: [4, 0.33875, 1, 1, 3, 1]}


if __name__ == "__main__":
    tune_result()
