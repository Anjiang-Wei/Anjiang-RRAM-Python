import torch

all_float_dump = []
all_float_in = []

def dump_list(vals):
    for v in vals:
        if type(v) == float:
            all_float_dump.append(v)
        else:
            print(type(v))
            print("-------------------")
            raise NotImplementedError

def get_list(num_vals):
    global all_float_in
    res = all_float_in[:num_vals]
    all_float_in = all_float_in[num_vals:]
    return res

def dump_tensor(tensor):
    flatten = torch.flatten(tensor)
    dump_list(flatten.tolist())

def get_tensor(tensor):
    size = list(tensor.size())
    num_elems = torch.numel(tensor)
    mutated_list = get_list(num_elems)
    new_tensor = torch.tensor(mutated_list, dtype=tensor.dtype)
    new_tensor = new_tensor.view(*size)
    return new_tensor

def should_skip(name):
    skipped = ["num_batches_tracked"]
    for s in skipped:
        if s in name:
            return True
    return False

def dump_net_from_path(model_path, float_file):
    '''
    Read from model_path, dump to float_file
    '''
    state_dict = torch.load(model_path)
    print(len(state_dict))
    cnt = 0
    for item in state_dict:
        cnt += 1
        print(cnt, end=",", flush=True)
        if not should_skip(item):
            v = state_dict[item]
            dump_tensor(v)
    with open(float_file, "w") as fout:
        fout.writelines([str(a)+"\n" for a in all_float_dump])
    

def load_net_from_float(float_file2, model_path2):
    '''
    Read from float_file2, save state_dict to model_path2
    '''
    with open(float_file2, "r") as fin:
        lines = fin.readlines()
        for l in lines:
            all_float_in.append(float(l))
    state_dict = torch.load(model_path2)
    cnt = 0
    for item in state_dict:
        cnt += 1
        # print(cnt, end=",", flush=True)
        if not should_skip(item):
            v = state_dict[item]
            v2 = get_tensor(v)
            state_dict[item] = v2
    torch.save(state_dict, model_path2)

if __name__ == "__main__":
    dump_net_from_path("mnist_torch.pt", "floatfile")
    load_net_from_float("floatfile", "mnist_torch.pt0")
