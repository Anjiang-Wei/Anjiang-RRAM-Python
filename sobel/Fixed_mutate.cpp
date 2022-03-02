#include <iostream>
# include "../Rfix/rfix.cpp"
# include <stdlib.h>
#include <assert.h>
using namespace std;

#define VERB

int main(int argc, char* argv[]) {
    assert(argc == 10);
    ifstream infile;
    infile.open(argv[1]);
    ofstream outfile;
    outfile.open(argv[2]);

    int R; int M;
    int m_p; int m_a; // m_p + m_a = M
    float scale; // RRAM is actually storing input_number * scale
    float spec_ber; float raw_ber;

    R = atoi(argv[3]);
    M = atoi(argv[4]);
    m_p = atoi(argv[5]);
    m_a = atoi(argv[6]);
    assert(m_p + m_a == M);

    scale = atof(argv[7]);

    spec_ber = atof(argv[8]);
    raw_ber = atof(argv[9]);

    vector<long long> all_fixed;

    std::ios::sync_with_stdio(false);
    std::cin.tie(0);

    float x;
    while (infile >> x) {
      all_fixed.push_back((long long)(x * scale));
    }
    #ifdef VERB
    cout << "Fixed_mutate configutation " << argv[1] << " " << argv[2] << " "
        << R << " " << M
        << " " << m_p  << " " <<  m_a
        << " " << spec_ber  << " " << raw_ber << std::endl;
    #endif
    auto output = mutate_vec_ll(all_fixed, R, M, m_p, m_a, spec_ber, raw_ber);

    for (auto item: output) {
      float scale_back = ((float) item) / scale;
      outfile << (long long) scale_back  << endl;
    }
    infile.close();
    outfile.close();
    #ifdef VERB
    cout << "finished!!" << endl;
    #endif
    return 0;
}
