#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
using namespace std;

class DataSpec {
    public:
        string datatype;
        int bitlength;
        // Given a bit index X (where 0 <= X < bit length), return its corresponding Bit Error Rate
        map<int, float> index2ber;
        // Reverse of index2ber, return all the integers satisfying the BER specification
        map<float, vector<int>> ber2index;

        DataSpec(string filename);
};

DataSpec::DataSpec(string filename) {
    ifstream infile;
    infile.open(filename);
    infile >> datatype >> bitlength;
    cout << datatype << bitlength << endl;
    float ber; int num_index;
    while (infile >> ber >> num_index) {
        while (num_index--) {
            int index;
            infile >> index;
            index2ber[index] = ber;
        }
    }
    for (auto iter = index2ber.begin(); iter != index2ber.end(); ++iter) {
        cout << iter->first << " " << iter->second << endl;
    }
}

int main() {
    DataSpec d0("spec0.txt");
    return 0;
}
