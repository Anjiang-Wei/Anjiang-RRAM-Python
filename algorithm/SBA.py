import time
import tqdm
import sys
sys.path.append("..")
from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel
import numpy as np
from scipy.stats import norm

Rmin = 8000
Rmax = 40000
Nctr = 500
max_attempts = 100
timestmp = 1

def sigma_Based_Read_Range(distr, number_of_sigma):
    '''
    Goal: get the read range based on the specified sigma

    distr: the resistance distribution
    number_of_sigma: the SBA technique's input, e.g., 3.
    3 simga is the reported number used in the paper: 
    - Resistive RAM With Multiple Bits Per Cell: Array-Level Demonstration of 3 Bits Per Cell

    API reference:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
    '''
    # here we get the read range based on the specified sigma
    sigma = np.std(distr)
    mean = np.mean(distr)
    # Get percentiles using Cumulative Distribution Function (cdf) for normal distribution
    # E.g., norm.cdf(-1, loc=0, scale=1) = 15.87%
    # E.g., normal.cdf(1, loc=0, scale=1) = 84.13%
    percentile1 = norm.cdf(-number_of_sigma, loc=0, scale=1)
    percentile2 = norm.cdf(number_of_sigma, loc=0, scale=1)
    # Given the percentile, and the distribution of write, get the read regions
    read_low = norm.ppf(percentile1, loc=mean, scale=sigma)
    read_high = norm.ppf(percentile2, loc=mean, scale=sigma)
    return read_low, read_high

def level_inference(Rmin, Rmax, Nctr, max_attempts, T, number_of_sigma, write_model_only):
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts, 100 (a fixed number)
    T: time for relaxation, 1s (fixed)
    number_of_sigma: the specification parameter for sigma based technique (SBA)
    '''
    levels = []
    for Wctr in tqdm.tqdm(range(Rmin, Rmax, (Rmax-Rmin)//Nctr)): # write_center
        for width in range(50, 1000, 100): # write_width: pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 100
            Read_N = 1000
            WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
            if write_model_only:
                distr = WriteDistr
            else:
                distr = RelaxModel.distr(WriteDistr, T, Read_N)
            Rlow, Rhigh = sigma_Based_Read_Range(distr, number_of_sigma)
            try:
                if len(levels) == 0:
                    levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=0, assertion=True))
                    continue
                if Rlow > levels[-1].r2: # current level does not overlap with prior level
                    levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=0, assertion=True))
            except Exception as e:
                continue
    return levels


def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def generate_schemes():
    sigma_start = 0.8
    sigma_end = 2
    sigma_delta = 0.1
    while sigma_start <= sigma_end:
        levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestmp, sigma_start, False)
        num_level = len(levels)
        print(f"Solved for {num_level}")
        file_tag = f"C13_both_{num_level}_{sigma_start}.json"
        levels = Level.refine_read_ranges(levels)
        Level.export_to_file(levels, fout="../scheme/SBA/" + file_tag)
        sigma_start += sigma_delta
    # starts = [1.2, 1.1, 0.9]
    # ends = [1.3, 1.2, 1.0]
    # for kkk in range(len(starts)):
    #     sigma_delta = 0.01
    #     sigma_start = starts[kkk] + sigma_delta
    #     sigma_end = ends[kkk]
    #     while sigma_start < sigma_end:
    #         levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestmp, sigma_start, False)
    #         num_level = len(levels)
    #         print(f"Solved for {num_level}")
    #         file_tag = f"C13_both_{num_level}_{sigma_start}.json"
    #         levels = Level.refine_read_ranges(levels)
    #         Level.export_to_file(levels, fout="../scheme/SBA/" + file_tag)
    #         sigma_start += sigma_delta
def perf_test():
    perf = {}
    starts = [1.6, 1.2, 0.9]
    ends = [1.8, 1.3, 1.0]
    target_levels = [4, 8, 16]
    for kkk in range(len(starts)):
        pre_time = time.time()
        target = target_levels[kkk]
        sigma_delta = 0.01
        sigma_start = starts[kkk] + sigma_delta
        sigma_end = ends[kkk]
        while sigma_start < sigma_end:
            levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestmp, sigma_start, False)
            if len(levels) == target:
                print(f"Solved for {target}")
                post_time = time.time()
                perf[target] = post_time - pre_time
                break
            sigma_start += sigma_delta
        print(perf)
    print(perf)


if __name__ == "__main__":
    init()
    # generate_schemes()
    perf_test()
