#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <stdint.h>
#include <assert.h>
#include <math.h>
using namespace std;

#define maxE 20
#define maxM 40

class Rfloat {
    public: 
        uint8_t R; // radix
        uint8_t E; // number of bits in exponent
        uint8_t M; // number of bits in mantissa
        bool sign;
        int bias; // to be deducted when computing exponent
        uint8_t leadingM; // within [1, R-1]
        uint8_t exp[maxE]; // each element should be within [0, radix-1]
        uint8_t mant[maxM];

        Rfloat();
        Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, bool sign_, uint8_t leadingM_, uint8_t exp_[maxE], uint8_t mant_[maxM]);
        Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, float val);

        friend ofstream& operator<<(ofstream &output, const Rfloat &D);
        friend ifstream& operator>>(ifstream &input, const Rfloat &D);

        void print();
        float from_Rfloat();
};

Rfloat::Rfloat() {
    return;
}

Rfloat::Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, bool sign_, uint8_t leadingM_, uint8_t exp_[maxE], uint8_t mant_[maxM]) {
    R = R_; E = E_; M = M_; sign = sign_; leadingM = leadingM_;
    for (int i = 0; i < maxE; i++) {
        exp[i] = exp_[i];
    }
    for (int i = 0; i < maxM; i++) {
        mant[i] = mant_[i];
    }
    bias = (int) pow(R, E-1) - 1;
}

Rfloat::Rfloat(uint8_t R_, uint8_t E_, uint8_t M_, float val) {
    R = R_; E = E_; M = M_;
    bias = (int) pow(R, E-1) - 1;
    if (val == 0) {
        sign = false;
        leadingM = 0;
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
    for (int i = E-1; i >= 0; i--) {
        // cout << "exp_val % R = " << exp_val % R << endl;
        exp[i] = exp_val % R;
        exp_val = exp_val / R;
    }
    float R_to_y = pow(R, y);
    float remainder = val / R_to_y;
    leadingM = (int) remainder;
    remainder -= leadingM;
    // cout << "remainder = " << remainder << endl;
    for (int i = 0; i < M; i++) {
        remainder *= R;
        mant[i] = (int) remainder;
        remainder -= (int) remainder;
    }
}

ofstream& operator<<(ofstream& output, const Rfloat& D) {
    output << (int) D.R << " " << (int) D.E << " " << (int) D.M <<  " " << (int) D.sign 
        << " " << (int) D.bias << " " << (int) D.leadingM << endl;
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
    input >> D.bias;
    D.leadingM = get_uint8(input);
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
    cout << (int) leadingM << ".";
    for (int i = 0; i < M; i++) {
        cout << (int) mant[i];
    }
    cout << endl;
}


float Rfloat::from_Rfloat() {
    float val = (float) leadingM;
    float weight = R;
    for (int i = 0; i < M; i++) {
        val += ((float) mant[i]) / weight;        
        weight = weight * R;
        // cout << "weight:" << weight << endl;
    }
    // cout << "val:" << val << endl;
    int exp_val = 0;
    for (int i = 0; i < E; i++) {
        exp_val = exp_val * R + (int) exp[i];
    }
    // cout << "exp_val:" << exp_val << endl;
    // cout << "bias:" << bias << endl; 
    exp_val -= bias;
    val = val * pow(R, exp_val);
    if (sign) {
        val = -val;
    }
    return val;
}
