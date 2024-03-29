#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
#include <assert.h>
#include "Bit.h"
using namespace std;

Bit::Bit(string filename, bool isdata) {
    // Read float from file and initialize bits
    ifstream infile;
    infile.open(filename);
    if (isdata) {
        float d0;
        while (infile >> d0) {
            data.push_back(d0);
        }
        data2bits();
    } else {
        string s;
        while (infile >> s) {
            bitset<32> x(s);
            bits.push_back(x);
        }
        bits2data();
    }
    infile.close();
}

void Bit::PrintData() {
    for (auto d: data) {
        cout << d << endl;
    }
}

void Bit::PrintBits() {
    for (auto b : bits) {
        cout << b << endl;
    }
}

void Bit::data2bits() {
    if (bits.size() == 0) {
        for (auto d: data) {
            bitset<32> b0(*(uint32_t*)&d);
            bits.push_back(b0);
        }
    } else {
        int length = data.size();
        assert (length == bits.size());
        for (int i = 0; i < length; i++) {
            float d = data[i];
            bitset<32> b0(*(uint32_t*)&d);
            bits[i] = b0;
        }
    }
}

void Bit::bits2data() {
    if (data.size() == 0) {
        for (auto b: bits) {
            uint32_t x = b.to_ulong();
            float y = *(float*)&x;
            data.push_back(y);
        }
    } else {
        int length = bits.size();
        assert (length == data.size());
        for (int i = 0; i < length; i++) {
            uint32_t x = bits[i].to_ulong();
            data[i] = *(float*)&x;
        }
    }
}

void Bit::data2file(string filename) {
    ofstream outfile;
    outfile.open(filename);
    for (auto d : data) {
        outfile << d << endl;
    }
    outfile.close();
}

void Bit::bits2file(string filename) {
    ofstream outfile;
    outfile.open(filename);
    for (auto b : bits) {
        outfile << b << endl;
    }
    outfile.close();
}
