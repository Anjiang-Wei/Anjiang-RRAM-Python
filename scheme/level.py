import matplotlib.pyplot as plt
import seaborn as sns
import json

class Level(object):
    '''
    Level is represented as Read Range [r1, r2] and Write Range [w1, w2]
    [w1, w2] should be within the range of [r1, r2] 
    '''
    def __init__(self, r1, r2, w1, w2, sigma=0, prob=0):
        assert r1 < w1 and w1 < w2 and w2 < r2
        self.r1 = r1
        self.r2 = r2
        self.w1 = w1
        self.w2 = w2
        self.sigma = sigma
        self.prob = prob
    
    def __str__(self):
        return "Read:[%d,%d], Write:[%d,%d]" % (self.r1, self.r2, self.w1, self.w2)
    
    @staticmethod
    def draw(levels):
        for i in range(len(levels)):
            color = sns.color_palette(n_colors=len(levels))[i]
            plt.axvline(levels[i].r1, color=color, linestyle=':', linewidth=1)
            plt.axvline(levels[i].r2, color=color, linestyle=':', linewidth=1)
            plt.axvline(levels[i].w1, color=color, linestyle='-', linewidth=1)
            plt.axvline(levels[i].w2, color=color, linestyle='-', linewidth=1)
        plt.show()

    @staticmethod
    def dict2level(d):
        return Level(d['r1'], d['r2'], d['w1'], d['w2'], d['sigma'], d['prob'])

    @staticmethod
    def export_to_file(levels, fout="B_mapping.json"):
        jsonstr = json.dumps(levels, default=lambda obj: obj.__dict__)
        with open(fout, "w") as f:
            f.write(jsonstr)
    
    @staticmethod
    def load_from_file(fin="B_mapping.json", draw=False):
        with open(fin, "r") as f:
            jsonstr = f.readlines()[0]
            levels = json.loads(jsonstr, object_hook=Level.dict2level)
            if draw:
                Level.draw(levels)
            print(len(levels))
            return levels

    @staticmethod
    def overlap(A, B) -> bool:
        if B.r2 >= A.r1 and A.r2 >= B.r1:
            return True
        else:
            return False
    
    @staticmethod
    def sort_by_mean(all_levels):
        return sorted(all_levels, key=lambda x: (x.w1 + x.w2) / 2)
    
    @staticmethod
    def longest_non_overlap(all_levels):
        '''
        This is inaccurate greedy algorithm
        Assumption:
            interval of read ranges increases with the resistance
        '''
        res = []
        sorted_levels = Level.sort_by_mean(all_levels)
        res.append(sorted_levels[0])
        cur = sorted_levels[0]
        for i in range(1, len(sorted_levels)):
            nxt = sorted_levels[i]
            if Level.overlap(cur, nxt) == False:
                res.append(nxt)
                cur = nxt
        return res
    
if __name__ == "__main__":
    Level.load_from_file()
