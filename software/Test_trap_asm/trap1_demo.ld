/* Script de linker para programa TRAP #1 */
OUTPUT_FORMAT("elf32-m68k")
ENTRY(_start)

MEMORY {
    RAM (rwx) : ORIGIN = 0x82000, LENGTH = 32K
}

SECTIONS {
    . = 0x82000;

    .text : {
        *(.text)
        *(.text.*)
    } > RAM

    .data : {
        *(.data)
        *(.rodata)
    } > RAM

    .bss : {
        *(.bss)
        *(COMMON)
    } > RAM

    /* Define símbolos para o programa */
    _start = .;
    _end = .;

    /* Pilha no topo da memória */
    _stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
