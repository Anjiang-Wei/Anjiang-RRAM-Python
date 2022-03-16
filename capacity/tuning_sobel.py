from scipy.special import comb
import pickle
import math
import numpy as np
import pprint

db = {}
# (q, n, k) --> d
# overhead: n / k

def P_cw(N, E, RBER):
    '''
    N: block length; the number of cells for output [length of codeword]
    E: the number of errors that can be corrected
    RBER: Raw BER; the probability of level drift; worst case analysis
    # actually RBER depends on q
    '''
    res = 0
    for i in range(E+1, N+1):
        res += comb(N, i) * pow(RBER, i) * pow(1-RBER, N-i)
    return res


def load_db():
    global db
    with open('database.json', 'rb') as fin:
        db = pickle.load(fin)


def get_all_candidates(intended_q=None):
    res = []
    for key in db.keys():
        q, n, k = key
        d = db[key]
        assert d <= n - k + 1
        if intended_q == None:
            res.append((q, n, k, d))
        else:
            if q == intended_q:
                res.append((q, n, k, d))
    return res

def select_ratio(candidates, intended_uber, RBER):
    res = []
    for cand in candidates:
        q, n, k, d = cand
        p_cw = P_cw(n, int((d-1)/2), RBER)
        # User_Data_bits_per_CW = log(pow(q^m, k), base=2) = k / log(2, base=q^m)
        bits_per_cw = k / math.log(2, q)
        uber = p_cw / bits_per_cw
        if uber <= intended_uber:
            res.append((cand, uber))
    return res


def compute_blksize(q, e, m_p, k):
    '''
    the maximum integer x, such that
    x * m_p <= k

    '''
    return math.floor(k / m_p)

def compute_blksize2(q, e, m_p, k):
    '''
    the maximum float x, such that
    x * m_p <= k

    '''
    assert q == 2
    return k / m_p

def select_blksize(candidates, n_max, e, m_p, q_binary):
    res = []
    for cand_uber in candidates:
        cand, uber = cand_uber
        q, n, k, d = cand
        assert e == 0 # Rnum / Rint does not need e
        if m_p > 0:
            if q_binary:
                blksize = compute_blksize2(q, e, m_p, k)
            else:
                blksize = compute_blksize(q, e, m_p, k)
        else:
            blksize = -1 # if m_p = 0, Rnum / Rint does not need notion of blksize
        if blksize <= n_max:
            res.append((q, n, k, d, uber, blksize))
    return res

def minimum_overhead(candidates, total_floats, m_a, q_binary):
    '''
    if blksize != -1:
        ceil((#total num) / blksize ) ∗ n + # total num * m_a
    else:
        # total num * m_a
    '''
    res = ()
    cur_best = 1e20
    for param in candidates:
        q, n, k, d, uber, blksize = param
        if blksize == 0:
            continue
        if q_binary:
            overhead = math.ceil(total_floats / blksize * n) + total_floats * m_a
        else:
            overhead = math.ceil(total_floats / blksize) * n + total_floats * m_a
        if blksize == -1:
            overhead = total_floats * m_a
        overhead = overhead / total_floats
        if overhead < cur_best:
           res = (q, n, k, d, uber, blksize, overhead)
           cur_best = overhead
    return res



def get_matrix_from_file(filename):
    with open(filename, "r") as fin:
        lines = fin.readlines()
        n = len(lines)
        matrix = np.zeros((n, n))
        for i in range(n):
            line = list((map(float, lines[i].split(","))))
            assert len(line) == n
            for j in range(n):
                matrix[i][j] = line[j]
    return matrix

def get_rber_from_matrix(matrix):
    '''
    worst case analysis
    '''
    n = len(matrix)
    minimum_diag = 1.0
    for i in range(n):
        elem = matrix[i][i]
        minimum_diag = min(elem, minimum_diag)
    return n, 1.0 - minimum_diag

def get_all_q_uber(ours):
    if ours:
        ours_list = ["ours" + str(i) for i in range(4, 17)]
    else:
        ours_list = ["SBA" + str(i) for i in range(4, 17)]
    res = []
    for f in ours_list:
        matrix = get_matrix_from_file(f)
        n, rber = get_rber_from_matrix(matrix)
        # print(n, rber, f)
        res.append((n, rber))
    return res



