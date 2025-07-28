ENTRY(_start)

MEMORY {
    ROM (rx) : ORIGIN  = 0x00000000, LENGTH = 256K
    RAM (rwx) : ORIGIN = 0x00080000, LENGTH = 128K
}

SECTIONS {
    .text : {
        KEEP(*(.vectors))
        *(.text .text.*)
        . = ALIGN(4);
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
    } > RAM

    .bss : {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > RAM

    /DISCARD/ : {
        *(.comment)
        *(.note.*)
    }
}
