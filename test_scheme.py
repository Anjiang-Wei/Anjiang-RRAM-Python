import time
from nirram import NIRRAM
import random
from scheme.level import Level
import dead_detection

chipname = "C10"
config_char = "B"
start_addr = 0
end_addr = 65536
dead_cells = []
levels = Level.load_from_file("scheme/B_mapping.json")
high_init_config = {
    "B": [86666.666, 200 * 1e3]
}
timestamps = [0.01, 0.1, 1.0]

random_seed = 1

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
    target = nisys.target(target_low_res, target_hi_res, max_attempts=25)
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
    with open("log/dead_test.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    with open("log/new_dead.csv", "r") as fin:
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

def testscheme(ncells):
    dead_log = open("log/new_dead.csv", "a")
    cells = random_pick(ncells)
    for addr in cells:
        print(addr)
        for level in levels:
            write_init(addr)
            write(addr, level.w1, level.w2)
            for t in timestamps:
                time.sleep(t)
                read(addr, level.r1, level.r2)
    print("Start dead cell detection")
    dead_detection.detect(cells, dead_log, nisys)
    dead_log.close()


if __name__ == "__main__":
    dead_init()
    print("Num of dead cells", len(dead_cells))
    nisys = NIRRAM(chipname)
    n_cells = 10
    log = open(f"testlog/scheme_test_{n_cells}_{random_seed}_1", "w")
    testscheme(n_cells)
    nisys.close()
    log.close()
