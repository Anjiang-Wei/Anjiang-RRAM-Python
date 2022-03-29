import subprocess


'''
Comparing "2_output" and "2_output0"
  Mean error = 4.4059e+08
  RMS error = 1.59511e+11
  Peak SNR = 77.0505
  Max error  = 5.77491e+13 @ (4, 256, Y)
  2 pixels (0.000763%) over 1e-06
  2 pixels (0.000763%) over 1e-06
FAILURE
-------------
Comparing "2_output" and "2_output0"
PASS
'''

def judge(text):
    if "PASS" in text:
        return True
    assert "RMS error" in text
    lines = text.split('\n')
    for line in lines:
        if "RMS error = " in line:
            _, num = line.split("=")
            num = float(num)
            # print(num)
            if num <= 0.1:
                return True
            else:
                return False

def diffonce(f1, f2):
    # Reason for not using compare: it does not work on the generated jpeg file
    # So we have to swtich to idiff
    # https://openimageio.readthedocs.io/en/stable/idiff.html
    # image diff 10%
    ret = subprocess.run(["idiff", f1, f2],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = ret.stdout.decode()
    if judge(out):
        return True
    else:
        return False

def diffpair(f1, f2):
    # to mitigate the randomness of the tool idiff for image difference computation
    for i in range(10):
        if diffonce(f1, f2):
            return True
    return False

def diff(f1_list, f2_list):
    for i in range(len(f1_list)):
        if diffpair(f1_list[i], f2_list[i]) == False:
           return False
    return True

if __name__ == "__main__":
    print(diff(["1_output", "2_output", "3_output"], ["1_output0", "2_output0", "3_output0"]))
    print(diff(["1_output", "2_output", "3_output"], ["1_output0", "2_output0", "2_output0"]))
    print(diff(["1_output", "2_output", "3_output"], ["1_output0", "3_output0", "3_output0"]))
