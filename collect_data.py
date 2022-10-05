import time
from nirram import NIRRAM
import random
import dead_detection

chipname = "C13"
config_char = "B"
start_addr = 0
end_addr = 65536
lowest_target = 7812.5
dead_cells = []
# levels = Level.load_from_file("scheme/B_mapping.json")
high_init_config = {
    "B": [30000, 200 * 1e3]
}

timestamps = [0.01, 0.1-0.01, 1.0-0.1, 2.0-1.0]

random_seed = 1
exp_id = 0

def write_init(addr):
    nisys.set_addr(addr)
    target_low_res = high_init_config[config_char][0]
    target_hi_res = high_init_config[config_char][1]
    reset = nisys.dynamic_reset(target_low_res)
    log.write(f"Init\t{target_low_res}\t{target_hi_res}\t{addr}\t{time.time()}\t{reset[0]}\t{reset[1]}\t0\n")
    time.sleep(1)


def write(addr, target_low_res, target_hi_res, attempts):
    assert addr >= start_addr and addr < end_addr
    if target_low_res < lowest_target:
        print("Too low, skip!")
        return -1
    nisys.set_addr(addr)
    target = nisys.target(target_low_res, target_hi_res, max_attempts=attempts)
    log.write(f"Write\t{target_low_res}\t{target_hi_res}\t{addr}\t{time.time()}\t{target[0]}\t{target[1]}\t{attempts}\n")
    return 0

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


def is_dead(addr):
    return addr in dead_cells

def random_pick(ncells):
    random.seed(random_seed)
    res = []
    while len(set(res)) < ncells:
        new = random.randint(start_addr, end_addr-1)
        if new not in dead_cells:
            res.append(new)
    res = sorted(set(res))
    return res

def collect(ncells):
    cells = random_pick(ncells)
    w_centers = list(range(7800, 10000, 200)) # 11
    w_centers += list(range(10000, 20000, 1000)) # 10
    w_centers += list(range(20000, 42000, 2000)) # 11
    print(len(w_centers), w_centers)
    # w_centers = [7822.5, 8002.5, 8182.5, 8362.5, 8542.5, \
    #             8722.5, 8902.5, 9082.5, 9382.5, 9792.5, \
    #             10202.5, 10612.5, 11342.5, 12452.5, 14382.5, \
    #             18682.5, 22000.0, 26442.5, 32000.0, 39502.5]
    for w_center in w_centers:
        # for num_attempts in [10, 25, 50, 100]:
        for width in range(50, 1000, 100):
            if w_center-width/2 < lowest_target:
                continue
            if w_center < 14000 and width > 500:
                continue
            for addr in cells:
                if is_dead(addr):
                    continue
                print(addr)
                write_init(addr)
                ret = write(addr, w_center-width/2, w_center+width/2, 100) # num_attempts=100
                if ret == -1:
                    continue # skip the read if write is skipped
                for t in timestamps:
                    time.sleep(t)
                    read(addr, -1, -1)
        print("Start dead cell detection")
        dead_log = open("log/14new_dead.csv", "a")
        dead_detection.detect(cells, dead_log, nisys, already_dead=dead_cells)
        dead_log.close()
        dead_init()


if __name__ == "__main__":
    dead_init()
    print("Num of dead cells", len(dead_cells))
    nisys = NIRRAM(chipname)
    n_cells = 100
    log = open(f"testlog/14collect_data_{n_cells}_{random_seed}_{exp_id}", "w")
    collect(n_cells)
    nisys.close()
    log.close()
