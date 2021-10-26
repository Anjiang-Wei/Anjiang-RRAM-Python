import matplotlib.pyplot as plt
import seaborn as sns

class Tiny_Level(object):
    all_levels = []
    def __init__(self, low, high, success, max_attempts, final):
        assert low < high
        self.low = low
        self.high = high
        self.width = high - low
        self.center = (low + high) / 2
        self.success = success
        self.summary = {0: 0, -1: 0, 1: 0}
        self.summary[success] = 1
        self.max_attempts = max_attempts
        self.finals = [final]
    
    def __eq__(self, o, differentiate_attempt=False):
        if differentiate_attempt:
            return self.low == o.low and self.high == o.high and self.max_attempts == o.max_attempts
        else:
            return self.low == o.low and self.high == o.high
    
    def __str__(self):
        success_total = self.summary[0]
        lower_total = self.summary[-1]
        higher_total = self.summary[1]
        total_times = sum(self.summary.values())
        assert success_total + lower_total + higher_total == total_times
        return f"Width:{self.width}, Center:{self.center}, \
            Attempts:{self.max_attempts},\
            Success:{success_total}/{total_times} = {success_total/total_times}, \
            Low:{lower_total}, High:{higher_total}"
    
    @staticmethod
    def printall():
        for level in Tiny_Level.all_levels:
            print(level)
    
    @staticmethod
    def clear():
        Tiny_Level.all_levels = []

    @staticmethod
    def add(o):
        '''
        Update the single result to all levels
        Initialize a new level when needed
        '''
        if o not in Tiny_Level.all_levels:
            Tiny_Level.all_levels.append(o)
        else:
            idx = Tiny_Level.all_levels.index(o)
            Tiny_Level.all_levels[idx].summary[o.success] += 1
            Tiny_Level.all_levels[idx].finals += o.finals

    @staticmethod
    def low2idx(low, levels=all_levels):
        '''
        Given a low value, return the index (redundance removed) to it w.r.t all the levels specified
        '''
        all_lows = list(map(lambda x: x.low), levels)
        sorted_lows = sorted(list(set(all_lows)))
        return sorted_lows.index(low)
    
    @staticmethod
    def filter_levels(lambda_func):
        '''
        Given a lambda function, return the filtered levels from all_levels
        '''
        satisfied_levels = list(filter(lambda_func, Tiny_Level.all_levels))
        return satisfied_levels
    
    @staticmethod
    def draw_levels(levels, lambda_func=lambda x: x):
        all_levels = list(filter(lambda_func, levels))
        for i in range(len(all_levels)):
            color = sns.color_palette(n_colors=len(all_levels))[i]
            plt.axvline(all_levels[i].low, color=color, linestyle=':', linewidth=1)
            plt.axvline(all_levels[i].high, color=color, linestyle=':', linewidth=1)
            sns.distplot(all_levels[i].finals, kde=True, label='Range %d' % i, axlabel=True)
        plt.show()
