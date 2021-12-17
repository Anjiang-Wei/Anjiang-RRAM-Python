from scipy.special import xlogy
import math
good = False
"""
    https://colab.research.google.com/github/cvxpy/cvxpy/blob/master/examples/notebooks/WWW/Channel_capacity_BV4.57.ipynb
"""

import cvxpy as cp
import numpy as np

def channel_capacity(n, m, P, sum_x=1):
    '''
    Boyd and Vandenberghe, Convex Optimization, exercise 4.57 page 207
    Capacity of a communication channel.
    
    We consider a communication channel, with input X(t)∈{1,..,n} and
    output Y(t)∈{1,...,m}, for t=1,2,... .The relation between the
    input and output is given statistically:
    p_(i,j) = ℙ(Y(t)=i|X(t)=j), i=1,..,m  j=1,...,n
    
    The matrix P ∈ ℝ^(m*n) is called the channel transition matrix, and
    the channel is called a discrete memoryless channel. Assuming X has a
    probability distribution denoted x ∈ ℝ^n, i.e.,
    x_j = ℙ(X=j), j=1,...,n
    
    The mutual information between X and Y is given by
    ∑(∑(x_j p_(i,j)log_2(p_(i,j)/∑(x_k p_(i,k)))))
    Then channel capacity C is given by
    C = sup I(X;Y).
    With a variable change of y = Px this becomes
    I(X;Y)=  c^T x - ∑(y_i log_2 y_i)
    where c_j = ∑(p_(i,j)log_2(p_(i,j)))
    '''
    
    # n is the number of different input values
    # m is the number of different output values
    if n*m == 0:
        print('The range of both input and output values must be greater than zero')
        return 'failed', np.nan, np.nan

    # x is probability distribution of the input signal X(t)
    x = cp.Variable(shape=n)
    
    # y is the probability distribution of the output signal Y(t)
    # P is the channel transition matrix
    y = P@x
    
    # I is the mutual information between x and y
    c = np.sum(np.array((xlogy(P, P) / math.log(2))), axis=0)
    # c = np.sum(P*np.log2(P),axis=0)
    I = c@x + cp.sum(cp.entr(y) / math.log(2))

    # Channel capacity maximised by maximising the mutual information
    obj = cp.Minimize(-I)
    constraints = [cp.sum(x) == sum_x,x >= 0]
    
    # Form and solve problem
    prob = cp.Problem(obj,constraints)
    prob.solve()
    if prob.status=='optimal':
        return prob.status, -prob.value, x.value
    else:
        return prob.status, np.nan, np.nan

def compute_level():
    ours_1 = {4: 1.0, # manually added
            5: 1.0, # manually added
            6: 0.995,
            7: 0.9885714285714285,
            8: 0.9825,
            9: 0.9811111111111112,
            10: 0.95,
            11: 0.9581818181818181,
            12: 0.9341666666666667,
            13: 0.926923076923077,
            14: 0.9185714285714286,
            15: 0.8986666666666667,
            16: 0.878125}
    ours_10 = {4: 1.0,
            5: 1.0,
            6: 0.9833333333333333,
            7: 0.9671428571428572,
            8: 0.94875,
            9: 0.9366666666666666,
            10: 0.915,
            11: 0.9027272727272727,
            12: 0.8733333333333333,
            13: 0.8576923076923078,
            14: 0.85,
            15: 0.7866666666666666,
            16: 0.781875}
    sba_1 =  {4: 0.9075,
            5: 0.9,
            6: 0.91,
            7: 0.9114285714285715,
            8: 0.8888888888888888,
            9: 0.8611111111111112,
            10: 0.88,
            11: 0.8927272727272727,
            12: 0.8666666666666667,
            13: 0.8392307692307692,
            14: 0.8514285714285714,
            15: 0.8200000000000001,
            16: 0.815625}
    sba_10 = {4: 0.9025,
            5: 0.868,
            6: 0.87,
            7: 0.8542857142857143,
            8: 0.8371212121212122,
            9: 0.7911111111111111,
            10: 0.798,
            11: 0.8045454545454546,
            12: 0.7658333333333334,
            13: 0.7384615384615385,
            14: 0.7235714285714285,
            15: 0.688,
            16: 0.68125}
    to_try_dict = [ours_1, sba_1, ours_10, sba_10]
    for try_dict in to_try_dict:
        for levels in range(4, 17):
            r = try_dict[levels]
            n = levels # input symbols
            m = levels # output symbols
            # $p_{ij} = \mathbb{P}(Y(t)=i | X(t)=j)$
            P = np.zeros((levels,levels))
            for i in range(levels):
                P[i][i] = r
                if i == 0:
                    P[i+1][i] = 1-r
                elif i == levels-1:
                    P[i-1][i] = 1-r
                else:
                    P[i-1][i] = (1-r)/2
                    P[i+1][i] = (1-r)/2
            # if levels <= 6:
            #     print(P)
            stat, C, x = channel_capacity(n, m, P)
            assert stat == "optimal"
            print('level = {:d}, C = {:.4f}'.format(levels, C))
            # print('Optimal variable x = \n', x)
        print("=============")


def test():
    n = 2
    m = 2
    P = np.array([[0.75, 0.25],
                [0.25,0.75]])
    stat, C, x = channel_capacity(n, m, P)
    assert stat == "optimal"
    print("{:.4g}".format(C)) # 0.1887
    print(x)

    n = 2
    m = 3
    P = np.array([[0.8, 0],
                [0.2, 0.2],
                [0, 0.8]])
    stat, C, x = channel_capacity(n, m, P)
    assert stat == "optimal"
    print("{:.4g}".format(C)) # 0.8
    print(x)

    n = 4
    m = 4
    P = np.array([[0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
    stat, C, x = channel_capacity(n, m, P)
    assert stat == "optimal"
    print("{:.4g}".format(C)) # 2
    print(x)

if __name__ == "__main__":
    # test()
    compute_level()
