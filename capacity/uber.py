from scipy.special import comb
import pickle
import math

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


def load_db():
    global db
    with open('database.json', 'rb') as fin:
        db = pickle.load(fin)


def get_all_candidates(prune=False):
    res = []
    for key in db.keys():
        q, n, k = key
        d = db[key]
        assert d <= n - k + 1
        if prune:
            if d == n - k + 1:
                res.append((q, n, k, d))
        else:
            res.append((q, n, k, d))
    return res

def select_ratio(candidates, ratio):
    res = []
    for cand in candidates:
        q, n, k, d = cand
        p_cw = P_cw(n, int((d-1)/2), 0.01)
        # User_Data_bits_per_CW = log(pow(q^m, k), base=2) = k / log(2, base=q^m)
        bits_per_cw = k / math.log(2, q)
        uber = p_cw / bits_per_cw
        if uber <= ratio:
            res.append((cand, uber))
    return res

def best_overhead(candidates):
    minimum = 10
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


if __name__ == "__main__":
    load_db()
    res = get_all_candidates(prune=False)
    res = select_ratio(res, 1e-16)
    cand, overhead = best_overhead(res)
    print(len(cand), overhead)
    print("q, n, k, d, uber")
    print(cand)
    # RBER: 0.01
    # With Pruning:
    # No

    # Without Pruning:
    # 1 1.6538461538461537
    # q, n, k, d, uber
    # [(16, 129, 78, 33, 7.857483952855776e-17)]