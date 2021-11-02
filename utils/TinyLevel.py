import matplotlib.pyplot as plt
import seaborn as sns

class Tiny_Level(object):
    differentiate_attempt = True
    all_levels = []
    def __init__(self, low, high, success, max_attempts, final):
        assert low < high
        self.low = low
        self.high = high
        self.width = high - low
        self.center = (low + high) / 2
        self.success = success
        self.max_attempts = max_attempts
        # -1: final lower than target, 1: final higher than target
        self.summary = {0: 0, -1: 0, 1: 0}
        self.summary[success] = 1
        self.finals = [final]
        # computed after all_levels is stable
        self.idx = 0
        self.total_times = 0
        self.success_rate = 0
    
    def __eq__(self, o):
        if Tiny_Level.differentiate_attempt:
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
    def data_stable():
        '''
        After all_levels are stable, call this func to ensure correct initialization!
        '''
        Tiny_Level.compute_idx()
        Tiny_Level.compute_total_succ()
    
    @staticmethod
    def printall():
        Tiny_Level.compute_idx()
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
    def center2idx(center, levels=all_levels):
        '''
        Given a center value, return the index (redundance removed) to it w.r.t all the levels specified
        '''
        all_centers = list(map(lambda x: x.center, levels))
        sorted_centers = sorted(list(set(all_centers)))
        return sorted_centers.index(center)
    
    @staticmethod
    def compute_idx():
        '''
        After all_levels are stable, this function should be called
        '''
        for i in range(len(Tiny_Level.all_levels)):
            level = Tiny_Level.all_levels[i]
            level.idx = Tiny_Level.center2idx(level.center)
    
    @staticmethod
    def compute_total_succ():
        for i in range(len(Tiny_Level.all_levels)):
            level = Tiny_Level.all_levels[i]
            level.total_times = sum(level.summary.values())
            level.success_rate = level.summary[0] / level.total_times
    
    @staticmethod
    def filter_levels(lambda_func, all_levels=all_levels):
        '''
        Given a lambda function, return the filtered levels from all_levels
        '''
        satisfied_levels = list(filter(lambda_func, all_levels))
        return satisfied_levels
    
    def filter_properties(lambda_func):
        '''
        Given a lambda function, return the set of values of a certain property
        '''
        property_vals = set(map(lambda_func, Tiny_Level.all_levels))
        return property_vals
    
    def level_sort_by_width():
        vals = Tiny_Level.filter_properties(lambda x: x.width)
        res = []
        for val in vals:
            res += Tiny_Level.filter_levels(lambda x: x.width == val)
        return res
    
    def level_sort_by_attempt():
        vals = Tiny_Level.filter_properties(lambda x: x.max_attempts)
        res = []
        for val in vals:
            res += Tiny_Level.filter_levels(lambda x: x.max_attempts == val)
        return res
    
    @staticmethod
    def draw_levels(levels, lambda_func=lambda x: x, hint=""):
        all_levels = list(filter(lambda_func, levels))
        for i in range(len(all_levels)):
            color = sns.color_palette(n_colors=len(all_levels))[i]
            plt.axvline(all_levels[i].low, color=color, linestyle=':', linewidth=1)
            plt.axvline(all_levels[i].high, color=color, linestyle=':', linewidth=1)
            sns.distplot(all_levels[i].finals, kde=True, label=f'{hint} {i}', axlabel=True)
        plt.legend()
        plt.show()
    
    @staticmethod
    def draw_level(level):
        color= sns.color_palette(n_colors=1)[0]
        plt.axvline(level.low, color=color, linestyle=':', linewidth=1)
        plt.axvline(level.high, color=color, linestyle=':', linewidth=1)
        success_total, total_times = level.summary[0], sum(level.summary.values())
        label = f"{level.idx} IDX, {level.width} WID, {level.max_attempts} ATT, {success_total/total_times}"
        sns.distplot(level.finals, kde=True, label=label, axlabel=False)
        plt.legend()
        plt.show()
