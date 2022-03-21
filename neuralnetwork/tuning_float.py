# https://github.com/pytorch/examples/blob/master/mnist/main.py

from __future__ import print_function
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
# from fault import mutate_tensor
import dump_load
import subprocess
import pprint

original_model = "mnist_torch.pt"
original_float = "float"
mutate_model = "mnist_torch.pt0"
mutate_float = "float0"


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if args.dry_run:
                break


def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)), flush=True)
    return correct / len(test_loader.dataset)


def main():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=1, metavar='N',
                        help='number of epochs to train (default: 1)')
    parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
                        help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='quickly check a single pass')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_false', default=True,
                        help='For Saving the current Model')
    args = parser.parse_args()
    use_cuda = not args.no_cuda and torch.cuda.is_available()

    torch.manual_seed(args.seed)

    device = torch.device("cuda" if use_cuda else "cpu")

    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])
    dataset1 = datasets.MNIST('./data', train=True, download=True,
                       transform=transform)
    dataset2 = datasets.MNIST('./data', train=False, download=True,
                       transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset1,**train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    for epoch in range(1, args.epochs + 1):
        train(args, model, device, train_loader, optimizer, epoch)
        test(model, device, test_loader)
        scheduler.step()

    if args.save_model:
        torch.save(model.state_dict(), original_model)
        torch.save(model.state_dict(), mutate_model)

# def fault_inject():
#     state_dict = torch.load(mutate_model)
#     for item in state_dict:
#         v = state_dict[item]
#         v_ = mutate_tensor(v)
#         state_dict[item] = v_
#     torch.save(state_dict, mutate_model)


def test_net():
    device = torch.device("cpu")
    model = Net().to(device)
    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])
    dataset2 = datasets.MNIST('./data', train=False, download=True,
                       transform=transform)
    test_loader = torch.utils.data.DataLoader(dataset2, batch_size=1000)
    # print("===========Original============")
    # model.load_state_dict(torch.load(original_model))
    # test(model, device, test_loader)
    # fault_inject()
    # print("Fault Injected", flush=True)
    model.load_state_dict(torch.load(mutate_model))
    return test(model, device, test_loader)

def dump_float():
    dump_load.dump_net_from_path(original_model, original_float)
    # print("Dump finished", flush=True)

def load_float():
    dump_load.load_net_from_float(mutate_float, mutate_model)
    print("Load finished", flush=True)

def drop_bits(R, E, spec_ber, raw_ber, start_M, minimum_accuracy):
    # R, E, M = 10, 1, 4
    # m_p, m_a = 4, 0
    # spec_ber, raw_ber = 1e-13, 0.1
    M = start_M
    m_p, m_a = M, 0
    print(f"R={R}, E={E}, M={M}, m_p_start={m_p}, m_a={m_a}, spec_ber={spec_ber}, raw_ber={raw_ber}", flush=True)
    while m_p >= 0:
        print(f"Current configuration: E={E}, M={M}, m_p={m_p}, m_a={m_a}", flush=True)
        subprocess.run(["./a.out", original_float, mutate_float, str(R), str(E), str(M), 
                str(m_p), str(m_a), str(spec_ber), str(raw_ber)])
        load_float()
        acc = test_net()
        if acc >= minimum_accuracy:
            start_M = M
        else:
            return start_M
        M -= 1
        m_p -= 1
        print("------", flush=True)

def drop_precise(R, E, spec_ber, raw_ber, start_M, minimum_accuracy):
    # R, M = 10, 3
    # m_p, m_a = 3, 0
    # spec_ber, raw_ber = 1e-13, 0.1
    M = start_M
    m_p, m_a = M, 0
    print(f"R={R}, E={E}, M={M}, m_p_start={m_p}, m_a={m_a}, spec_ber={spec_ber}, raw_ber={raw_ber}", flush=True)
    while m_p >= 0:
        print(f"Current configuration: E={E}, M={M}, m_p={m_p}, m_a={m_a}", flush=True)
        subprocess.run(["./a.out", original_float, mutate_float, str(R), str(E), str(M), 
                str(m_p), str(m_a), str(spec_ber), str(raw_ber)])
        load_float()
        acc = test_net()
        if acc >= minimum_accuracy:
            start_M = m_p
        else:
            return start_M
        m_p -= 1
        m_a += 1
        print("--------", flush=True)
    return 0 # no precise mantissa

