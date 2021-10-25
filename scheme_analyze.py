logfile = "10_2_1_25"

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
        return fail_addr
    
    def analyze_level_prob(results):
        for low in all_lows:
            filtered_res_write = list(filter(lambda x: x.low == low and x.action == "Write", results))
            Result.compute_prob(filtered_res_write, str(low) + "+write")
            filtered_res_read = list(filter(lambda x: x.low == low and x.action == "Read", results))
            Result.compute_prob(filtered_res_read, str(low) + "+read")

def data_init():
    global all_lows
    with open("testlog/scheme_test_" + logfile, "r") as fin:
        lines = fin.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _ = line
            low, high, addr, time, final = float(low), float(high), int(addr), float(time), float(final)
            if low not in all_lows:
                all_lows.append(low)
            success = Result.check_range(low, high, final)
            r = Result(action, addr, low, high, final, success, time)            
            if action == "Init":
                Result.init.append(r)
            elif action == "Write":
                Result.write.append(r)
            else:
                assert action == "Read"
                Result.read.append(r)
            Result.all.append(r)
    all_lows = sorted(set(all_lows))


if __name__ == "__main__":
    data_init()
    init_bad = Result.compute_prob(Result.init, "init")
    write_bad = Result.compute_prob(Result.write, "write")
    read_bad = Result.compute_prob(Result.read, "read")
    all_bad = Result.compute_prob(Result.all, "all")
    Result.analyze_level_prob(Result.all)
    # print(sorted(set(init_bad)))
    # print(sorted(set(write_bad)))
    # print(sorted(set(read_bad)))
    # print(sorted(set(all_bad)))
