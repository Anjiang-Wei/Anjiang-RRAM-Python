num_level = 8
Rpre_max = 3200
Rfinal_min = 39902
V_BL = [0] + [0.20] * (num_level - 1)

delta_I = 1e-6

# R_range obtained from graph based on the chosen m
m = 1.088
R_range = [0, 532, 782, 1215, 2034, 3793, 13192, 0]

res = [(0, Rpre_max)]
for i in range(1, num_level-1):
    premax = res[-1][1]
    # V_BL[i] / premax - V_BL[i] / Rcur_min = 2*delta_I
    Rcur_min = V_BL[i] / (V_BL[i] / premax - 2*delta_I)
    Rcur_max = Rcur_min + R_range[i]
    res.append((Rcur_min, Rcur_max))

res.append((Rfinal_min, 1e6))
print(res)
