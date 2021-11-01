from utils.TinyLevel import Tiny_Level


logfile = "30_7_0"

init = {}
write = {}
read = {}

class Result(object):
    all = []
    def __init__(self, action, addr, low, high, final, time, max_attempts):
        self.action = action
        self.addr = addr
        self.low = low
        self.high = high
        self.final = final
        self.success = Result.check_range(low, high, final)
        self.time = time
        self.max_attempts = max_attempts
        self.center = (low + high) / 2
        self.width = high - low

    @staticmethod
    def add2all(o):
        Result.all.append(o)
    
    @staticmethod
    def check_range(low, high, value):
        '''
        Return:
        -1: value too low
        0: correct
        1: value too high
        '''
        assert low < high
        if value < low:
            return -1
        elif value > high:
            return 1
        else:
            return 0
    
    @staticmethod
    def filter_result(lambda_func, all_results=all):
        return list(filter(lambda_func, all_results))
    
    @staticmethod
    def toTinyLevel(results):
        for o in results:
            Tiny_Level.add(Tiny_Level(o.low, o.high, o.success, o.max_attempts, o.final))

def data_init():
    with open("testlog/collect_data_" + logfile, "r") as fin:
        lines = fin.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _, max_attempts = line
            low, high, addr, time, final, max_attempts = float(low), float(high), int(addr), float(time), float(final), int(max_attempts)
            r = Result(action, addr, low, high, final, time, max_attempts)
            Result.add2all(r)

def report_all():
    Result.toTinyLevel(Result.all)
    Tiny_Level.printall()
    # Tiny_Level.draw_levels(Tiny_Level.all_levels, lambda x: x.low < 10000)

if __name__ == "__main__":
    data_init()
    report_all()