def pick_nkd(n_max, p_rel, q, e, m_p, m_a, rber, total_floats, q_binary):
    '''
    n_max (maximum of block size)
    fail_prob <= p_rel
    q: base
    e: # exponent bits
    m_p: # precise mantissa
    rber: prob of level drift
    '''
    res = get_all_candidates(intended_q=q)
    # print("after q", len(res), flush=True)
    res = select_ratio(res, p_rel, rber) # compute_uber
    # print("after ratio", len(res), flush=True)
    res = select_blksize(res, n_max, e, m_p, q_binary) # compute_blksize
    # print("after blksize", len(res), flush=True)
    # (q, n, k, d, uber, blksize)
    res = minimum_overhead(res, total_floats, m_a, q_binary)

    return res

def tuning_algorithm(n_max, p_rel, q, e, m_p, m_a, total_floats, verbose, ours, q_binary=False):
    '''
    Arg list:
    n_max: # maximum fp values for batched read
    p_rel: spec for reliable storage, UBER
    q: base (q^m)
    m_p: # precise mantissa
    m_a: # approximate mantissa

    Other args:
    rber: level drift prob
    e: # exponent bits
    <n, k, d>: linear code params
    '''
    for q_, rber in get_all_q_uber(ours):
        if q_ != q:
            continue
        if q_binary:
            if verbose:
                print(f'q_original = {q}')
            q = 2
        cand = pick_nkd(n_max, p_rel, q, e, m_p, m_a, rber, total_floats, q_binary)
        if verbose:
            print(f'q = {q}, e = {e}, m_p = {m_p}, m_a = {m_a}, rber=  {rber}, cand = {cand}', flush=True)
        return cand


# our result
# q --> (rber, scaling_factor, m_p, m_a)
dynamic_result = {4: [0.003750000000000031, 0.0625, 0, 2],
                  5: [0.006249999999999978, 0.2, 1, 2],
                  6: [0.012499999999999956, 0.16666666666666666, 1, 2],
                  7: [0.02749999999999997, 0.14285714285714285, 1, 1],
                  8: [0.043749999999999956, 0.125, 1, 1],
                  9: [0.043749999999999956, 0.1111111111111111, 1, 1],
                  10: [0.09999999999999998, 0.1, 1, 1],
                  11: [0.15749999999999997, 0.09090909090909091, 1, 1],
                  12: [0.21250000000000002, 0.08333333333333333, 1, 1],
                  13: [0.16749999999999998, 0.07692307692307693, 1, 1],
                  14: [0.15874999999999995, 0.07142857142857142, 1, 1],
                  15: [0.23375, 0.06666666666666667, 2, 0],
                  16: [0.25125, 0.0625, 1, 0]}
# SBA
# q --> (rber, scaling_factor, m_p, m_a)
dynamic_result2 = {4: [0.125, 0.0625, 1, 1],
                   5: [0.16500000000000004, 0.2, 2, 1],
                   6: [0.13249999999999995, 0.16666666666666666, 2, 1],
                   7: [0.14, 0.14285714285714285, 1, 1],
                   8: [0.2234848484848485, 0.125, 1, 1],
                   9: [0.25, 0.1111111111111111, 1, 1],
                   10: [0.16625, 0.1, 1, 1],
                   11: [0.21375, 0.09090909090909091, 1, 1],
                   12: [0.24624999999999997, 0.08333333333333333, 1, 1],
                   13: [0.25, 0.07692307692307693, 1, 1],
                   14: [0.26875000000000004, 0.07142857142857142, 2, 0],
                   15: [0.38749999999999996, 0.06666666666666667, 2, 0],
                   16: [0.33875, 0.0625, 1, 0]}

def tool():
    res = ()
    optimal = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        e = 0
        cand = tuning_algorithm(128, 1e-13, q, e, m_p, m_a, 512*512*3, verbose=False, ours=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====tool======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)
    '''
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 1, 2, 5, 130, 74, 25, 1.7130293974600777e-14, 74, 3.7568461100260415)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 0, 2, 2)
    '''
    overhead_bin = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        iter = math.ceil(math.log(q, 2))
        overhead = m_p * iter + m_a
        if overhead < overhead_bin:
            overhead_bin = overhead
            res = (q, e, m_p, m_a, overhead)
    print("if assuming 2 reliable, {q, e, m_p, m_a, overhead}=", res)

