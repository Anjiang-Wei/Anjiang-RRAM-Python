import sys

def reverse_inter(infile, outfile):
    to_write = ["512,512\n"]
    with open(infile, "r") as fin:
        lines = fin.readlines()
        # print(len(lines))
        assert len(lines) == 512 * 512 * 3
        for i in range(0, 512 * 512 * 3, 512 * 3):
            new_line = []
            for elem in lines[i: i + 512 * 3]:
                new_line.append(elem.strip())
            to_write.append(",".join(new_line) + "\n")

    line_last = "{'bitdepth': 8, 'interlace': 0, 'background': (255, 255, 255), 'planes': 3, 'greyscale': False, 'alpha': False, 'size': (512, 512)}"
    to_write.append(line_last)

    # print(to_write)
    with open(outfile, "w") as fout:
        fout.writelines(to_write)

if __name__ == "__main__":
    filename = sys.argv[1]
    reverse_inter(filename, filename)
