from scipy.special import comb
import pickle

db = {}
# (q, n, k) --> d
# The bound: d <= n - k + 1
# smallest overhead: 1 - k / n

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

def BCH():
    '''
    For any positive integer m >= 3 and t < 2^m-1, there exists a binary BCH code:
    Block length: n = 2^m - 1
    Number of parity-check digits: n - k ≤ mt
    Minimum distance: d_min ≥ 2t + 1.
    '''
    res = P_cw(12, 3, 0.001)
    print(res)
    res = P_cw(12, 3, 0.002)
    print(res)
    res = P_cw(4, 3, 0.002)
    print(res)


def load_db():
    global db
    with open('database.json', 'rb') as fin:
        db = pickle.load(fin)

def select_bound():
    res = []
    for key in db.keys():
        q, n, k = key
        d = db[key]
        assert d <= n - k + 1
        if d == n - k + 1:
            res.append((q, n, k, d))
    return res

def select_ratio(candidates, ratio):
    res = []
    for cand in candidates:
        q, n, k, d = cand
        uber = P_cw(n, int((d-1)/2), 0.0001)
        if uber < ratio:
            res.append(cand)
    return res

def best_overhead(candidates):
    minimum = 10
    best_cand = []
    for cand in candidates:
        q, n, k, d = cand
        overhead = 1 - k / n
        if overhead <= minimum:
            minimum = overhead
            best_cand.append((q, n, k, d))
    return best_cand, overhead


if __name__ == "__main__":
    load_db()
    res = select_bound()
    # print(len(res))
    res = select_ratio(res, 1e-16)
    print(res[:5])
    # cand, overhead = best_overhead(res)
    # print(len(cand), overhead)
    # print(cand)
