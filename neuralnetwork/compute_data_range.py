import sys

def get_range(filename):
    with open(filename, "r") as fin:
        lines = fin.readlines()
        mini, maxi = 1e10, -1e10
        for line in lines:
            line = line.strip()
            data = float(line)
            if data < mini:
                mini = data
            if data > maxi:
                maxi = data
        print(mini, maxi)
        return mini, maxi

def get_range2(filename):
    with open(filename, "r") as fin:
        lines = fin.readlines()
        pos, neg = 1e10, -1e10
        for line in lines:
            line = line.strip()
            data = float(line)
            if data < 0:
                neg = max(neg, data)
            if data > 0:
                pos = min(pos, data)
        print(pos, neg)
        return pos, neg


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = "float"
    get_range(filename)
    get_range2(filename)
