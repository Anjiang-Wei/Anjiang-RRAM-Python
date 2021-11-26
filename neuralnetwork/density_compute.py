R=5
exp=7
man=20
def find_2_radix(r):
    for i in range(0, 6):
        res = 2 ** i
        next_res = 2 ** (i + 1)
        if res <= r and r < next_res:
            return i

def cal(R, exp, man):
    print(f"R = {R}, exp = {exp}, man = {man}")
    we_cells = exp + man + 2 # related with rfloat.cpp, leading mantissa needs extra 
    original_cells = 32
    bits_per_cell = find_2_radix(R)# R = [8, 15], bits_per_cell=3
    cells_ = original_cells / bits_per_cell
    sota = original_cells / 2.8
    print("Compared with 2-based fp onto 2-level  /   cell, improvement: ", original_cells / we_cells)
    print("Compared with 2-based fp onto 2-^N levels/ cell, improvement: ", cells_ / we_cells)
    print("Compared with SOTA:                                           ", sota / we_cells)

cal(5, 7, 20)
cal(5, 3, 10)
cal(5, 3, 3)
cal(15, 3, 3)
