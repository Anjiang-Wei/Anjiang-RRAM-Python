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


class BitLevelMapping {
    public:
        map<int, int> mapping; // a set of bits ---> index of the levels
        BitLevelMapping();
}

class Level {
    public:
        int num_levels; // the number of levels
        float BER; // Bit Error Rate specification for this Level (prob of moving to adjacent levels)
        vector<int> levels_idx; // indices of levels
}

