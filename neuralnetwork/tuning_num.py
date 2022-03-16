import subprocess
import pprint
import math
import compute_diff

# q: rber
use_ours = True
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

def find_start_scale():
    return 1

def find_start_M(R):
    # data range = [0, 255]
    log_res = math.ceil(math.log(255, R))
    if R ** log_res == 255:
        log_res += 1
    return log_res

def run(R, M, m_p, m_a, scale, spec_ber, raw_ber, only3):
    # f1s: intermediate/1.rgb, f2s: mutated/1.rgb, fout: mutated/1.out
    f1s, f2s = compute_diff.all_files("rgb")
    _, fout = compute_diff.all_files("out")
    if only3:
        f1s, f2s = f1s[:3], f2s[:3]
        fout = fout[:3]
    for i in range(len(f1s)):
        subprocess.run(["./bin_fix_mutate", f1s[i], f2s[i], str(R), str(M),
                        str(m_p), str(m_a), str(scale), str(spec_ber), str(raw_ber)])
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

def find_s_mp_ma(start_scale, R, start_M, spec_ber, raw_ber):
    original_M = start_M
    M = start_M
    while M >= 1:
        M -= 1
        scale = R ** (M - original_M)
        if run(R, M, M, 0, scale, spec_ber, raw_ber, True):
            start_M = M
            start_scale = scale
        else:
            break
    print("R = ", R, "; M = ", start_M, "; scale = ", start_scale, flush=True)
    m_p_start = start_M
    m_p = m_p_start
    m_a = 0
    while m_p >= 0:
        m_p -= 1
        m_a += 1
        assert(m_p + m_a == start_M)
        if m_p < 0:
            continue
        if run(R, start_M, m_p, m_a, start_scale, spec_ber, raw_ber, True):
            m_p_start = m_p
    print("m_p = ", m_p_start, "; m_a = ", start_M - m_p_start, flush=True)
    return start_scale, m_p_start, start_M - m_p_start




if __name__ == "__main__":
    q_rber = ours if use_ours else sba
    spec_ber = 1e-13
    res = {}
    for R, rber in q_rber.items():
        start_scale = find_start_scale()
        start_M = find_start_M(R)
        scale, m_p, m_a = find_s_mp_ma(start_scale, R, start_M, spec_ber, rber)
        res[R] = [rber, scale, m_p, m_a]
    pprint.pprint(res)
