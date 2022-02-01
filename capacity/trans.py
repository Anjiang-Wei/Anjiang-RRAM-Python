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

def trans(int1, prefix):
    m1 = get_matrix_from_file(prefix + str(int1))
    print(m1)
    int2 = int1 // 2
    m2 = np.zeros((int2, int2))
    for i in range(int2):
        for j in range(int2):
            m2[i][j] = (m1[i*2][j*2] + m1[i*2][j*2+1] + m1[i*2+1][j*2] + m1[i*2+1][j*2+1]) / 2
    print(m2)
    write_matrix(m2, prefix + str(int2))

if __name__ == "__main__":
    trans(10, prefix="ours")
    trans(8, prefix="ours")
