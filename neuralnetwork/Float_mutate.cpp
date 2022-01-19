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
    int m_p; int m_a; // m_p + m_a = M
    float spec_ber; float raw_ber;

    R = atoi(argv[3]);
    E = atoi(argv[4]);
    M = atoi(argv[5]);
    m_p = atoi(argv[6]);
    m_a = atoi(argv[7]);
    assert(m_p + m_a == M);

    spec_ber = atof(argv[8]);
    raw_ber = atof(argv[9]);

    vector<float> all_floats;

    std::ios::sync_with_stdio(false);
    std::cin.tie(0);
    
    float x;
    while (infile >> x) {
        all_floats.push_back(x);
    }
    cout << "Float_mutate configutation " << R << " " << E << " " << M
         << " " << m_p  << " " <<  m_a  << " " << spec_ber  << " " << raw_ber << std::endl;
    auto output = mutate_vec_float(all_floats, R, E, M, m_p, m_a, spec_ber, raw_ber);

    for (auto item: output) {
        outfile << item << endl;
    }
    infile.close();
    outfile.close();
    cout << "finished!!" << endl;
    return 0;
}
