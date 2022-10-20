import matplotlib.pyplot as plt
import seaborn as sns
import json
import sys

class Level(object):
    '''
    Level is represented as Read Range [r1, r2] and Write Range [w1, w2]
    [w1, w2] should be within the range of [r1, r2]
    '''
    def __init__(self, r1, r2, w1, w2, sigma=0, prob=0, assertion=True):
        if assertion:
            assert ((w1 == 0 and r1 == 0) or r1 < w1) and w1 < w2 and w2 < r2, f'{r1}, {w1}, {w2}, {r2}'
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
            if i != len(levels) - 1:
                plt.axvline(levels[i].r2, color=color, linestyle=':', linewidth=1)
            plt.axvline(levels[i].w1, color=color, linestyle='-', linewidth=1)
            plt.axvline(levels[i].w2, color=color, linestyle='-', linewidth=1)
        plt.show()
        plt.savefig(f"{len(levels)}level.png")

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
    def refine_read_ranges(levels):
        '''
        This makes sure that there won't be holes between levels
        '''
        levels[0].r1 = 0
        levels[-1].r2 = 10000000
        for i in range(0, len(levels)-1):
            avg = (levels[i].r2 + levels[i+1].r1) / 2
            levels[i].r2 = avg
            levels[i+1].r1 = avg
        return levels

    @staticmethod
    def merge_adjacent(levels):
        '''
        This merges the adjacent levels
        '''
        assert len(levels) % 2 == 0
        result_levels = []
        for i in range(0, len(levels), 2):
            new_r1, new_r2 = levels[i].r1, levels[i+1].r2
            new_w1 = (levels[i].w1 + levels[i+1].w1) / 2
            new_w2 = (levels[i].w2 + levels[i+1].w2) / 2
            new_level = Level(new_r1, new_r2, new_w1, new_w2)
            result_levels.append(new_level)
        assert(len(result_levels) == len(levels) / 2)
        return result_levels

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
    def sort_by_read_high(all_levels):
        return sorted(all_levels, key=lambda x: x.r2)

    @staticmethod
    def longest_non_overlap_old(all_levels):
        '''
        Deprecated!
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

    @staticmethod
    def longest_non_overlap(all_levels):
        '''
        This is a greedy algorithm
        '''
        res = []
        sorted_levels = Level.sort_by_read_high(all_levels)
        res.append(sorted_levels[0])
        cur = sorted_levels[0]
        for i in range(1, len(sorted_levels)):
            nxt = sorted_levels[i]
            if nxt.r1 >= cur.r2:
                res.append(nxt)
                cur = nxt
        return res

if __name__ == "__main__":
    levels = Level.load_from_file(fin=sys.argv[1], draw=True)
