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

def sigma_Based_Read_Range(write_distr, number_of_sigma):
    '''
    Goal: get the read range based on the specified sigma

    write_distr: the resistance distribution of write (no relaxation error)
    number_of_sigma: the SBA technique's input, e.g., 3.
    3 simga is the reported number used in the paper: 
    - Resistive RAM With Multiple Bits Per Cell: Array-Level Demonstration of 3 Bits Per Cell

    API reference:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
    '''
    # here we get the read range based on the specified sigma
    sigma = np.std(write_distr)
    mean = np.mean(write_distr)
    # Get percentiles using Cumulative Distribution Function (cdf) for normal distribution
    # E.g., norm.cdf(-1, loc=0, scale=1) = 15.87%
    # E.g., normal.cdf(1, loc=0, scale=1) = 84.13%
    percentile1 = norm.cdf(-number_of_sigma, loc=0, scale=1)
    percentile2 = norm.cdf(number_of_sigma, loc=0, scale=1)
    # Given the percentile, and the distribution of write, get the read regions
    read_low = norm.ppf(percentile1, loc=mean, scale=sigma)
    read_high = norm.ppf(percentile2, loc=mean, scale=sigma)
    return read_low, read_high

def level_inference(Rmin, Rmax, Nctr, max_attempts, T, number_of_sigma):
    '''
    Rmin, Rmax: set by hardware constraints
    Nctr: how many write center values to try in [Rmin, Rmax]
    max_attempts: the maximum number of attempts, 100 (a fixed number)
    T: time for relaxation, 1s (fixed)
    number_of_sigma: the specification parameter for sigma based technique (SBA)
    '''
    levels = []
    for Wctr in range(Rmin, Rmax, (Rmax-Rmin)//Nctr): # write_center
        for width in range(50, 1000, 100): # write_width: pre-set values during data collection
            # run monte carlo simulation based on measurement data
            Write_N = 1000
            WriteDistr = WriteModel.distr(Wctr, width, max_attempts, Write_N)
            Rlow, Rhigh = sigma_Based_Read_Range(WriteDistr, number_of_sigma)
            if len(levels) == 0:
                levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=0, assertion=True))
                continue
            if Rlow > levels[-1].r2: # current level does not overlap with prior level
                levels.append(Level(Rlow, Rhigh, Wctr-width/2, Wctr+width/2, prob=0, assertion=True))
    return levels


def init():
    WriteModel.data_init()
    RelaxModel.data_init()

def generate_schemes():
    init()
    sigma_start = 3
    sigma_end = 10
    sigma_delta = 1
    while sigma_start <= sigma_end:
        levels = level_inference(Rmin, Rmax, Nctr, max_attempts, timestmp, sigma_start)
        num_level = len(levels)
        print(f"Solved for {num_level}")
        file_tag = f"C13_{num_level}_{sigma_start}.json"
        levels = Level.refine_read_ranges(levels)
        Level.export_to_file(levels, fout="../scheme/SBA/" + file_tag)
        sigma_start += sigma_delta

if __name__ == "__main__":
    init()
    generate_schemes()
