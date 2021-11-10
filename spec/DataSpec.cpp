#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include "DataSpec.h"
using namespace std;


int main() {
    DataSpec d0("spec0.txt");
    d0.PrintInfo();
    return 0;
}
