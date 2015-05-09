int faculty(int x) {
    int result = x;
    while(x > 2) {
        result *= --x;
    }

    return result;
}

int power(int x, int y) {
    int result = x;
    for(; y>1; y--) {
        result *= x;
    }

    return result;
}

int main(void) {
    return faculty(5);
}
