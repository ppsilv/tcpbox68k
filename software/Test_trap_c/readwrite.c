// Definições de funções GEMDOS compatíveis
#define PTERM0  0x00
#define CCONIN  0x01
#define CCONOUT 0x02

// Declarações para evitar otimizações
volatile int trap_result;
volatile int trap_param;

int main(void);

// Função de entrada do programa - DEVE ser _start
void _start(void) {
    // Chama a função main
    main();

    // Se retornar, termina o programa
    asm volatile (
        "MOVE.W #0, %%D0\n\t"   // PTERM0
        "TRAP #1\n\t"
        :
        :
        : "d0", "cc"
    );

    // Loop infinito de segurança
    while(1) {}
}

// Print a character using the TUTOR monitor trap function.
void outch(char c) {
    asm volatile (
        "movem.l %%d0/%%d1/%%a0,-(%%sp)\n\t"  // Save modified registers
        "move.b %0, %%d1\n\t"                 // Put character in D1
        "move.w #2, %%d0\n\t"                 // OUTCH trap function code
        "trap #1\n\t"                         // Call TUTOR function
        "movem.l (%%sp)+,%%d0/%%d1/%%a0"      // Restore registers
        :
        : "r" (c)
        : "d0", "d1", "a0", "cc", "memory"
    );
}

// Ler caractere do console
int read_char(void) {
    int result;
    asm volatile (
        "MOVE.W #1, %%D0\n\t"   // CCONIN
        "TRAP #1\n\t"
        "MOVE.L %%D0, %0"
        : "=g" (result)
        :
        : "d0", "d1", "cc", "memory"
    );
    return result & 0xFF; // Retorna apenas o byte inferior
}

// Escrever caractere no console
void write_char(int c) {
    trap_param = c; // Garante que o valor não seja otimizado
    asm volatile (
        "MOVE.W #2, %%D0\n\t"   // CCONOUT
        "MOVE.L %0, %%D1\n\t"
        "TRAP #1"
        :
        : "g" (trap_param)
        : "d0", "d1", "cc", "memory"
    );
}

// Função principal
int main(void) {
    // Teste básico de escrita
    outch('A');
    outch('A');
    outch('A');
    outch('A');
    outch('A');
    write_char('A');
    write_char('B');
    write_char('C');
    write_char('\n');

    // Mensagem de prompt
    write_char('D');
    write_char('i');
    write_char('g');
    write_char('i');
    write_char('t');
    write_char('e');
    write_char(':');
    write_char(' ');

    // Loop de leitura/escrita
    while(1) {
        int c = read_char();
        write_char('\n');
        write_char('R');
        write_char('e');
        write_char('c');
        write_char('e');
        write_char('b');
        write_char('i');
        write_char(':');
        write_char(' ');
        write_char(c);
        write_char('\n');
        write_char(':');
        write_char(' ');
    }
    return 0;
}
