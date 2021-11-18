#include "rfloat.cpp"
#include <stdlib.h>

void validate(float num) {
    float eps = 0.0000001;
    Rfloat num1 = Rfloat(2, 8, 23, num);
    float num2 = num1.from_Rfloat();
    // num2 += 0.01;
    // cout << num << "," << num2 << endl;
    assert(fabs(num - num2) < eps);
}

int RandomInt(int lower, int upper) {
    int num = (rand() % (upper - lower + 1)) + lower;
    // printf("%d \n", num);
    return num;
}

void validate2(float num) {
    float eps = 1e-3;
    int R = RandomInt(3, 10);
    int exp = RandomInt(6, 8);
    int man = RandomInt(10, 30);
    Rfloat num1 = Rfloat(R, exp, man, num);
    float num2 = num1.from_Rfloat();
    cout << num << "," << num2 << endl;
    assert(fabs((num - num2) / num) < eps);
}

float RandomFloat(float a, float b) {
    float random = ((float) rand()) / (float) RAND_MAX;
    float diff = b - a;
    float r = random * diff;
    return a + r;
}


int main() {
    // -354: 1 10000111 01100010000000000000000
    uint8_t exp[8] = {1, 0, 0, 0, 0, 1, 1, 1};
    uint8_t mant[23] = {0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    Rfloat a = Rfloat(2, 8, 23, true, 1, exp, mant);
    float b = a.from_Rfloat();
    a.print();
    cout << b << endl;
    cout << "--------" << endl;
    Rfloat c = Rfloat(2, 8, 23, b);
    c.print();
    float d = c.from_Rfloat();
    cout << d << endl;
    for (int i = 0; i < 100000; i++) {
        validate(RandomFloat(-1e5, 1e5));
        validate2(RandomFloat(-1e5, 1e5));
    }
    float to_be_tested[] = {0, -1, 1, 0.000001, -0.000001};
    for (auto f: to_be_tested) {
        validate(f);
    }
    return 0;
}
