import time
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

repeated = 3

def run(fin, fout, R, base, p, a0, f, spec_ber, raw_ber, scale):
    subprocess.run(["./bin_fix_mutate", fin, fout,
                    str(R), str(base),
                    str(p), str(a0), str(f),
                    str(spec_ber), str(raw_ber),
                    str(scale)])

def testonce(R, base, p, a0, f, spec_ber, raw_ber, scale, only3):
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

def test(R, base, p, a0, f, spec_ber, raw_ber, scale, only3=True):
    for i in range(repeated):
        if testonce(R, base, p, a0, f, spec_ber, raw_ber, scale, only3) == False:
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


if __name__ == "__main__":
    tune_result()
