logfiles = [
    'testlog/13scheme_test_100_9_6_Dec6',
    'testlog/13scheme_test_100_10_7_Dec6',
    'testlog/13scheme_test_100_11_8_Dec6',
    'testlog/13scheme_test_100_12_9_Dec6',
    'testlog/13scheme_test_100_13_10_Dec6',
    'testlog/13scheme_test_100_14_11_Dec6',
    'testlog/13scheme_test_100_15_12_Dec6',
    'testlog/13scheme_test_100_16_13_Dec6',
    'testlog/13scheme_test_100_17_14_Dec6',
    'testlog/13scheme_test_100_18_15_Dec6',
    'testlog/13scheme_test_100_19_16_Dec6',
]

'''
test_scheme_files = [
    '6, 0.02',
    '7, 0.01',
    '8, 0.05',
    '10, 0.1',
    '12, 0.15',
    '13, 0.2',
    '16, 0.3'
]
'''

timestamp = [0, 0.01, 0.1, 0.2, 0.5, 1.0, 2, 5, 10]

all_lows = []
dead_cells = []

class Result(object):
    init = []
    write = []
    read = []
    all = []
    def __init__(self, action, addr, low, high, final, success, time):
        self.action = action
        self.addr = addr
        self.low = low
        self.high = high
        self.final = final
        self.success = success
        self.time = time

    def check_range(low, high, value):
        assert low < high
        if low <= value and value <= high:
            return True
        else:
            return False
        
    def compute_prob(results, hint):
        total = len(results)
        fail = 0
        fail_addr = []
        for v in results:
            if v.success == False:
                fail += 1
                # print(v.addr, v.low, v.high, v.final)
                fail_addr.append(v.addr)
        if total == 0:
            return
        print(f"Failure rate for {hint}: {fail} / {total} = {fail/total}")
        return set(fail_addr), fail/total
    
    def analyze_level_prob(results):
        for i in range(0, len(all_lows), 2):
            filtered_res_write = list(filter(lambda x: x.low == all_lows[i+1] and x.action == "Write", results))
            write_fail_addr, write_failrate = Result.compute_prob(filtered_res_write, str(i/2) + "+write")
            filtered_res_read = list(filter(lambda x: x.low == all_lows[i] and x.action == "Read", results))
            read_fail_addr, read_failrate = Result.compute_prob(filtered_res_read, str(i/2) + "+read")
            both_fail = write_fail_addr & read_fail_addr
            both_fail_prob = len(both_fail) / len(filtered_res_write)
            if write_failrate != 0:
                print(f"P(read_fail | write_fail) = {both_fail_prob}/{write_failrate} = {both_fail_prob/write_failrate}")
    
    def report_by_elasped_time(results, num_cat, only_report=None, hint=""):
        # results are only about read, assuming all read for same address are consecutive
        # num_cat is the number of timestamps
        categorized = {}
        for i in range(num_cat):
            categorized[i] = []
        assert len(results) % num_cat == 0
        for i in range(0, len(results)):
            categorized[i%num_cat].append(results[i])
        if only_report is not None:
            Result.compute_prob(categorized[only_report], hint)
            return
        for i in range(num_cat):
            Result.compute_prob(categorized[i], "timebin_" + str(i))


def data_init(logfile):
    global all_lows
    with open(logfile, "r") as fin:
        lines = fin.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _ = line
            low, high, addr, time, final = float(low), float(high), int(addr), float(time), float(final)
            success = Result.check_range(low, high, final)
            r = Result(action, addr, low, high, final, success, time)
            if addr in dead_cells:
                # print(f"{addr} is dead, skipping")
                continue           
            if action == "Init":
                assert i % (len(timestamp) + 1) == 0
                Result.init.append(r)
            elif action == "Write":
                assert i % (len(timestamp) + 1) == 1
                Result.write.append(r)
                if low not in all_lows:
                    all_lows.append(low)
            else:
                assert action == "Read"
                assert i % (len(timestamp) + 1) >= 2
                Result.read.append(r)
                if low not in all_lows:
                    all_lows.append(low)
            Result.all.append(r)
    all_lows = sorted(set(all_lows))
    # print(all_lows)

def clear():
    global all_lows
    all_lows = []
    Result.init = []
    Result.write = []
    Result.read = []
    Result.all = []

def dead_cell_init(logdir=""):
    '''
    Consider two log files to initialize the dead cell tracking
    Output -> dead_cells (a global variable)
    '''
    if logdir == "":
        logdir = 'log/'
    global dead_cells
    with open(logdir + "13dead_test.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    with open(logdir + "13new_dead.csv", "r") as fin:
        lines = fin.readlines()
        for line in lines:
            if "False" in line:
                dead_addr = int(line.split(",")[0])
                dead_cells.append(dead_addr)
    dead_cells = sorted(set(dead_cells))
    print(f'Dead cell initialization finished: {len(dead_cells)} are dead')


if __name__ == "__main__":
    dead_cell_init()
    for i in range(len(logfiles)):
        clear()
        data_init(logfiles[i])
        # init_bad = Result.compute_prob(Result.init, "init")
        # write_bad = Result.compute_prob(Result.write, "write")
        # read_bad = Result.compute_prob(Result.read, "read")
        # all_bad = Result.compute_prob(Result.all, "all")
        # Result.analyze_level_prob(Result.all)
        # [0, 0.01, 0.1, 0.2, 0.5, 1.0, 2, 5, 10]
        Result.report_by_elasped_time(Result.read, len(timestamp) - 1, only_report=5, hint=str(i + 6))
        # print(sorted(set(init_bad)))
        # print(sorted(set(write_bad)))
        # print(sorted(set(read_bad)))
        # print(sorted(set(all_bad)))
