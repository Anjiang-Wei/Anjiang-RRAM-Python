import numpy as np

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

def write_matrix(matrix, filename):
    with open(filename, "w") as fout:
        to_write = []
        for i in range(len(matrix)):
            to_write.append(",".join(map(str, matrix[i])) + "\n")
        fout.writelines(to_write)

def trans(int1, merge, prefix):
    m1 = get_matrix_from_file(prefix + str(int1))
    print(m1)
    int2 = int1 - 1
    m2 = np.zeros((int2, int2))
    for i in range(int2):
        for j in range(int2):
            if i == merge or j == merge:
                continue
            idxi = i
            idxj = j
            if i > merge:
                idxi += 1
            if j > merge:
                idxj += 1
            m2[i][j] = m1[i if i < merge else (i + 1)][j if j < merge else (j + 1)]
    for j in range(int1):
        m1[merge][j] += m1[merge+1][j]
    for i in range(int1):
        m1[i][merge] += m1[i][merge+1]
    for j in range(int2):
        m2[merge][j] = m1[merge][j if j <= merge else (j + 1)]
    for i in range(int2):
        m2[i][merge] = m1[i if i <= merge else (i + 1)][merge] / 2
    print(m2)
    write_matrix(m2, prefix + str(int2))

if __name__ == "__main__":
    trans(6, 2, prefix="ours")
    trans(5, 1, prefix="ours")

