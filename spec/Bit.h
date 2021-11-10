#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
#include <assert.h>
using namespace std;
#ifndef BIT_H
#define BIT_H

class Bit {
    public:
        // Todo: extend support for other data types
        vector<float> data;
        // 1 float = 32 bit
        vector<bitset<32>> bits;

        Bit(string filename, bool isdata);
        void PrintData();
        void PrintBits();
        void data2bits();
        void bits2data();
        void bits2file(string filename);
        void data2file(string filename);
};
#endif
