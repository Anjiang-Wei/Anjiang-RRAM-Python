#include "rfix.cpp"
#include <stdlib.h>

void validate(long long num) {
    Rfix num1 = Rfix(2, 20, num);
    long long num2 = num1.from_Rfix();
    // cout << num << "," << num2 << endl;
    assert(num - num2 == 0);
}

int RandomInt(int lower, int upper) {
    int num = (rand() % (upper - lower + 1)) + lower;
    // printf("%d \n", num);
    return num;
}

void validate2(long long num) {
    int R = RandomInt(3, 10);
    int M = RandomInt(30, 40);
    Rfix num1 = Rfix(R, M, num);
    long long num2 = num1.from_Rfix();
    cout << num << "," << num2 << endl;
    assert(num - num2 == 0);
}

void validate3(long long num) {
    int R = RandomInt(3, 10);
    int M = RandomInt(10, 30);
    Rfix num1 = Rfix(R, M, num);
    ofstream outfile;
    outfile.open("rfloat.dat");
    outfile << num1;
    cout << num1.from_Rfix() << endl;
    outfile.close();

    Rfix num2;
    ifstream infile;
    infile.open("rfloat.dat");
    infile >> num2;
    cout << num2.from_Rfix() << endl;
    infile.close();

    assert(num == num2.from_Rfix());
    assert(num1.from_Rfix() == num2.from_Rfix());
}

long long RandomLL(long long a, long long b) {
    float random = ((float) rand()) / (float) RAND_MAX;
    float diff = b - a;
    float r = random * diff;
    return a + (long long)r;
}


int main() {
    uint8_t content[23] = {0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    Rfix a = Rfix(2, 23, true, content);
    long long b = a.from_Rfix();
    a.print();
    cout << b << endl;
    cout << "--------" << endl;
    Rfix c = Rfix(2, 23, b);
    c.print();
    printf("===========================\n");
    long long d = c.from_Rfix();
    cout << d << endl;
    for (int i = 0; i < 1000; i++) {
        validate(RandomLL(-1e5, 1e5));
        validate2(RandomLL(-1e5, 1e5));
        // validate3(RandomFloat(-1e5, 1e5));
    }
    long long to_be_tested[] = {0, -1, 1, 100, -100};
    for (auto f: to_be_tested) {
        validate(f);
    }
    cout << "------test mutation-----" << endl;
    vector<long long> mutation_input;
    for (int i = 0; i < 10; i++) {
        long long a = RandomLL(-100, 100);
        mutation_input.push_back(a);
    }
    int R = 7, M = 5, m_p = 1, m_a = 4;
    float spec_ber = 1e-13, raw_ber = 0.1;
    auto output = mutate_vec_ll(mutation_input, R, M, m_p, m_a, spec_ber, raw_ber);
    for (int i = 0; i < output.size(); i++) {
        cout << mutation_input[i] << " " << output[i] << endl;
    }
    return 0;
}
