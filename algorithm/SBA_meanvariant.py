import numpy as np
import time
import tqdm
import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

Rmin = 8000
Rmax = 40000
Nctr = 500
max_attempts = 25
timestmp = 1
date="meanvariantOct24"

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
            # Write_N = 176
            # WriteDistr = WriteModel.distr(Wctr, width, max_attempts)
            # RelaxDistr = RelaxModel.distr(WriteDistr, T)
            sigma = RelaxModel.distr_sigma(Wctr, timestmp)
            mean_delta = RelaxModel.distr_mean(Wctr, timestmp)
            sigma_distr = np.random.normal(Wctr + mean_delta, sigma, 1000)
            Rlow, Rhigh = getReadRange(sigma_distr, BER)
            if Wctr-width/2 < Rmin:
                Rlow = 0
            try:
                # level = 5,6 needs this fix, otherwise the hardware assertion in the write algorithm fails
                if Wctr - width / 2 <= 7812.5: # 1 / (128 uS)
                    continue
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

def minimal_BER(specified_levels, eps, timestamp, low_BER = 0, high_BER = 1):
    first = True
    while high_BER - low_BER > eps:
        cur_BER = (low_BER + high_BER) / 2
        cur_levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestamp, cur_BER)
        print(len(cur_levels), cur_BER)
        if first:
            best_level, best_BER = cur_levels, cur_BER # make sure that there is a solution
            first = False
        if len(cur_levels) < specified_levels: # the precision requirement is too strict to be met
            low_BER = cur_BER # make BER looser
        elif len(cur_levels) > specified_levels:
            high_BER = cur_BER
        else:
            high_BER = cur_BER
            best_level, best_BER = cur_levels, cur_BER
    return best_level, best_BER

def generate_schemes():
    init()
    for num_level in range(4, 9):
        levels, ber = minimal_BER(num_level, 0.005, timestmp)
        print(f"Solved for {num_level}: {len(levels)}, {ber}")
        file_tag = "C14_" +  str(num_level) + "_" + str(len(levels)) + "_" + str(ber) + "_" + str(timestmp) + "_" + date + ".json"
        levels = Level.refine_read_ranges(levels)
        Level.export_to_file(levels, fout="../scheme/" + file_tag)

def fix_5_6():
    init()
    for num_level in range(5, 7):
        levels, ber = minimal_BER(num_level, 0.005, timestmp)
        print(f"Solved for {num_level}: {len(levels)}, {ber}")
        file_tag = "C14_" +  str(num_level) + "_" + str(len(levels)) + "_" + str(ber) + "_" + str(timestmp) + "_" + date + ".json"
        levels = Level.refine_read_ranges(levels)
        Level.export_to_file(levels, fout="../scheme/" + file_tag)

def refine_levels():
    filename = sys.argv[1]
    levels = Level.load_from_file(filename)
    new_levels = Level.refine_read_ranges(levels)
    Level.export_to_file(new_levels, fout=filename)

def evaluate_perf():
    init()
    perf = {}
    for num_level in [4, 8, 16]:
        pre_time = time.time()
        if num_level == 4:
            levels, ber = minimal_BER(num_level * 2, 0.001, timestmp, 0, 0.0625)
            levels = Level.merge_adjacent(levels)
            ber = ber / 2
        elif num_level == 16:
            levels, ber = minimal_BER(num_level, 0.005, timestmp, 0.125, 0.25)
        else:
            levels, ber = minimal_BER(num_level, 0.001, timestmp, 0, 0.0625)
        print("success", len(levels), ber)
        post_time = time.time()
        perf[num_level] = post_time - pre_time
    print(perf)


if __name__ == "__main__":
    generate_schemes()
    # fix_5_6()
    # refine_levels()
    # evaluate_perf()