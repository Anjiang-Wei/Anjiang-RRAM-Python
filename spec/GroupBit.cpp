#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
#include <assert.h>
#include <boost/dynamic_bitset.hpp>
#include <boost/utility/binary.hpp>

#include "Bit.cpp"
#include "DataSpec.cpp"
using namespace std;


class GroupBit {
    public:
        // BER, bits
        map<float, boost::dynamic_bitset<>> groupBits;
        GroupBit(Bit bit, DataSpec spec);
        
        void PrintBits();
}

GroupBit::GroupBit(Bit b, DataSpec spec) {
    for (auto bs: b.bits) {
        // Todo: only works for 32 bit
        for (int i = 0; i < 32; i++) {
            groupBits[spec.index2ber[i]].append(bs[i])
        }
    }
}

void GroupBit::PrintBits() {
    for (auto iter = groupBits.begin(); iter != groupBits.end(); ++iter) {
        cout << iter->first << ": [ ";
        for (auto val : iter->second) {
            cout << val << " ";
        }
        cout << "]" << endl;
    }
}

int main() {

}
