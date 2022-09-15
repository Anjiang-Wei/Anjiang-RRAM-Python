def get_R_range(m, num_level):
    if m == 1.088 and num_level == 8:
        return [0, 532, 782, 1215, 2034, 3793, 13192, 0]
    if m == 1.205 and num_level == 8:
        return [0, 597, 903, 1454, 2538, 4968, 16164, 0]
    if m == 4.18 and num_level == 4:
        return [0, 3790, 19974, 0]
    else:
        assert(False)

def compute(num_level, Rpre_max, Rfinal_min, V_BL, delta_I, m):
    # R_range obtained from graph based on the chosen m
    R_range = get_R_range(m, num_level)

    res = [(0, Rpre_max)]
    for i in range(1, num_level-1):
        premax = res[-1][1]
        # V_BL[i] / premax - V_BL[i] / Rcur_min = 2*delta_I
        Rcur_min = V_BL[i] / (V_BL[i] / premax - 2*delta_I)
        Rcur_max = Rcur_min + R_range[i]
        res.append((Rcur_min, Rcur_max))

    res.append((Rfinal_min, 1e6))
    print(res)
    return res

if __name__ == "__main__":
    compute(8, 3200, 39902, [0] + [0.20] * 7, 1e-6, 1.088)
    V_BL = [0, 0.20, 0.22, 0.23, 0.24, 0.25, 0.28, 0.40]
    compute(8, 3200, 39978, V_BL, 1e-6, 1.205)
    compute(4, 3500, 39970, [0, 0.2, 0.25, 0.4], 2*1e-6, 4.18)
