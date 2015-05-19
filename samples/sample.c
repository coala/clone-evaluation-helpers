#include <stdio.h>
#include "not_existant.c"

int test(void);
int another(void) {
    int i;
    return i;
}

int quite_another(void) {
    int g;
    return g;
}

int glob;

#define INC(a, b)  a = a + b

struct test_type {
    int member1,
    int member2
}

int main(int t, char* args) {
    smile(t, glob);
    t = args = glob;
    struct test_type *a_thing;
    a_thing->member1 = 2;

    INC(t, 1);

    // TODO: Test short if: expr ? cond : elseexpr
    if (t == glob) {
        int *asd;
        t = args[glob];
    }

    int i;
    while (t)
        printf("i is %d", i);

    for(; i < 5; i++) {
        printf("i is %d", i);
    }

    return t;
}

int not_main(char g, int h) {
    for(int j; j < g; h++) {

    }
}
