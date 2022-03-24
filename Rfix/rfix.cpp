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

inline bool is_1_at(long long num, int k) { // k starting from 0
  if ((num >> k) & 1) {
    return true;
  } else {
    return false;
  }
}

int extract_val(long long input, int start, int end) {
  int result = 0;
  for (int j = start; j < end; j++) {
    if (is_1_at(input, j)) {
      result = (result << 1) + 1;
    } else {
      result = (result << 1);
    }
  }
  return result;
}

long long mutate(long long input, int R, int base, int p, int a0, int f, float spec_ber, float raw_ber)
{
  input = (input >> f);
  input = (input << f);
  for (int i = 0; i < a0; i++) {
    int val = extract_val(input, f + i * base, f + (i + 1) * base);
    
  }
}

vector<long long> mutate_vec_ll(vector<long long> input, int R, int base,
                                int p, int a0, int f, float spec_ber, float raw_ber)
{
  int size = input.size();
  for (int i = 0; i < size; i++) {
    input[i] = mutate(input[i], R, base, p, a0, f, spec_ber, raw_ber);
#ifdef DEBUG
    cout << input[i] << endl;
#endif
  }
  return input;
}
