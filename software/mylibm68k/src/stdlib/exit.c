#include <stdlib.h>

/* Função exit() que chama trap #0 para retornar ao monitor */
void exit(int status) {
    /* Passar status de retorno em D0 para o monitor */
    /*
    __asm__ volatile (
        "move.l %0, %%d0\n\t"   // Colocar status em D0
        "trap #0\n\t"           // Chamar monitor
        : // no outputs
        : "r" (status)
        : "d0"
    );
    */
            asm volatile (
                "MOVE.W #0, %%D0\n\t"   // PTERM0
                "TRAP #0\n\t"
                :
                :
                : "d0", "cc"
            );
    /* Loop infinito se trap retornar (não deveria) */
    while (1);
}
