#include <stdarg.h>

// Definições de funções GEMDOS compatíveis
#define PTERM0  0x00
#define CCONIN  0x01
#define CCONOUT 0x02

// Declarações para evitar otimizações
volatile int trap_result;
volatile int trap_param;

int main(void);
int printf(const char *format, ...);

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
int get_status(void){
    int result=0;
    asm volatile (
        "MOVE.W %%SR, %%D0\n\t"   // CCONIN
        "MOVE.L %%D0, %0"
        : "=g" (result)
        :
        : "d0", "d1", "cc", "memory"
    );
    return result;
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
// Print a string.
void printString(const char *s) {
    while (*s != 0) {
        outch(*s);
        s++;
    }
}
/*
void printNumber(unsigned int n) {
    unsigned int d;
    short digitPrinted = 0;
    unsigned int mult = 1000000000;

    while (mult > 1) {
        d = n / mult;
        if (d == 0) {
            if (digitPrinted) {
                outch(d + '0');
            }
        } else {
            outch(d + '0');
            digitPrinted = 1;
        }
        n = n - d * mult;
        mult = mult / 10;
    }
    outch(n + '0');
}
*/

//void UART_WriteChar(int){

//}

// Função principal
int main(void) {
    int status=get_status();
   // int a= 2/1;
    // Teste básico de escrita
    printString("Teste basico de ling C e assembler\n");
    printString("Status ");
    printf("Teste Int[0x%X] string[%s] char [%c] [0x%x] [0x%X]\n", status&0x0000FFFF,"Teste printf",'Z', 12,65535);
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
        if( c == 0x1b ){
            printString("Digitado ESC retornando");
            asm volatile (
                "MOVE.W #0, %%D0\n\t"   // PTERM0
                "TRAP #0\n\t"
                :
                :
                : "d0", "cc"
            );
        }
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

#include <stdarg.h>
/*
 *
    printf("=== Sistema MC68000 ===\n");
    printf("Char: %c\n", 'A');
    printf("Decimal: %d\n", 12345);
    printf("Negativo: %d\n", -6789);
    printf("Unsigned: %u\n", 4000000000U);
    printf("Hexadecimal: 0x%x\n", 0xABCDEF);
    printf("Octal: %o\n", 255);
    printf("String: %s\n", "Hello World!");
    printf("Mix: %c %d %s 0x%x\n", 'X', 42, "test", 0x123);
    printf("Porcentagem: 100%% completo\n");

    // Testes diversos
    printf("Zero: %d\n", 0);
    printf("Max int: %d\n", 2147483647);
    printf("Min int: %d\n", -2147483648);

  Características desta implementação:
✅ ZERO operações de ponto flutuante

✅ ZERO divisões/multiplicações

✅ ZERO dependências de biblioteca

✅ Usa apenas: adição, subtração, shifts, comparações

✅ Suporte completo a: %c, %d, %i, %u, %x, %o, %s, %%

✅ Float ignorado mas não causa erro

✅ Código completamente independente
 *
 *
 */
// Função para enviar um caractere pela serial
void putchar(char c) {
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

// Função para enviar string
void puts(const char *str) {
    while (*str) {
        putchar(*str++);
    }
}

// Função strlen simples
int strlen(const char *str) {
    int len = 0;
    while (*str++) len++;
    return len;
}

// Conversão de hexadecimal usando shifts (sem divisão)
char *itox(unsigned int value, char *str) {
    char *ptr = str;
    int started = 0;

    if (value == 0) {
        *ptr++ = '0';
        *ptr = '\0';
        return str;
    }

    for (int shift = 28; shift >= 0; shift -= 4) {
        int nibble = (value >> shift) & 0xF;
        if (nibble != 0 || started) {
            *ptr++ = "0123456789abcdef"[nibble];
            started = 1;
        }
    }

    *ptr = '\0';
    return str;
}

// Conversão de decimal usando lookup table (sem divisão)
char *itodec(int value, char *str) {
    char *ptr = str;

    if (value == 0) {
        *ptr++ = '0';
        *ptr = '\0';
        return str;
    }

    if (value < 0) {
        *ptr++ = '-';
        value = -value;
    }

    unsigned int uvalue = value;

    // Potências de 10 pré-calculadas
    static const unsigned int powers[] = {
        1000000000, 100000000, 10000000, 1000000, 100000, 10000, 1000, 100, 10, 1
    };

    int started = 0;

    for (int i = 0; i < 10; i++) {
        unsigned int power = powers[i];
        int digit = 0;

        // Contar subtrações (em vez de divisão)
        while (uvalue >= power) {
            uvalue -= power;
            digit++;
        }

        if (digit != 0 || started) {
            *ptr++ = '0' + digit;
            started = 1;
        }
    }

    *ptr = '\0';
    return str;
}

// Conversão de octal usando shifts (sem divisão)
char *itooct(unsigned int value, char *str) {
    char *ptr = str;
    int started = 0;

    if (value == 0) {
        *ptr++ = '0';
        *ptr = '\0';
        return str;
    }

    for (int shift = 30; shift >= 0; shift -= 3) {
        int triplet = (value >> shift) & 0x7;
        if (triplet != 0 || started) {
            *ptr++ = '0' + triplet;
            started = 1;
        }
    }

    *ptr = '\0';
    return str;
}

// Conversão de unsigned decimal (sem divisão)
char *itoudec(unsigned int value, char *str) {
    char *ptr = str;

    if (value == 0) {
        *ptr++ = '0';
        *ptr = '\0';
        return str;
    }

    // Potências de 10 para unsigned
    static const unsigned int powers[] = {
        1000000000, 100000000, 10000000, 1000000, 100000, 10000, 1000, 100, 10, 1
    };

    int started = 0;

    for (int i = 0; i < 10; i++) {
        unsigned int power = powers[i];
        int digit = 0;

        while (value >= power) {
            value -= power;
            digit++;
        }

        if (digit != 0 || started) {
            *ptr++ = '0' + digit;
            started = 1;
        }
    }

    *ptr = '\0';
    return str;
}

// Implementação principal do printf - SEM FLOAT
int printf(const char *format, ...) {
    va_list args;
    va_start(args, format);

    int chars_printed = 0;
    char buffer[32];

    while (*format) {
        if (*format == '%') {
            format++;

            switch (*format) {
                case 'c': {
                    char c = (char)va_arg(args, int);
                    putchar(c);
                    chars_printed++;
                    break;
                }

                case 'd':
                case 'i': {
                    int num = va_arg(args, int);
                    itodec(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case 'u': {
                    unsigned int num = va_arg(args, unsigned int);
                    itoudec(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case 'f':
                case 'F': {
                    // Ignorar floats - consumir argumento mas não usar
                    puts("[float]");
                    chars_printed += 7;
                    va_arg(args, double);
                    break;
                }

                case 's': {
                    char *str = va_arg(args, char*);
                    if (str) {
                        puts(str);
                        chars_printed += strlen(str);
                    } else {
                        puts("(null)");
                        chars_printed += 6;
                    }
                    break;
                }

                case 'x':
                case 'X': {
                    unsigned int num = va_arg(args, unsigned int);
                    itox(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case 'o': {
                    unsigned int num = va_arg(args, unsigned int);
                    itooct(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case '%': {
                    putchar('%');
                    chars_printed++;
                    break;
                }

                default:
                    putchar('%');
                    putchar(*format);
                    chars_printed += 2;
                    break;
            }
        } else {
            putchar(*format);
            chars_printed++;
        }

        format++;
    }

    va_end(args);
    return chars_printed;
}

// Funções auxiliares simples
void memcpy(void *dest, const void *src, int n) {
    char *d = (char *)dest;
    const char *s = (const char *)src;
    while (n--) *d++ = *s++;
}

void memset(void *s, int c, int n) {
    char *p = (char *)s;
    while (n--) *p++ = c;
}

int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char *)s1 - *(unsigned char *)s2;
}



















/*

#include <stdarg.h>

// Função para enviar um caractere pela serial
void putchar(char c) {
    // Implementação específica para seu hardware
    volatile char *uart_data = (volatile char *)0x10000000;
    volatile char *uart_status = (volatile char *)0x10000004;

    while (!(*uart_status & 0x02));
    *uart_data = c;
}

// Função para enviar string
void puts(const char *str) {
    while (*str) {
        putchar(*str++);
    }
}

// Função strlen simples
int strlen(const char *str) {
    int len = 0;
    while (*str++) len++;
    return len;
}

// Implementação de divisão e módulo usando subtração
void divide_mod(int dividend, int divisor, int *quotient, int *remainder) {
    if (divisor == 0) {
        *quotient = 0;
        *remainder = 0;
        return;
    }

    int sign = 1;
    unsigned int udividend, udivisor;

    // Converter para unsigned mantendo sinal
    if (dividend < 0) {
        sign = -sign;
        udividend = -dividend;
    } else {
        udividend = dividend;
    }

    if (divisor < 0) {
        sign = -sign;
        udivisor = -divisor;
    } else {
        udivisor = divisor;
    }

    // Divisão por subtração
    *quotient = 0;
    while (udividend >= udivisor) {
        udividend -= udivisor;
        (*quotient)++;
    }

    *quotient *= sign;
    *remainder = udividend;
}

// Conversão de número para string (sem divisão/multiplicação)
char *itoa_simple(int value, char *str, int base) {
    char *ptr = str;
    char *start = str;
    char tmp_char;
    unsigned int uvalue;
    int quotient, remainder;

    // Handle negativo para base 10
    if (value < 0 && base == 10) {
        *ptr++ = '-';
        uvalue = -value;
        start++;
    } else {
        uvalue = (unsigned int)value;
    }

    // Converter dígitos usando nossa própria divisão
    char *digits_start = ptr;
    do {
        divide_mod(uvalue, base, &quotient, &remainder);
        *ptr++ = "0123456789abcdef"[remainder];
        uvalue = quotient;
    } while (uvalue > 0);

    *ptr-- = '\0';

    // Inverter a string
    while (digits_start < ptr) {
        tmp_char = *digits_start;
        *digits_start++ = *ptr;
        *ptr-- = tmp_char;
    }

    return str;
}

// Conversão de hexadecimal para string (sem divisão)
char *itox_simple(unsigned int value, char *str) {
    char *ptr = str;

    for (int i = 28; i >= 0; i -= 4) {
        int nibble = (value >> i) & 0xF;
        if (nibble != 0 || ptr != str || i == 0) {
            *ptr++ = "0123456789abcdef"[nibble];
        }
    }

    *ptr = '\0';
    return str;
}

// Conversão de decimal para string usando lookup table (muito rápido)
char *itod_simple(int value, char *str) {
    char *ptr = str;

    if (value < 0) {
        *ptr++ = '-';
        value = -value;
    }

    // Lookup table para potências de 10
    const unsigned int powers[] = {
        1000000000, 100000000, 10000000, 1000000, 100000, 10000, 1000, 100, 10, 1
    };

    int started = 0;
    unsigned int uvalue = value;

    for (int i = 0; i < 10; i++) {
        unsigned int power = powers[i];
        int digit = 0;

        while (uvalue >= power) {
            uvalue -= power;
            digit++;
        }

        if (digit != 0 || started || i == 9) {
            *ptr++ = '0' + digit;
            started = 1;
        }
    }

    *ptr = '\0';
    return str;
}

// Implementação principal do printf SEM FLOAT
int printf(const char *format, ...) {
    va_list args;
    va_start(args, format);

    int chars_printed = 0;
    char buffer[32];

    while (*format) {
        if (*format == '%') {
            format++;

            switch (*format) {
                case 'c': {
                    char c = (char)va_arg(args, int);
                    putchar(c);
                    chars_printed++;
                    break;
                }

                case 'd':
                case 'i': {
                    int num = va_arg(args, int);
                    itod_simple(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case 'f':
                case 'F': {
                    // Ignorar floats completamente
                    puts("[float]");
                    chars_printed += 7;
                    va_arg(args, double); // Consumir o argumento
                    break;
                }

                case 's': {
                    char *str = va_arg(args, char*);
                    if (str) {
                        puts(str);
                        chars_printed += strlen(str);
                    } else {
                        puts("(null)");
                        chars_printed += 6;
                    }
                    break;
                }

                case 'x':
                case 'X': {
                    unsigned int num = va_arg(args, unsigned int);
                    itox_simple(num, buffer);
                    puts(buffer);
                    chars_printed += strlen(buffer);
                    break;
                }

                case '%': {
                    putchar('%');
                    chars_printed++;
                    break;
                }

                default:
                    putchar('%');
                    putchar(*format);
                    chars_printed += 2;
                    break;
            }
        } else {
            putchar(*format);
            chars_printed++;
        }

        format++;
    }

    va_end(args);
    return chars_printed;
}

*/
