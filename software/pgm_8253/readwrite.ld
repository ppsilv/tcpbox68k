/* Script de linkagem para endereço 0x82000 */
ENTRY(_start)

MEMORY {
    RAM (rwx) : ORIGIN = 0x82000, LENGTH = 32K
}

SECTIONS {
    . = 0x82000;

    .text : {
        *(.text)
        *(.text.*)
        *(.rodata)
        *(.rodata.*)
    } > RAM

    .data : {
        *(.data)
        *(.data.*)
    } > RAM

    .bss : {
        *(.bss)
        *(.bss.*)
        *(COMMON)
    } > RAM

    /* Define o símbolo _start no início do código */
    _start = .;

    /* Define o fim da pilha (ajuste conforme necessário) */
    _stack_end = ORIGIN(RAM) + LENGTH(RAM);

    /* Remove seções desnecessárias */
    /DISCARD/ : {
        *(.comment)
        *(.note)
        *(.eh_frame)
    }
}
