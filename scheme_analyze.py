import pprint
import numpy as np
'''
export DATE="Oct21"
ls testlog/* | grep ${DATE} | sed "s?testlog?'testlog?g" | sed "s?${DATE}?${DATE}',?g"
'''
skip_write_fail = True
logfiles = [
    'testlog/14scheme_testours_100_2024_4_Oct20',
    'testlog/14scheme_testours_100_2025_5_Oct20',
    'testlog/14scheme_testours_100_2026_6_Oct20',
    'testlog/14scheme_testours_100_2027_7_Oct20',
    'testlog/14scheme_testours_100_2028_8_Oct20',
]
logfiles2 = [
    'testlog/14scheme_testSBA_100_202214_4_Oct21',
    'testlog/14scheme_testSBA_100_202215_5_Oct21',
    'testlog/14scheme_testSBA_100_202216_6_Oct21',
    'testlog/14scheme_testSBA_100_202217_7_Oct21',
    'testlog/14scheme_testSBA_100_202218_8_Oct21',
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
num_cells = 100

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
    
    def report_by_elasped_time(results, num_cat, only_report=None, hint="", level_num=10):
        # results are only about read, assuming all read for same address are consecutive
        # num_cat is the number of timestamps
        categorized = {}
        for i in range(num_cat):
            categorized[i] = []
        # print(f"{len(results)} / ({num_cat} * {level_num})")
        # tested_cells = len(results) / (num_cat * level_num)
        # print("num_cells=", num_cells, ", tested_cells=", tested_cells)
        # assert num_cells - tested_cells <= 1, f"{num_cells}, {tested_cells}"
        for i in range(0, len(results)):
            categorized[i%num_cat].append(results[i])
        if only_report is not None:
            _, res = Result.compute_prob(categorized[only_report], hint)
            return res
        for i in range(num_cat):
            Result.compute_prob(categorized[i], "timebin_" + str(i))


def data_init(logfile):
    global all_lows
    with open(logfile, "r") as fin:
        lines = fin.readlines()
        should_skip = False
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _ = line
            low, high, addr, time, final = float(low), float(high), int(addr), float(time), float(final)
            success = Result.check_range(low, high, final)
            if action == "Init":
                should_skip = False
            if action == "Write" and success == False and skip_write_fail == True:
                should_skip = True
                continue
            if should_skip == True:
                assert action == "Read"
                continue
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


def gen_matrix(read_list, isOur, all_level):
    lows = sorted(list(set(map(lambda x: x.low, read_list))))
    highs = sorted(list(set(map(lambda x: x.high, read_list))))
    assert len(lows) == len(highs)
    num_levels = len(lows)
    assert all_level == num_levels
    P = np.zeros((num_levels, num_levels))
    for j in range(num_levels): # target value is j level
        input_j = list(filter(lambda x: x.low == lows[j], read_list))
        input_j_ = list(filter(lambda x: x.high == highs[j], read_list))
        assert len(input_j) == len(input_j_)
        for i in range(num_levels): # final written value is i level
            output_i = list(filter(lambda x: lows[i] <= x.final and x.final < highs[i], input_j))
            prob = len(output_i) / len(input_j)
            P[i][j] = prob
    # print(P.tolist())
    # e = max(1 - P[k][k])
    max_error = 0.0
    for k in range(num_levels):
        max_error = max(1 - P[k][k], max_error)
    print("max_error", num_levels, max_error)
    to_write = []
    for i in range(num_levels):
        to_write.append(",".join(map(str, P[i])) + "\n")
    with open("capacity/" + ("ours" if isOur else "SBA") + str(all_level), "w") as f:
        f.writelines(to_write)
    # print(f"Success Rate for {num_levels}: ",
    #     np.mean(list(map(lambda x: P[x][x], [k for k in range(0, num_levels)]))))
    return max_error


if __name__ == "__main__":
    dead_cell_init()
    map_report = {}
    map_report_maxerr = {}
    our = False
    if our:
        for i in range(len(logfiles)):
            clear()
            data_init(logfiles[i])
            # [0, 0.01, 0.1, 0.2, 0.5, 1.0, 2, 5, 10]
            # only_report=4: 1s, 7: 10s
            # Result.report_by_elasped_time(Result.write, 1, only_report=None, hint="write")
            res = Result.report_by_elasped_time(Result.read, len(timestamp)-1, only_report=4, hint=str(i+4), level_num=i+4)
            map_report[i+4] = res
            err = gen_matrix(Result.read, our, i+4)
            map_report_maxerr[i+4] = err
    else:
        for i in range(len(logfiles2)):
            clear()
            data_init(logfiles2[i])
            # [0, 0.01, 0.1, 0.2, 0.5, 1.0, 2, 5, 10]
            # Result.report_by_elasped_time(Result.write, 1, only_report=None, hint="write")
            res = Result.report_by_elasped_time(Result.read, len(timestamp)-1, only_report=4, hint=str(i+4), level_num=i+4)
            map_report[i+4] = res
            err = gen_matrix(Result.read, our, i+4)
            map_report_maxerr[i+4] = err
    print("ours" if our else "SBA")
    print("Average error:")
    pprint.pprint(map_report)
    print("Worst error:")
    pprint.pprint(map_report_maxerr)
