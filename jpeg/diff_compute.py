import subprocess

def diffonce(f1, f2):
    # Reason for not using compare: it does not work on the generated jpeg file
    # So we have to swtich to idiff
    # Reason for not using RMSE: it has too much randomness
    # https://openimageio.readthedocs.io/en/stable/idiff.html
    # image diff 10%
    ret = subprocess.run(["idiff", "-fail", "0.01", "-failpercent", "10", f1, f2],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if ret.returncode == 0:
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
