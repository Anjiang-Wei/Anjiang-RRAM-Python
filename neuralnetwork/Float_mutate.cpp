#include <iostream>
# include "../Rfloat/rfloat.cpp"
using namespace std;

int main(int argc, char* argv[]) {
    ifstream infile;
    infile.open(argv[1]);
    ofstream outfile;
    outfile.open(argv[2]);
    
    vector<float> all_floats;
    
    float x;
    while (infile >> x) {
        all_floats.push_back(x);
    }
    auto output = mutate_vec_float(all_floats, 5, 3, 3, 0.01, 0.5, 0);

    for (auto item: output) {
        outfile << item << endl;
    }
    infile.close();
    outfile.close();
    cout << "finished!!" << endl;
    return 0;
}
