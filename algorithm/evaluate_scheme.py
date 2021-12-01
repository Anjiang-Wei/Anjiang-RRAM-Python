import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def evaluate_levels(levels):
    Write_N = 1000
    Read_N = 1000
    max_attempts = 100
    T = 1
    success = 0
    total = 0
    for i in range(len(levels)):
        level = levels[i]
        r1, r2, w1, w2 = level.r1, level.r2, level.w1, level.w2
        assert r1 < w1 and w1 < w2 and w2 < r2
        WriteDistr = WriteModel.distr((w1+w2)/2, w2-w1, max_attempts, Write_N)
        RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
        for dp in RelaxDistr:
            if i == 0:
                if dp < r2:
                    success += 1
            elif i == len(levels) - 1:
                if dp > r1:
                    success += 1
            else:
                if r1 < dp and dp < r2:
                    success += 1
            total += 1
    print(f"{filename}: {1 - (success/total)}")


if __name__ == "__main__":
    init()
    filename = sys.argv[1]
    levels = Level.load_from_file(filename)
    evaluate_levels(levels)
