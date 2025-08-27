#include <stdio.h>
#include <stdlib.h>

#include <mc68000.h>
#include <stdio.h>

// Função para verificar stack
void check_stack(void) {
    unsigned long stack_val;
    asm volatile (
        "move.l %%sp, %0\n\t"
        : "=r" (stack_val)
    );
    printf("Stack pointer: 0x%08X\n", stack_val);
}

int main() {
    check_stack();  // ✅ Verificar stack no início

    printf("Hello MC68000!\n");

    check_stack();  // ✅ Verificar stack no meio

    // Teste de stack - não fazer isso em produção!
    volatile int test_array[10];
    for (int i = 0; i < 10; i++) {
        test_array[i] = i;
    }

    check_stack();  // ✅ Verificar stack no final

    return 42;
}

/*
int main() {
    system_init();
    printf("Hello MC68000!\n");
    printf("Testing printf: %d ox%x %s\n", 123, 0xABC, "string");

    asm volatile (
        "MOVE.W #0, %%D0\n\t"   // PTERM0
        "TRAP #0\n\t"
        :
        :
        : "d0", "cc"
    );


    return 0;
}
*/
