import bitstring
while True:
    a = float(input())
    f1 = bitstring.BitArray(float=a, length=32)
    for elem in f1.bin:
        print(elem+",", end="")
    print()