# q: (rber, e)
algo_res = {4: (0.003750000000000031, 0),
 5: (0.006249999999999978, 0),
 6: (0.012499999999999956, 0),
 7: (0.02749999999999997, 0),
 8: (0.043749999999999956, 0),
 9: (0.043749999999999956, 0),
 10: (0.09999999999999998, 0),
 11: (0.15749999999999997, 0),
 12: (0.21250000000000002, 0),
 13: (0.16749999999999998, 0),
 14: (0.15874999999999995, 0),
 15: (0.23375, 0),
 16: (0.25125, 0)}

algo_res2 = {4: (0.125, 0),
 5: (0.16500000000000004, 0),
 6: (0.13249999999999995, 0),
 7: (0.14, 0),
 8: (0.2234848484848485, 0),
 9: (0.25, 0),
 10: (0.16625, 0),
 11: (0.21375, 0),
 12: (0.24624999999999997, 0),
 13: (0.25, 0),
 14: (0.26875000000000004, 0),
 15: (0.38749999999999996, 0),
 16: (0.33875, 0)}

def normal(ours):
    '''
    algo_res or algo_res2
    '''
    to_test = algo_res if ours else algo_res2
    res = {}
    for q, rber_e in to_test.items():
        rber, e = rber_e
        print(f"-----------drop bits for R={q}, raw_ber={rber}, E={e}------", flush=True)
        min_M = drop_bits(R=q, E=e, spec_ber=1e-13, raw_ber=rber, start_M=4, minimum_accuracy=0.98)
        print(f"-----------drop precise bits for R={q}, raw_ber={rber}, E={e}, min_M={min_M}------", flush=True)
        min_m_p = drop_precise(R=q, E=e, spec_ber=1e-13, raw_ber=rber, start_M=min_M, minimum_accuracy=0.98)
        print(f"Config found: R={q}, raw_ber={rber}, E={e}, min_M={min_M}, min_m_p={min_m_p}", flush=True)
        res[q] = (min_m_p, min_M-min_m_p)
    print("q --> (m_p, m_a)")
    pprint.pprint(res)

def rdrop():
    m_p, m_a = 1, 0
    R, E, M = 9, 0, 1
    spec_ber, raw_ber = 1e-13, algo_res[R][0]
    print(f"R={R}, E={E}, M={M}, m_p={m_p}, m_a={m_a}, spec_ber={spec_ber}, raw_ber={raw_ber}", flush=True)
    print(f"Current configuration: E={E}, M={M}, m_p={m_p}, m_a={m_a}", flush=True)
    subprocess.run(["./a.out", original_float, mutate_float, str(R), str(E), str(M), 
                    str(m_p), str(m_a), str(spec_ber), str(raw_ber)])
    load_float()
    acc = test_net()
    print(acc)
    '''
    Test set: Average loss: 2.3026, Accuracy: 980/10000 (10%)
    0.098
    '''

if __name__ == '__main__':
    # main()
    # test_net()
    # fault_inject()

    # dump_float()
    normal(ours=False)
    # rdrop()
    '''
    our:
    {4: (1, 3),
    5: (1, 3),
    6: (2, 1),
    7: (1, 2),
    8: (1, 2),
    9: (1, 2),
    10: (1, 2),
    11: (1, 2),
    12: (1, 2),
    13: (1, 2),
    14: (1, 2),
    15: (1, 2),
    16: (1, 2)}
    SBA:
    q --> (m_p, m_a)
    {4: (2, 2),
    5: (2, 2),
    6: (2, 1),
    7: (2, 1),
    8: (2, 1),
    9: (2, 1),
    10: (1, 2),
    11: (1, 2),
    12: (1, 2),
    13: (1, 2),
    14: (1, 2),
    15: (1, 2),
    16: (1, 2)}
    '''
