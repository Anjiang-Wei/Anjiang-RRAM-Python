deads = []
to_write = []
with open("13new_dead.csv", "r") as fin:
    lines = fin.readlines()
    for line in lines:
        addr = line.strip().split(",")[0]
        if addr not in deads:
            deads.append(addr)
            to_write.append(line)

with open("13new_dead2.csv", "w") as fout:
    fout.writelines(to_write)
