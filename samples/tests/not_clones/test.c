int faculty(int x) {
    int result = x;
    while(x > 2) {
        result *= --x;
    }

    return result;
}

int main(void) {
    return faculty(5);
}
