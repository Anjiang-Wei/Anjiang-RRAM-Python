import tqdm
import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

def sba(Rmin, Rmax, Nctr, max_attempts, T, BER):
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts
    T: time for relaxation
    BER: bit error rate specification
    '''
    levels = []
    for Wctr in tqdm.tqdm(range(Rmin, Rmax, (Rmax-Rmin)//Nctr)):
        for width in range(50, 1000, 100): # pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 100
            Read_N = 100
            WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
            try:
                RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
                Rlow, Rhigh = getReadRange(RelaxDistr, BER)
                levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=1-BER, assertion=True))
            except Exception as e:
                # print(f"{str(e)}: {Rlow}, {Rhigh}, {Wctr-width/2}, {Wctr+width/2}")
                continue
    return Level.longest_non_overlap(levels)

def getReadRange(vals, BER):
    num_discard = int(BER * len(vals) / 2)
    # print(f'from {len(vals)} delete {num_discard}')
    sorted_v = sorted(vals)
    return sorted_v[num_discard], sorted_v[-num_discard]


def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def level_inference_test():
    import numpy as np
    max_attempts = 50
    Rmin, Rmax = 8000, 50000-1000
    Nctr = 100
    T = 1
    for Wctr in range(Rmin, Rmax, (Rmax-Rmin)//Nctr):
        width_mean = {}
        width_std = {}
        for width in range(50, 1000, 100): # pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 100
            Read_N = 100
            WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
            try:
                RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
                w_mean, w_std = np.mean(WriteDistr), np.std(WriteDistr)
                r_mean, r_std = np.mean(RelaxDistr), np.std(RelaxDistr)
                # print(Wctr, width, ":", w_mean, r_mean, w_std, r_std)
                width_mean[width] = float(abs(r_mean - Wctr))
                width_std[width] = float(r_std)
            except Exception as e:
                # print(f'{e}')
                continue
        std_best_width = min(width_std, key=width_std.get)
        mean_best_width = min(width_mean, key=width_mean.get)
        print(Wctr, std_best_width, mean_best_width)

if __name__ == "__main__":
    init()
    # level_inference_test()
    #            Rmin,   Rmax,     Nctr,att, T, BER 
    levels = sba(8000, 50000-1000, 400, 100, 1, 0.003) # 5 -> 2bit
    print(len(levels))
    levels = sba(8000, 50000-1000, 400, 100, 1, 0.01) # 5 -> 3bit
    print(len(levels))