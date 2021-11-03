import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

def level_inference(Rmin, Rmax, Nctr, max_attempts, T, BER):
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts
    T: time for relaxation
    BER: bit error rate specification
    '''
    levels = []
    for Wctr in range(Rmin, Rmax, (Rmax-Rmin)/Nctr):
        for width in range(50, 1000, 100): # pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 1000
            Read_N = 1000
            WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
            RelaxDistr = RelaxModel.distr(WriteDistr, T, Read_N)
            Rlow, Rhigh = getReadRange(RelaxDistr, BER)
            levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=1-BER))
    return Level.longest_non_overlap(levels)

def getReadRange(vals, BER):
    num_discard = BER * len(vals) // 2
    sorted_v = sorted(vals)
    return sorted_v[num_discard], sorted_v[-num_discard]


def init():
    WriteModel.data_init()
    RelaxModel.data_init()

if __name__ == "__main__":
    init()
    level_inference()
