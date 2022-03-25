def relative_diff(golden, mutated):
    assert len(golden) == len(mutated)
    all_error = 0
    for i in range(len(golden)):
        err = golden[i] - mutated[i]
        rel_err = abs(rel_err / golden[i])
        all_error += rel_err
    all_error = all_error / len(golden)
    assert all_error >= 0 and all_error <= 1



