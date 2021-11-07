#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
using namespace std;

class Bit {
    public:
        // Todo: extend support for other data types
        vector<float> data;
        // 1 float = 32 bit
        vector<bitset<32>> bits;

        Bit(string filename);
        void PrintInfo();
        void export2file(string filename);
};

Bit::Bit(string filename) {
    ifstream infile;
    infile.open(filename);
    float d0;
    while (infile >> d0) {
        data.push_back(d0);
        bitset<32> b0(*(uint32_t*)&d0);
        bits.push_back(b0);
    }
}

void Bit::PrintInfo() {
    for (auto b : bits) {
        cout << b << endl;
    }
}

int main() {
    Bit b("bit0.txt");
    b.PrintInfo();
    return 0;
}
