# include "rfloat.cpp"




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
    return 0;
}