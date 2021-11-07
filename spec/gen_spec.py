filename = "spec0.txt"
dtype = "float"
dlength = 32
lines = []
config = {
    "0.001": [0],
    "0.1": [i for i in range(1, 9)],
    "0.2": [i for i in range(9, 32)]
}
with open(filename, "w") as fout:
    lines.append(f'{dtype};{dlength}\n')
    for k in config.keys():
        string = ",".join(map(str, config[k]))
        lines.append(f'{k};{len(config[k])};{string}\n')
    fout.writelines(lines)
