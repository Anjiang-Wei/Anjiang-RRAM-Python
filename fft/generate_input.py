lines = []
for i in range(0, 2048):
    lines.append(str(i)+"\n")
with open("input0", "w") as fout:
    fout.writelines(lines)
