ENTRY(_start)

MEMORY {
    ROM (rx) : ORIGIN  = 0x00000000, LENGTH = 16K
    RAM (rwx) : ORIGIN = 0x00080000, LENGTH = 128K
}

SECTIONS {
    .text : {
        _start = .;
        KEEP(*(.vectors))
        *(.text .text.*)
        . = ALIGN(4);
        _start_end = .;
    } > ROM

    .rodata : {
        *(.rodata .rodata.*)
        . = ALIGN(4);
    } > ROM

    .data : AT(ADDR(.rodata) + SIZEOF(.rodata)) {
        __data_load = LOADADDR(.data);
        __data_start = .;
        *(.data .data.*)
        . = ALIGN(4);
        __data_end = .;
    } > ROM

    /* --- Nova seção para o checksum (últimos 4 bytes da ROM) --- */
    .checksum (NOLOAD) : {
        /* Posiciona o checksum nos últimos 4 bytes da ROM */
        . = ALIGN(4);
        __checksum_addr = .;
        LONG(0);  /* Espaço reservado (será preenchido pós-build) */
    } > ROM

    .bss : {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    }

    /DISCARD/ : {
        *(.comment)
        *(.note.*)
    }
}