def tool_binary():
    res = ()
    optimal = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        if q not in [2, 4, 8, 16]:
            continue
        e = 0
        cand = tuning_algorithm(128, 1e-13, q, e, m_p, m_a, 512*512*3, verbose=False, ours=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====tool_binary======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)
    overhead_bin = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        if q not in [2, 4, 8, 16]:
            continue
        iter = math.log(q, 2)
        e = 0
        overhead = m_p * iter + m_a
        if overhead < overhead_bin:
            overhead_bin = overhead
            res = (q, e, m_p, m_a, overhead)
    print("if assuming 2 reliable, {q, e, m_p, m_a, overhead}=", res)

def tool_any_blksize():
    res = ()
    optimal = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        e = 0
        cand = tuning_algorithm(1e10, 1e-13, q, e, m_p, m_a, 512*512*3, verbose=False, ours=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====tool_any_blksize======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)
    overhead_bin = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        iter = math.ceil(math.log(q, 2))
        e = 0
        overhead = m_p * iter + m_a
        if overhead < overhead_bin:
            overhead_bin = overhead
            res = (q, e, m_p, m_a, overhead)
    print("if assuming 2 reliable, {q, e, m_p, m_a, overhead}=", res)

def our_precise_bin():
    '''
    All precise data
    '''
    res = ()
    optimal = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        if q not in [2, 4, 8, 16]:
            continue
        m_p += m_a
        m_a = 0
        e = 0
        cand = tuning_algorithm(1e10, 1e-13, q, e, m_p, m_a, 512*512*3, verbose=False, ours=True, q_binary=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====our_precise_bin======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)
    overhead_bin = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result.items():
        if q not in [2, 4, 8, 16]:
            continue
        iter = math.ceil(math.log(q, 2))
        m_p += m_a
        m_a = 0
        overhead = m_p * iter + m_a
        if overhead < overhead_bin:
            overhead_bin = overhead
            res = (q, e, m_p, m_a, overhead)
    print("if assuming 2 reliable, {q, e, m_p, m_a, overhead}=", res)

def sba_precise_bin():
    res = ()
    optimal = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result2.items():
        if q not in [2, 4, 8, 16]:
            continue
        m_p += m_a
        m_a = 0
        e = 0
        cand = tuning_algorithm(1e10, 1e-13, q, e, m_p, m_a, 512*512*3, verbose=False, ours=False, q_binary=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====sba_precise_bin======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)

    overhead_bin = 1e20
    for q, (rber, scaling_factor, m_p, m_a) in dynamic_result2.items():
        if q not in [2, 4, 8, 16]:
            continue
        iter = math.log(q, 2)
        m_p += m_a
        m_a = 0
        e = 0
        overhead = m_p * iter + m_a
        if overhead < overhead_bin:
            overhead_bin = overhead
            res = (q, e, m_p, m_a, overhead)
    print("if assuming 2 reliable, {q, e, m_p, m_a, overhead}=", res)


if __name__ == "__main__":
    load_db()
    sba_precise_bin()
    our_precise_bin()
    # tool()
    # tool_binary()
    # tool_any_blksize()
    '''
    ====sba_precise_bin======
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 2, 0, 4, 253, 22, 145, 8.632076970817778e-14, 11, 23.00005849202474)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 2, 0, 4.0)
    ====our_precise_bin======
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 2, 0, 4, 254, 184, 25, 7.332052762489173e-14, 92, 2.7611363728841147)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 2, 0, 4)
    ====tool======
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 1, 2, 5, 130, 74, 25, 1.7130293974600777e-14, 74, 3.7568461100260415)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 0, 2, 2)
    ====tool_binary======
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 1, 1, 8, 129, 41, 53, 9.774053558937065e-14, 41, 4.146461486816406)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 0, 2, 2.0)
    ====tool_any_blksize======
    e, m_p, m_a, q, n, k, d, uber, blksize, overhead
    (0, 1, 2, 5, 130, 74, 25, 1.7130293974600777e-14, 74, 3.7568461100260415)
    if assuming 2 reliable, {q, e, m_p, m_a, overhead}= (4, 0, 0, 2, 2)
    '''
