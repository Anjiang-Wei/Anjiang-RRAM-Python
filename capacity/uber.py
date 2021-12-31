from scipy.special import comb

def P_cw(N, E, RBER):
    '''
    N: block length; the number of cells for output [length of codeword]
    E: the number of errors that can be corrected
    RBER: Raw BER; the probability of level drift; worst case analysis
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


if __name__ == "__main__":
    BCH()
