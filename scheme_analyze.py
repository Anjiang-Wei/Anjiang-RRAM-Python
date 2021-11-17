logfile = "30_0_1" # cells_manualseed_experimentid_attempts

init = {}
write = {}
read = {}
all_lows = []

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
    
    def report_by_elasped_time(results, num_cat):
        # results are only about read, assuming all read for same address are consecutive
        # num_cat is the number of timestamps
        categorized = {}
        for i in range(num_cat):
            categorized[i] = []
        for i in range(0, len(results)):
            categorized[i%num_cat].append(results[i])
        for i in range(num_cat):
            Result.compute_prob(categorized[i], "timebin_" + str(i))


def data_init():
    global all_lows
    with open("testlog/13scheme_test_" + logfile, "r") as fin:
        lines = fin.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _ = line
            low, high, addr, time, final = float(low), float(high), int(addr), float(time), float(final)
            success = Result.check_range(low, high, final)
            r = Result(action, addr, low, high, final, success, time)            
            if action == "Init":
                Result.init.append(r)
            elif action == "Write":
                Result.write.append(r)
                if low not in all_lows:
                    all_lows.append(low)
            else:
                assert action == "Read"
                Result.read.append(r)
                if low not in all_lows:
                    all_lows.append(low)
            Result.all.append(r)
    all_lows = sorted(set(all_lows))
    print(all_lows)


if __name__ == "__main__":
    data_init()
    init_bad = Result.compute_prob(Result.init, "init")
    write_bad = Result.compute_prob(Result.write, "write")
    read_bad = Result.compute_prob(Result.read, "read")
    all_bad = Result.compute_prob(Result.all, "all")
    Result.analyze_level_prob(Result.all)
    Result.report_by_elasped_time(Result.read, 3)
    # print(sorted(set(init_bad)))
    # print(sorted(set(write_bad)))
    # print(sorted(set(read_bad)))
    # print(sorted(set(all_bad)))
