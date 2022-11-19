import numpy as np
import pprint

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

# def write_matrix(matrix, filename):
#     with open(filename, "w") as fout:
#         to_write = []
#         for i in range(len(matrix)):
#             to_write.append(",".join(map(str, matrix[i])) + "\n")
#         fout.writelines(to_write)

def compute_average(matrix):
    error_rate = 0
    for i in range(len(matrix)):
        error_rate += 1 - matrix[i][i]
    error_rate = error_rate / len(matrix)
    return error_rate
            
def report_results(filename_prefix, hint):
    res = {}
    for i in range(4, 9):
        fname = filename_prefix + str(i)
        matrix = get_matrix_from_file(fname)
        avg = compute_average(matrix)
        res[i] = avg
    print(hint + " = \\")
    pprint.pprint(res)

if __name__ == "__main__":
    report_results("ours", "our_res")
    report_results("SBA", "sba_res")
    report_results("SBAvar", "sba_our_search")
    report_results("SBAmeanvar", "sba_our_search_mean")
# we should use this file for final results reported in the paper
# instead of scheme_analyze.py (which is non-uniform weighted average)