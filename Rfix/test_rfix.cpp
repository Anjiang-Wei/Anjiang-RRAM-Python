#include "rfix.cpp"
#include <stdlib.h>

long long RandomLL(long long a, long long b) {
  float random = ((float) rand()) / (float) RAND_MAX;
  float diff = b - a;
  float r = random * diff;
  return a + (long long)r;
}

int main() {
  vector<long long> mutation_input;
  for (int i = 0; i < 16; i++) {
    //long long a = RandomLL(-100, 100);
    long long a = i;
    mutation_input.push_back(a);
  }
  float spec_ber = 1e-13, raw_ber = 1;
  int R = 4, base = 2, p = 3, a0 = 1, f = 1;
  auto output = mutate_vec_ll(mutation_input, R, base, p, a0, f, spec_ber, raw_ber);
  for (int i = 0; i < output.size(); i++) {
    cout << mutation_input[i] << " " << output[i] << endl;
  }
  return 0;
}
