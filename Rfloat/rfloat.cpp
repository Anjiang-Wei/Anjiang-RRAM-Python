#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <random>
using namespace std;

#define maxE 20
#define maxM 40

// #define DEBUG
// #define inf2zero

random_device rd;  // Will be used to obtain a seed for the random number engine
std::mt19937 gen(rd()); // Standard mersenne_twister_engine seeded with rd()
std::uniform_real_distribution<> dis(0.0, 1e15);

class Rfloat {
    public: 
        uint8_t R; // radix
        uint8_t E; // number of bits in exponent
        uint8_t M; // number of bits in mantissa.
        bool sign;
        int bias; // to be deducted when computing exponent
        uint8_t exp[maxE]; // each element should be within [0, radix-1]
        uint8_t mant[maxM];

        Rfloat();
        Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, bool sign_, uint8_t exp_[maxE], uint8_t mant_[maxM]);
        Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, float val);

        friend ofstream& operator<<(ofstream &output, const Rfloat &D);
        friend ifstream& operator>>(ifstream &input, const Rfloat &D);

        void print();
        float from_Rfloat();
        void mutate(int m_p, int m_a, float spec_ber, float raw_ber);
        static vector<Rfloat> mutate_vec_Rfloat(vector<Rfloat> input, 
                        int m_p, int m_a, float spec_ber, float raw_ber);
        static vector<float> mutate_vec_float(vector<float> input,
                        int R, int E, int M, int m_p, int m_a, float spec_ber, float raw_ber);
};

Rfloat::Rfloat() {
    return;
}

Rfloat::Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, bool sign_, uint8_t exp_[maxE], uint8_t mant_[maxM]) {
    R = R_; E = E_; M = M_; sign = sign_;
    for (int i = 0; i < maxE; i++) {
        exp[i] = exp_[i];
    }
    for (int i = 0; i < maxM; i++) {
        mant[i] = mant_[i];
    }
    bias = (int) pow(R, E-1) - 1;
    if (E == 0) {
      bias = 0;
    }
}

Rfloat::Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, float val) {
    R = R_; E = E_; M = M_;
    bias = (int) pow(R, E-1) - 1;
    if (E == 0) {
      bias = 0;
    }
    if (val == 0) {
        sign = false;
        for (int i = 0; i < maxE; i++) {
            exp[i] = 0;
        }
        for (int i = 0; i < maxM; i++) {
            mant[i] = 0;
        }
        return;
    }
    if (val > 0) {
        sign = false;
    } else {
        sign = true;
    }
    val = fabs(val);
    int y = (int) (log(val) / log(R));
    int exp_val = y + bias;
    if (exp_val < 0) { // if original exp_val negative, Rfloat has to turn its exp_val into 0
        y = y - exp_val;
        exp_val = 0;
    }
    for (int i = E-1; i >= 0; i--) {
        #ifdef DEBUG
            cout << "exp_val % R = " << exp_val % R << endl;
        #endif
        exp[i] = exp_val % R;
        exp_val = exp_val / R;
    }
    float R_to_y = pow(R, y);
    float remainder = val / R_to_y;
    mant[0] = (uint8_t)((int) remainder);
    assert(mant[0] >= 0 && mant[0] < R);
    remainder -= ((int) remainder);
    #ifdef DEBUG
        cout << "remainder = " << remainder << endl;
    #endif
    for (int i = 1; i < M; i++) {
        remainder *= R;
        mant[i] = (int) remainder;
        remainder -= (int) remainder;
    }
}

ofstream& operator<<(ofstream& output, const Rfloat& D) {
    output << (int) D.R << " " << (int) D.E << " " << (int) D.M <<  " " << (int) D.sign << endl;
    for (int i = 0; i < D.E; i++) {
        output << (int) D.exp[i] << " ";
    }
    output << endl;
    for (int i = 0; i < D.M; i++) {
        output << (int) D.mant[i] << " ";
    }
    output << endl;
    return output;
}

inline uint8_t get_uint8(ifstream &input) {
    int x;
    input >> x;
    return (uint8_t) x;
}

ifstream& operator>>(ifstream &input, Rfloat &D){
    D.R = get_uint8(input);
    D.E = get_uint8(input);
    D.M = get_uint8(input);
    D.sign = (bool) get_uint8(input);
    D.bias = (int) pow(D.R, D.E-1) - 1;
    if (D.E == 0) {
        D.bias = 0;
    }
    for (int i = 0; i < D.E; i++) {
        D.exp[i] = get_uint8(input);
    }
    for (int i = 0; i < D.M; i++) {
        D.mant[i] = get_uint8(input);
    }
    return input;
}

