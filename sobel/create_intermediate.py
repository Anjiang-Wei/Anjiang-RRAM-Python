import sys
ifile = sys.argv[1]
ofile = ifile.replace("original", "intermediate")
out = []
with open(ifile, "r") as fin:
    lines = fin.readlines()
    for line in lines[1:-1]:
        for eint in line.strip().split(","):
            out.append(eint + " ")
        out.append("\n")

with open(ofile, "w") as fout:
    fout.writelines(out)
