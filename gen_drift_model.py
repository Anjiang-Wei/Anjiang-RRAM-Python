logfile = "testlog/14collect_data_100_1_0"

# R[timept][R_0] -> R_t
R = {}
times = [] # [0.0, 0.01, 0.1, 1.0, 2.0]

# d[timept][R_0] -> R_t - R_0
d = {}

# write_center: (w_low + w_high) / 2 --> list of R_0
write_centers = {}


model_char = "C14"
config = {
    # maxi, mini of resistance range
    "C14": [40 * 1e3, 8000]
}
dead_cells = []
# the number of times for read --> corresponding timestamps
read2time = {0: 0.0, 1: 0.01, 2: 0.1, 3: 1, 4: 2}

fixed_timept = 1.0

def dead_cell_init(logdir=""):
    '''
    Consider two log files to initialize the dead cell tracking
    Output -> dead_cells (a global variable)
    '''
    if logdir == "":
        logdir = 'log/'
    global dead_cells
    with open(logdir + "14dead_test.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    with open(logdir + "14new_dead.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    dead_cells = sorted(set(dead_cells))
    print(f'Dead cell initialization finished: {len(dead_cells)} are dead')

def init(fname=""):
    if fname == "":
        fname = logfile
    with open(fname, "r") as fin:
        lines = fin.readlines()
        read_cnt = 0
        resistance_0 = 0
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            if line[0] == "Init":
                read_cnt = 0
                continue
            if line[0] == "Write":
                assert read_cnt == 0, read_cnt
                action, low, high, addr, t, final, _, max_attempts = line
                resistance, addr = float(final), int(addr)
                low, high = float(low), float(high)
                if addr in dead_cells:
                    continue
                if 0 not in R.keys():
                    R[0] = {}
                R[0][resistance] = resistance
                resistance_0 = resistance
                read_cnt += 1
                w_center = (low + high) / 2
                if w_center not in write_centers:
                    write_centers[w_center] = []
                write_centers[w_center].append(resistance_0)
            else:
                action, low, high, addr, t, final, _ = line
                resistance_t, addr = float(final), int(addr)
                timept = read2time[read_cnt]
                read_cnt += 1
                if addr in dead_cells:
                    continue
                if timept not in R.keys():
                    R[timept] = {}
                R[timept][resistance_0] = resistance_t
    global times
    times = sorted(list(R.keys()))

def compute_d():
    '''
    Compute the difference w.r.t time, given the same address [same initial g0]
    '''
    for t in times[1:]:
        if t not in d.keys():
            d[t] = {}
        for r_0 in R[t].keys():
            assert R[0][r_0] == r_0
            d[t][r_0] = R[t][r_0] - R[0][r_0]


def export(vals, append=True):
    vals_ = list(map(str, vals))
    with open("models/conf" + model_char, "a" if append else "w") as fout:
        fout.write(",".join(vals_) + "\n")

def to_conf():
    w_smallest, w_biggest = min(write_centers.keys()), max(write_centers.keys())
    export([w_smallest, w_biggest], append=False)
    for t in times[1:]:
        for w_center in write_centers.keys():
            r0_list = write_centers[w_center]
            diff_list = list(map(lambda x: d[t][x], r0_list))
            t_w_diff = [t] + [w_center] + diff_list
            export(t_w_diff)


if __name__ == "__main__":
    dead_cell_init()
    init()
    compute_d()
    to_conf()
