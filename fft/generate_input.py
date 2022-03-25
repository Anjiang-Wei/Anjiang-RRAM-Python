import sys

num = int(sys.argv[1])

lines = []
for i in range(0, 4096):
    lines.append(str(i)+"\n")
with open("input0", "w") as fout:
    fout.writelines(lines)
