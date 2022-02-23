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

#define maxM 64
// #define DEBUG

random_device rd;  // Will be used to obtain a seed for the random number engine
std::mt19937 gen(rd()); // Standard mersenne_twister_engine seeded with rd()
std::uniform_real_distribution<> dis(0.0, 1e15);

class Rfix {
public:
  uint8_t R; // radix
  uint8_t M; // number of bits in content
  bool sign; // if true (1), then negative; if false (0), then positive
  uint8_t content[maxM]; // each element should be within [0, radix-1]

  Rfix();
  Rfix(uint8_t R_, uint8_t M_, bool sign_, uint8_t content_[maxM]);
  Rfix(uint8_t R_, uint8_t M_, long long val);

  friend ofstream& operator<<(ofstream &output, const Rfix &D);
  friend ifstream& operator>>(ifstream &input, const Rfix &D);

  void print();
  long long from_Rfix();
  void mutate(int m_p, int m_a, float spec_ber, float raw_ber);
  static vector<Rfix> mutate_vec_Rfix(vector<Rfix> input,
                                      int m_p, int m_a, float spec_ber, float raw_ber);
  static vector<long long> mutate_vec_ll(vector<long long> input, int R, int M,
                                      int m_p, int m_a, float spec_ber, float raw_ber);
};

Rfix::Rfix() {
  return;
}

Rfix::Rfix(uint8_t R_, uint8_t M_, bool sign_, uint8_t content_[maxM]) {
  R = R_; M = M_; sign = sign_;
  for (int i = 0; i < M; i++) {
    content[i] = content_[i];
  }
}

Rfix::Rfix(uint8_t R_, uint8_t M_, long long val) {
    R = R_; M = M_;
    if (val < 0) {
      sign = true;
      val = -val;
    } else {
      sign = false;
    }
    for (int i = 0; i < M; i++) {
      content[i] = (uint8_t) (val % (long long) R);
      val = val / (long long) R;
    }
}

ofstream& operator<<(ofstream& output, const Rfix& D) {
  output << (int) D.R << " "  << (int) D.M <<  " " << (int) D.sign << " " << endl;
  for (int i = 0; i < D.M; i++) {
    output << (int) D.content[i] << " ";
  }
  output << endl;
  return output;
}

inline uint8_t get_uint8(ifstream &input) {
  int x;
  input >> x;
  return (uint8_t) x;
}

ifstream& operator>>(ifstream &input, Rfix &D){
  D.R = get_uint8(input);
  D.M = get_uint8(input);
  D.sign = (bool) get_uint8(input);
  for (int i = 0; i < D.M; i++) {
    D.content[i] = get_uint8(input);
  }
  return input;
}

void Rfix::print() {
  cout << "Radix: " << (int) R << endl;
  cout << "M: " << (int) M << ": " << endl;
  cout << "Sign : " << sign << endl;
  for (int i = 0; i < M; i++) {
    cout << (int) content[i];
  }
  cout << endl;
}


long long Rfix::from_Rfix() {
  long long val = 0;
  long long base = 1;
  for (int i = 0; i < M; i++) {
    val += base * content[i];
    base = base * R;
  }
  if (sign) { // negative
    val = -val;
  }
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

void Rfix::mutate(int m_p, int m_a, float spec_ber, float raw_ber) {
    #ifdef DEBUG
    cout << "Prior" << endl;
    print_uint8(content, M);
    #endif
    for (int i = 0; i < m_a; i++) {
      if (random_bool(raw_ber)) {
        content[i] = mutate_uint8(content[i], R);
      }
    }
    for (int i = m_a; i < m_a + m_p; i++) {
      if (random_bool(spec_ber)) {
        content[i] = mutate_uint8(content[i], R);
      }
    }
    #ifdef DEBUG
    cout << "After" << endl;
    print_uint8(content, M);
    cout << "==============" << endl;
#endif
}

static vector<Rfix> mutate_vec_Rfix(vector<Rfix> input,
                                    int m_p, int m_a, float spec_ber, float raw_ber) {
  int size = input.size();
  for (int i = 0; i < size; i++) {
    input[i].mutate(m_p, m_a, spec_ber, raw_ber);
  }
  return input;
}


static vector<long long> mutate_vec_ll(vector<long long> input, int R, int M,
                                  int m_p, int m_a, float spec_ber, float raw_ber)
{
  assert(m_p + m_a == M);
  int size = input.size();
  uint8_t R_ = (uint8_t) R;
  uint8_t M_ = (uint8_t) M;
  for (int i = 0; i < size; i++) {
    long long val = input[i];
    Rfix a = Rfix(R_, M_, val);
    a.mutate(m_p, m_a, spec_ber, raw_ber);
    input[i] = a.from_Rfix();
#ifdef DEBUG
    cout << val << " " << input[i] << endl;
#endif
  }
  return input;
}