void Rfloat::print() {
    cout << "Radix: " << (int) R << endl;
    cout << "Sign : " << sign << endl;
    cout << "Exp-" << (int) E << ": " << endl;
    for (int i = 0; i < E; i++) {
        cout << (int) exp[i];
    }
    cout << endl << "Man-" << (int) M << ": " << endl;
    for (int i = 0; i < M; i++) {
        cout << (int) mant[i];
    }
    cout << endl;
}


float Rfloat::from_Rfloat() {
    if (M == 0) {
        return 0;
    }
    float val = mant[0];
    float weight = R;
    for (int i = 1; i < M; i++) {
        val += ((float) mant[i]) / weight;
        weight = weight * R;
        // cout << "weight:" << weight << endl;
    }
    #ifdef DEBUG
    cout << "val:" << val << endl;
    #endif
    int exp_val = 0;
    for (int i = 0; i < E; i++) {
        exp_val = exp_val * R + (int) exp[i];
    }
    #ifdef DEBUG
    cout << "exp_val:" << exp_val << endl;
    cout << "bias:" << bias << endl;
    #endif
    exp_val -= bias;
    val = val * pow(R, exp_val);
    if (sign) {
        val = -val;
    }
    #ifdef inf2zero
    if (isinf(val)) {
        val = 0;
    }
    #endif
    return val;
}

inline bool random_bool(float ber) {
    // srand(time(0));
    float rand_gen = dis(gen);
    bool TrueFalse = rand_gen < (ber * 1e15);
    return TrueFalse;
}

inline uint8_t mutate_uint8(uint8_t original, uint8_t R) {
    // srand(time(0));
    if (original == 0)
        return original + 1;
    if (original == R - 1) {
        return original - 1;
    }
    if (random_bool(0.5)) {
        return original + 1;
    } else {
        return original - 1;
    }
}

void print_uint8(uint8_t array[], int num) {
    cout << "-----" << endl;
    for (int i = 0; i < num; i++) {
        cout << (int) array[i] << " ";
    }
    cout << endl << "-------" << endl;
}

void Rfloat::mutate(int m_p, int m_a, float spec_ber, float raw_ber) {
    #ifdef DEBUG
    cout << "Prior" << endl;
    print_uint8(exp, E);
    print_uint8(mant, M);
    #endif
    for (int i = 0; i < E; i++) {
        // E: always precise
        if (random_bool(spec_ber)) {
            exp[i] = mutate_uint8(exp[i], R);
        }
    }
    for (int i = 0; i < m_p; i++) {
        // m_p: precise
        if (random_bool(spec_ber)) {
            mant[i] = mutate_uint8(mant[i], R);
        }
    }
    assert(m_a + m_p == M);
    for (int i = m_p; i < m_p + m_a; i++) {
        // m_a: approximate
        if (random_bool(raw_ber)) {
            mant[i] = mutate_uint8(mant[i], R);
        }
    }
    #ifdef DEBUG
    cout << "After" << endl;
    print_uint8(exp, E);
    print_uint8(mant, M);
    cout << "==============" << endl;
    #endif
}

static vector<Rfloat> mutate_vec_Rfloat(vector<Rfloat> input,
    int m_p, int m_a, float spec_ber, float raw_ber) {
    int size = input.size();
    for (int i = 0; i < size; i++) {
        input[i].mutate(m_p, m_a, spec_ber, raw_ber);
    }
    return input;
}


static vector<float> mutate_vec_float(vector<float> input,
    int R, int E, int M, int m_p, int m_a, float spec_ber, float raw_ber) {
    /*
    R, E, M: base, number of bits for exponent, mantissa
    m_p, m_a: m_p + m_a = M; number of precise/approximate bits
    spec_ber: specification for precise drift error probability
    raw_ber: for the base R, the drift error probability
    */
    int size = input.size();
    uint8_t R_ = (uint8_t) R;
    uint8_t E_ = (uint8_t) E;
    uint8_t M_ = (uint8_t) M;
    for (int i = 0; i < size; i++) {
        float val = input[i];
        Rfloat a = Rfloat(R_, E_, M_, val);
        a.mutate(m_p, m_a, spec_ber, raw_ber);
        input[i] = a.from_Rfloat();
        #ifdef DEBUG
            cout << val << " " << input[i] << endl;
        #endif
    }
    return input;
}
