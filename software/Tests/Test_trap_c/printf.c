// readwrite.c
#include <stdarg.h>

// Define seu próprio stdout bare-metal
FILE *stdout = (FILE *)1;  // Apenas um identificador
FILE *stderr = (FILE *)2;

// Implementação personalizada de vfprintf
int vfprintf(FILE *stream, const char *format, va_list arg) {
    // Ignora o stream por enquanto (tudo vai para UART)
    return vprintf_custom(format, arg);
}

int printf_custom(const char *format, ...) {
    va_list args;
    va_start(args, format);
    int ret = vprintf_custom(format, args);
    va_end(args);
    return ret;
}

int vprintf_custom(const char *format, va_list args) {
    int chars_printed = 0;

    while (*format) {
        if (*format == '%') {
            format++;
            switch (*format) {
                case 'd': {
                    int num = va_arg(args, int);
                    chars_printed += printNumber(num);
                    break;
                }
                case 's': {
                    char *str = va_arg(args, char*);
                    while (*str) {
                        UART_WriteChar(*str++);
                        chars_printed++;
                    }
                    break;
                }
                case 'c': {
                    char c = (char)va_arg(args, int);
                    UART_WriteChar(c);
                    chars_printed++;
                    break;
                }
                default:
                    UART_WriteChar('%');
                    UART_WriteChar(*format);
                    chars_printed += 2;
            }
        } else {
            UART_WriteChar(*format);
            chars_printed++;
        }
        format++;
    }

    return chars_printed;
}
