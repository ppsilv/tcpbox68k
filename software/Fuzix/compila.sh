#!/bin/bash

echo "Compilando para 68000 TARGET=68knano"

make TARGET=68knano CPU=68000 CROSS_COMPILE=m68k-elf- VERSION=0 SUBVERSION=4

