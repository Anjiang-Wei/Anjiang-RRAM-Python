#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
#include <assert.h>
#include <boost/dynamic_bitset.hpp>
#include <boost/utility/binary.hpp>
#include "Bit.h"
#include "Bit.cpp"
#include "DataSpec.h"
using namespace std;


class GroupBit {
    public:
        // BER, bits
        map<float, boost::dynamic_bitset<>> groupBits;
        GroupBit(Bit bit, DataSpec spec);
        
        void PrintBits();
};

GroupBit::GroupBit(Bit b, DataSpec spec) {
    for (auto bs: b.bits) {
        // Todo: only works for 32 bit
        for (int i = 0; i < 32; i++) {
            groupBits[spec.index2ber[i]].append(bs[i]);
        }
    }
}

void GroupBit::PrintBits() {
    for (auto iter = groupBits.begin(); iter != groupBits.end(); ++iter) {
        cout << iter->first << ": [ " << iter->second << "]" << endl;
    }
}

int main() {
    Bit b0("float0.txt", true);
    DataSpec s0("spec0.txt");
    GroupBit g0(b0, s0);
    g0.PrintBits();
    return 0;
}
