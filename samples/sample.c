#include <stdio.h>
#include "not_existant.c"

int test(void);

int glob;

int main(int t, char* args) {
    smile(t, glob);
    t = args = glob;

    // TODO: Test short if: expr ? cond : elseexpr
    if (t == glob) {
        int *asd;
        t = args[glob];
    }

    while (t) {
        printf("test %d", i);
    }

    int i;
    for(; i < 5; i++) {
        printf("i is %d", i);
    }

    return t;
}
