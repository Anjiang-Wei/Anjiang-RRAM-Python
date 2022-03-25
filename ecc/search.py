from scipy.special import comb
import pickle
import math
import numpy as np
import pprint

db = {}
# (base, n, k) --> d
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


def RS():
    '''
    <n, k, n-k+1>_[p^m]: n <= p^m, p = 2
    '''
    res = {}
    p = 2
    for base in range(1, 12):
        for n in range(2, (p**base) + 1):
            for k in range(1, n):
                d = n - k + 1
                new_key = (base, n, k)
                res[new_key] = d
    print(res)
    return res

def Hamming():
    '''
    <2^r - 1, 2^r - r - 1, 3> (r >= 2)
    '''
    res = {}
    for r in range(2, 12):
        n = (2 ** r) - 1
        k = (2 ** r) - r - 1
        d = 3
        new_key = (1, n, k)
        res[new_key] = d
    print(res)
    return res

def BCH():
    '''
    https://web.ntpu.edu.tw/~yshan/BCH_code.pdf --> BCH.txt
    d = 2t + 1
    '''
    res = {}
    with open("BCH.txt", "r") as fin:
        lines = fin.readlines()[1:]
        for line in lines:
            n, k, t = map(int, line.split(","))
            d = 2 * t + 1
            new_key = (1, n, k)
            res[new_key] = d
    print(res)
    return res

def merge(dict1, dict2):
    # merge two dicts and reserve max
    res = dict2.copy()
    for key in dict1.keys():
        if key not in res.keys():
            res[key] = dict1[key]
        else:
            res[key] = max(dict1[key], dict2[key])
    return res

def mergeall(dicts):
    assert len(dicts) > 0
    if len(dicts) == 1:
        return dicts[0]
    if len(dicts) == 2:
        return merge(dicts[0], dicts[1])
    res = merge(dicts[0], dicts[1])
    for edict in dicts[2:]:
        res = merge(res, edict)
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


if __name__ == "__main__":
    RS()
