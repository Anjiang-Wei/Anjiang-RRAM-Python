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

inline int mutate(int original, int R) {
  assert(original >= 0 && original < R);
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


inline bool is_1_at(long long num, int k) { // k starting from 0
  if ((num >> k) & 1) {
    return true;
  } else {
    return false;
  }
}

int extract_val(long long input, int start, int end) {
  int result = 0;
  assert(end >= 1);
  assert(end > start);
  for (int j = end - 1; j >= start; j--) {
    if (is_1_at(input, j)) {
      result = (result << 1) + 1;
    } else {
      result = (result << 1);
    }
  }
  return result;
}

long long write_val(long long input, int start, int end, int val) {
  
}

long long mutate(long long input, int R, int base, int p, int a0, int f, float spec_ber, float raw_ber)
{
  input = (input >> f);
  input = (input << f);
  for (int i = 0; i < a0; i++) {
    int val = extract_val(input, f + i * base, f + (i + 1) * base);
    if (random_bool(raw_ber)) {
      val = mutate(val, R);
    }
    input = write_val(input, f + i * base, f + (i + 1) * base, val);
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
