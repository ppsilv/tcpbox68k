SECTIONS {
    .text 0x00000000 : { *(.text) }
    .data 0x00010000 : { *(.data) }
    .bss  0x00081000 : { *(.bss) }
}
