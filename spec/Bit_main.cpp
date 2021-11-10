#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <bitset>
#include <assert.h>
#include "Bit.h"
using namespace std;


int main() {
    Bit b("bit0.txt", false);
    b.data2file("float0.txt");
    b.PrintBits();
    b.PrintData();
    Bit c("float0.txt", true);
    c.PrintBits();
    c.PrintData();
    return 0;
}
