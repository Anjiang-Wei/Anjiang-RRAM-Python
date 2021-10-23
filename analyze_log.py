logfile = "10_1"

init = {}
write = {}
read = {}

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
                print(v.addr, v.low, v.high, v.final)
                fail_addr.append(v.addr)
        print(f"Failure rate for {hint}: {fail} / {total} = {fail/total}")
        return fail_addr

def data_init():
    with open("testlog/scheme_test_" + logfile, "r") as fin:
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
            else:
                assert action == "Read"
                Result.read.append(r)
            Result.all.append(r)


if __name__ == "__main__":
    data_init()
    # init_bad = Result.compute_prob(Result.init, "init")
    # write_bad = Result.compute_prob(Result.write, "write")
    # Run 10 cell experiment 3 times, non-determinism? Increase attempts=25, 50, 50
    # TODO: Ping Akash, x cells got stuck in 6xxx, is it fine? Increase the lower bound?
    # dead cell list is ready 
    read_bad = Result.compute_prob(Result.write, "read")
    # all_bad = Result.compute_prob(Result.write, "all")
    # print(sorted(set(init_bad)))
    # print(sorted(set(write_bad)))
    # print(sorted(set(read_bad)))
    # print(sorted(set(all_bad)))
    '''
    0. message Akash newly dead cell, dead cell list [maybe increase lower resistance?]
    1. dead cell check
    2. 10 cell experiment 3 (4) times, live cells the same, replace dead cells
    Analysis: level error rate analysis for write / read, correlation between write / read
    May variational write width
    '''
