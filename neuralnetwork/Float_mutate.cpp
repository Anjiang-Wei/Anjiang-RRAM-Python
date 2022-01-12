#include <iostream>
# include "../Rfloat/rfloat.cpp"
# include <stdlib.h>
#include <assert.h>
using namespace std;

int main(int argc, char* argv[]) {
    assert(argc == 10);
    ifstream infile;
    infile.open(argv[1]);
    ofstream outfile;
    outfile.open(argv[2]);

    int R; int E; int M;
    int rel_bits; int approx_bits;
    float rel_ber; float approx_ber;

    R = atoi(argv[3]);
    E = atoi(argv[4]);
    M = atoi(argv[5]);
    rel_bits = atoi(argv[6]);
    approx_bits = atoi(argv[7]);
    rel_ber = atof(argv[8]);
    approx_ber = atof(argv[9]);

    vector<float> all_floats;
    
    float x;
    while (infile >> x) {
        all_floats.push_back(x);
    }
    auto output = mutate_vec_float(all_floats, R, E, M, 0.01, 0.5, 0);

    for (auto item: output) {
        outfile << item << endl;
    }
    infile.close();
    outfile.close();
    cout << "finished!!" << endl;
    return 0;
}
