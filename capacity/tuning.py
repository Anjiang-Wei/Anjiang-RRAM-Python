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
    x * (e + m_p) + ceil(x / floor(log(q, base=2))) <= k

    '''
    x = 0
    while True:
        if x * (e + m_p) + math.ceil(x / math.floor(math.log(q, 2))) <= k:
            x += 1
        else:
            break
    return x - 1

def select_blksize(candidates, n_max, e, m_p):
    res = []
    for cand_uber in candidates:
        cand, uber = cand_uber
        q, n, k, d = cand
        blksize = compute_blksize(q, e, m_p, k)
        if blksize <= n_max:
            res.append((q, n, k, d, uber, blksize))
    return res

def minimum_overhead(candidates, total_floats, m_a):
    '''
    ceil((#total floats) / blksize ) ∗ n + # total floats * m_a
    '''
    res = ()
    cur_best = 1e20
    for param in candidates:
        q, n, k, d, uber, blksize = param
        overhead = math.ceil(total_floats / blksize) * n + total_floats * m_a
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

def pick_e(I_data, q):
    low, high = I_data
    low, high = abs(low), abs(high)
    value = max(low, high)
    # print(f"value = {value}")
    if q > value: # e_bit = 0
        return 0
    for e_bit in range(1, 8):
        bias = pow(q, e_bit-1) - 1
        e_max = str(q-1) * e_bit
        e_max = int(e_max, q)
        exp = e_max - bias
        max_value = pow(q, exp) * q
        # print(f"e_bit = {e_bit}, e_max = {e_max}, exp = {exp}, max_value = {max_value}")
        if max_value > value:
            return e_bit
    raise Exception

def compute_rber_e(I_data, ours):
    q2rber_e = {}
    for q, rber in get_all_q_uber(ours):
        e = pick_e(I_data, q)
        q2rber_e[q] = (rber, e)
    pprint.pprint(q2rber_e)


def pick_nkd(n_max, p_rel, q, e, m_p, m_a, rber, total_floats):
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
    res = select_blksize(res, n_max, e, m_p) # compute_blksize
    # print("after blksize", len(res), flush=True)
    # (q, n, k, d, uber, blksize)
    res = minimum_overhead(res, total_floats, m_a)

    return res

def tuning_algorithm(n_max, p_rel, q, e, m_p, m_a, total_floats, verbose, ours):
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
        cand = pick_nkd(n_max, p_rel, q, e, m_p, m_a, rber, total_floats)
        if verbose:
            print(f'q = {q}, e = {e}, m_p = {m_p}, m_a = {m_a}, rber=  {rber}, cand = {cand}', flush=True)
        return cand


# q --> (m_p, m_a)
# our result
dynamic_result = {4: (0, 4),
                  5: (0, 4),
                  6: (2, 1),
                  7: (0, 3),
                  8: (0, 3),
                  9: (0, 3),
                  10: (0, 3),
                  11: (0, 3),
                  12: (1, 2),
                  13: (0, 3),
                  14: (0, 3),
                  15: (0, 3),
                  16: (0, 3)}

# q --> (m_p, m_a)
dynamic_result = {4: (2, 2),
                  5: (2, 2),
                  6: (2, 1),
                  7: (1, 2),
                  8: (2, 1),
                  9: (1, 2),
                  10: (2, 1),
                  11: (2, 1),
                  12: (2, 1),
                  13: (2, 1),
                  14: (0, 3),
                  15: (0, 3),
                  16: (1, 2)}

def tool():
    res = ()
    optimal = 1e20
    for q, mp_ma in dynamic_result.items():
        m_p, m_a = mp_ma
        e = 0
        cand = tuning_algorithm(100, 1e-13, q, e, m_p, m_a, 1199882, verbose=False, ours=True)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====tool======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)

def sota():
    res = ()
    optimal = 1e20
    for q in [2, 4, 8, 16]:
        m_p, m_a = 23, 0
        e = 8
        cand = tuning_algorithm(100, 1e-13, q, e, m_p, m_a, 1199882, verbose=True, ours=False)
        if cand != ():
            q, n, k, d, uber, blksize, overhead = cand
            if overhead < optimal:
                optimal = overhead
                res = (e, m_p, m_a, *cand)
    print("====sota======")
    print("e, m_p, m_a, q, n, k, d, uber, blksize, overhead")
    print(res)


if __name__ == "__main__":
    load_db()
    # compute_rber_e((-0.5, 0.5), False)
    tool()
