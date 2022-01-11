from scipy.special import comb
import pickle
import math
import numpy as np

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

def best_overhead(candidates):
    minimum = 10e6
    best_cand = []
    for cand_uber in candidates:
        cand, uber = cand_uber
        q, n, k, d = cand
        overhead = n / k
        if overhead < minimum:
            minimum = overhead
            best_cand = [(q, n, k, d, uber)]
        elif overhead == minimum:
            best_cand.append((q, n, k, d, uber))
    return best_cand, minimum


all_files = []

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

def get_all_q_uber():
    ours_list = ["ours" + str(i) for i in range(6, 17)]
    # sba_list = ["SBA" + str(i) for i in range(4, 17)]
    all_files.extend(ours_list)
    # all_files.extend(sba_list)
    res = []
    for f in all_files:
        matrix = get_matrix_from_file(f)
        n, rber = get_rber_from_matrix(matrix)
        # print(n, rber, f)
        res.append((n, rber))
    return res

def pick_e(I_data, q):
    pass

def pick_mp(n_p, q):
    pass

def pick_nkd(k_max, p_rel):
    pass

def pick_ma(n_a, q):
    pass

def tuning_algorithm(n_max, p_rel, I_data, n_p, n_a):
    '''
    Arg list:
    n_max: # maximum fp values for batched read
    p_rel: spec for reliable storage, UBER
    I_data: tuple, range of data
    n_p: number of precise digits (base-10)
    n_a: number of approximate digits (base-10)

    Other args:
    m_p: # precise mantissa
    m_a: # approximate mantissa
    e: # exponent bits
    q: base (q^m)
    <n, k, d>: linear code params
    '''
    for q, rber in get_all_q_uber():
        e = pick_e(I_data, q)
        m_p = pick_mp(n_p, q)
        n, k, d = pick_nkd(n_max * (e+m_p+1), p_rel)
        m_a = pick_ma(n_a, q)


if __name__ == "__main__":
    load_db()
    for intended_q, rber in get_all_q_uber():
        require_uber = 1e-14
        res = get_all_candidates(intended_q)
        res = select_ratio(res, require_uber, rber)
        print(f"q={intended_q}, n, k, d, uber<{require_uber}, candidates = {len(res)}")
        cand, overhead = best_overhead(res)
        if len(cand) == 0:
            print("no solution")
        else:
            print(cand, f"overhead={overhead}")
