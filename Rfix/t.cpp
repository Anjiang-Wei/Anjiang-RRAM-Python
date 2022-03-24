# include <iostream>
#include <assert.h>
using namespace std;

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

int main() {
  long long x = 43;
  for (int i = 1; i < 8; i++) {
    cout << write_val(x, 0, i, 3) << endl;
  }
  return 0;
}
