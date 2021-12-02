import tqdm
import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

Rmin = 8000
Rmax = 40000
Nctr = 500
max_attempts = 100
timestmp = 1

def level_inference(Rmin, Rmax, Nctr, max_attempts, T, BER):
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
            Read_N = 1000
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

def minimal_BER(specified_levels, eps, timestamp):
    low_BER, high_BER = 0, 1
    while high_BER - low_BER > eps:
        cur_BER = (low_BER + high_BER) / 2
        cur_levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestamp, cur_BER)
        if len(cur_levels) < specified_levels: # the precision requirement is too strict to be met
            low_BER = cur_BER # make BER looser
        elif len(cur_levels) > specified_levels:
            high_BER = cur_BER
        else:
            high_BER = cur_BER
            best_level, best_BER = cur_levels, cur_BER
    return best_level, best_BER

if __name__ == "__main__":
    init()
    for num_level in range(6, 33):
        levels, ber = minimal_BER(num_level, 0.001, timestmp)
        print(f"Solved for {num_level}: {len(levels)}, {ber}")
        file_tag = "C13_" +  str(num_level) + "_" + str(len(levels)) + "_" + str(ber) + "_" + str(timestmp) + ".json"
        Level.export_to_file(levels, fout="../scheme/" + file_tag)
