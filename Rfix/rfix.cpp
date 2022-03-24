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

inline int mutate_single(int original, int R) {
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


#define is_1_at(x,y) (((x) >> (y))&1)

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

#define set1(x,y) (x|=(1<<(y)))
#define set0(x,y) (x&=~(1<<(y)))

#define reversebit(x,y) (x^=(1<<(y)))

long long write_val(long long input, int start, int end, int val) {
  assert(end >= 1);
  assert(end > start);
  for (int j = start; j < end; j++) {
    if (is_1_at(val, j-start)) {
      set1(input, j);
    } else {
      set0(input, j);
    }
  }
  return input;
}

long long mutate(long long input, int R, int base, int p, int a0, int f, float spec_ber, float raw_ber)
{
  input = (input >> f);
  input = (input << f);
  for (int i = 0; i < a0; i++) {
    int val = extract_val(input, f + i * base, f + (i + 1) * base);
    if (random_bool(raw_ber)) {
#ifdef DEBUG
      cout << i << " " << f + i * base << " " << f + (i + 1) * base << " flip1" << endl;
#endif
      val = mutate_single(val, R);
    }
    input = write_val(input, f + i * base, f + (i + 1) * base, val);
  }
  for (int i = 0; i < p; i++) {
    if (random_bool(spec_ber)) {
#ifdef DEBUG
      cout << "flip2" << endl;
#endif
      reversebit(input, f + a0 * base + i);
    }
  }
  return input;
}

vector<long long> mutate_vec_ll(vector<long long> input, int R, int base,
                                int p, int a0, int f, float spec_ber, float raw_ber)
{
  int size = input.size();
  for (int i = 0; i < size; i++) {
    input[i] = mutate(input[i], R, base, p, a0, f, spec_ber, raw_ber);
#ifdef DEBUG
    // cout << input[i] << endl;
#endif
  }
  return input;
}
