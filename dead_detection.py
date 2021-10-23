from nirram import NIRRAM
import test_scheme

chip_name = "C10"

def detect(cells, low=10*1e3, high=11*1e3):
    for addr in cells:
        assert test_scheme.start_addr <= addr and addr < test_scheme.end_addr
        nisys.set_addr(addr)
        target = nisys.target(low, high)
        if low <= target[0] and target[0] <= high:
            continue
        else:
            fout.write(f"{addr},{low},{high},{target[0]},False\n")

def detect_after_test(ncells):
    test_scheme.dead_init()
    cells = test_scheme.random_pick(ncells)
    detect(cells)
    print(cells)

if __name__ == "__main__":
    fout = open("log/new_dead.csv", "a")
    nisys = NIRRAM(chip_name)
    detect_after_test(10)
    nisys.close()
    fout.close()
