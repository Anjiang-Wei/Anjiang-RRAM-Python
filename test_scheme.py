import time
from nirram import NIRRAM
import random
from scheme.level import Level
import dead_detection

chipname = "C14"
config_char = "B"
start_addr = 0
end_addr = 65536
dead_cells = []
# export DATE="Oct20" # SBA
# ls scheme/* | grep ${DATE} | sed "s?scheme?'scheme?g" | sed "s?json?json',?g"
level_start = 4
test_scheme_files = [
    'scheme/C14_4_4_0.00390625_1_variantOct22.json',
    'scheme/C14_5_5_0.01953125_1_variantOct22.json',
    'scheme/C14_6_6_0.04296875_1_variantOct22.json',
    'scheme/C14_7_7_0.09375_1_variantOct22.json',
    'scheme/C14_8_8_0.15625_1_variantOct22.json',
]
our_sba = "SBAvariant"
date = "Oct23"
random_seed_start = 10232022
n_cells = 100
timestamps = [0, 0.01, 0.1, 0.2, 0.5, 1.0, 2, 5, 10]


def write_init(addr):
    nisys.set_addr(addr)
    target_low_res = high_init_config[config_char][0]
    target_hi_res = high_init_config[config_char][1]
    reset = nisys.dynamic_reset(target_low_res)
    log.write(f"Init\t{target_low_res}\t{target_hi_res}\t{addr}\t{time.time()}\t{reset[0]}\t{reset[1]}\n")
    time.sleep(1)


def write(addr, target_low_res, target_hi_res):
    assert addr >= start_addr and addr < end_addr
    nisys.set_addr(addr)
    target = nisys.target(target_low_res, target_hi_res, max_attempts=100)
    log.write(f"Write\t{target_low_res}\t{target_hi_res}\t{addr}\t{time.time()}\t{target[0]}\t{target[1]}\n")

def read(addr, read_range_low, read_range_high):
    nisys.set_addr(addr)
    read = nisys.read()
    log.write(f"Read\t{read_range_low}\t{read_range_high}\t{addr}\t{time.time()}\t{read[0]}\t{read[1]}\n")

def dead_init():
    '''
    Consider two log files to initialize the dead cell tracking
    Output -> dead_cells (a global variable)
    '''
    global dead_cells
    with open("log/14dead_test.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    with open("log/14new_dead.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    dead_cells = sorted(set(dead_cells))

def random_pick(ncells):
    random.seed(random_seed)
    res = []
    while len(set(res)) < ncells:
        new = random.randint(start_addr, end_addr-1)
        if new not in dead_cells:
            res.append(new)
    res = sorted(set(res))
    return res

def testscheme(ncells, levels):
    dead_log = open("log/14new_dead.csv", "a")
    cells = random_pick(ncells)
    for level in levels:
        for addr in cells:
            print(addr)
            write_init(addr)
            write(addr, level.w1, level.w2)
            for i in range(1, len(timestamps)):
                time.sleep(timestamps[i] - timestamps[i-1])
                read(addr, level.r1, level.r2)
    print("Start dead cell detection")
    dead_detection.detect(cells, dead_log, nisys)
    dead_log.close()


if __name__ == "__main__":
    dead_init()
    print("Num of dead cells", len(dead_cells))
    nisys = NIRRAM(chipname)
    for exp_id in range(level_start, level_start+len(test_scheme_files)):
        random_seed = random_seed_start + exp_id
        log = open(f"testlog/14scheme_test{our_sba}_{n_cells}_{random_seed}_{exp_id}_{date}", "w")
        levels = Level.load_from_file(test_scheme_files[exp_id-level_start])
        high_init_config = {
            "B": [levels[-1].r1, levels[-1].r2]
        }
        testscheme(n_cells, levels)
    nisys.close()
    log.close()
