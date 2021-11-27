from utils.TinyLevel import Tiny_Level


logfile = "30_78_merge"

init = {}
write = {}
read = {}

dead_cells = []

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

def data_init(fname=""):
    if fname == "":
        fname = "testlog/collect_data_" + logfile
    with open(fname, "r") as fin:
        lines = fin.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip().split()
            action, low, high, addr, time, final, _, max_attempts = line
            low, high, addr, time, final, max_attempts = float(low), float(high), int(addr), float(time), float(final), int(max_attempts)
            if addr not in dead_cells:
                r = Result(action, addr, low, high, final, time, max_attempts)
                Result.add2all(r)
            # else:
            #     print(f"Dead cell {addr} skipped")
        Result.toTinyLevel(Result.all)
        Tiny_Level.data_stable()


def report_all():
    Tiny_Level.printall()
    # levels = Tiny_Level.level_sort_by_width()
    # for l in levels[::-1]:
    #     Tiny_Level.draw_level(l)
    # levels = Tiny_Level.level_sort_by_attempt()
    # for l in levels[::-1]:
    #     Tiny_Level.draw_level(l)

if __name__ == "__main__":
    dead_cell_init()
    data_init()
    report_all()
