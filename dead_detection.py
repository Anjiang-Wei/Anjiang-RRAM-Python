from nirram import NIRRAM
import test_scheme
import time

chip_name = "C9"

def detect(cells, fout, nisys, low=10*1e3, high=11*1e3, already_dead=[]):
    for addr in cells:
        if addr in already_dead:
            continue
        assert test_scheme.start_addr <= addr and addr < test_scheme.end_addr
        nisys.set_addr(addr)
        target = nisys.target(low, high)
        if low <= target[0] and target[0] <= high:
            continue
        else:
            print(f"{addr},{low},{high},{target[0]},False\n")
            fout.write(f"{addr},{low},{high},{target[0]},False\n")

def detect_after_test(ncells, fout, nisys):
    test_scheme.dead_init()
    cells = test_scheme.random_pick(ncells)
    detect(cells, fout, nisys)
    print(cells)

if __name__ == "__main__":
    start = time.time()
    fout = open("log/9dead_test.csv", "w")
    nisys = NIRRAM(chip_name)
    cells = [i for i in range(0, 65536)]
    detect(cells, fout, nisys)
    nisys.close()
    fout.close()
    end = time.time()
    duration = end - start
    print("elapsed time:", duration)
