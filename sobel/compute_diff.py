import sys

def get_int_list(f):
    res = []
    with open(f, "r") as fin:
        lines = fin.readlines()
        for line in lines:
            line = line.strip()
            for eint in line.split():
                res.append(int(eint))
    return res

def root_mean_square(a1, a2):
    res = 0
    for i in range(0, len(a1)):
        res += (a1[i] - a2[i]) * (a1[i] - a2[i])
    res = res / len(a1)
    return res ** 0.5


def diff(f1, f2):
    res1 = get_int_list(f1)
    res2 = get_int_list(f2)
    assert len(res1) == len(res2)
    return root_mean_square(res1, res2)

def all_files(suffix):
    res1 = []
    res2 = []
    for i in range(1, 38):
        if i == 29:
            continue
        res1.append("intermediate/" + str(i) + "." + suffix)
        res2.append("mutated/" + str(i) + "." + suffix)
    assert len(res1) == 36 and len(res2) == 36
    return res1, res2

def diffall(only3):
    f1s, f2s = all_files("out")
    if only3:
        f1s, f2s = f1s[:3], f2s[:3]
    all_diff = 0
    for i in range(0, len(f1s)):
        ediff = diff(f1s[i], f2s[i])
        all_dff += ediff
    return all_diff / len(f1s)

if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    res = diff(f1, f2)
    print(res)
