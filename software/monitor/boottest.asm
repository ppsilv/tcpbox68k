; zBug V1.0 is a small monitor program for 68000-Based Single Board Computer
; The source code was assembled using C32 CROSS ASSEMBLER VERSION 3.0
;

; Copyright (c) 2002 WICHIT SIRICHOTE email kswichit@kmitl.ac.th
; 
;
; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; November 6 2014 - Modifications for 68Katy by Steve Chamberlin
;

LOADADDR    EQU $00000

; 68Katy memory map
ROMBASE	    EQU $00000
SERIN       EQU $78000
SEROUT      EQU $7A000
SERSTATUS   EQU $7C000
DOUT        EQU $7E000
RAM         EQU $80000
RAMTOP      EQU $FFFFF

; RAM-resident vector jump table, 198 bytes
; the ROM exception vectors point here
JUMP_TABLE_TOP  EQU  RAMTOP-5
JBUS_ERR    EQU  JUMP_TABLE_TOP ; 32
JADDR_ERR   EQU  JBUS_ERR-6 ; 31
JILLEGAL    EQU  JADDR_ERR-6
JZERO_DIV   EQU  JILLEGAL-6 ; 29
JCHK        EQU  JZERO_DIV-6
JTRAPV      EQU  JCHK-6 ; 27
JPRIV_VIOL  EQU  JTRAPV-6
JTRACE      EQU  JPRIV_VIOL-6 ; 25
JLINE_A     EQU  JTRACE-6
JLINE_F     EQU  JLINE_A-6 ; 23
JINT1       EQU  JLINE_F-6
JINT2       EQU  JINT1-6
JINT3       EQU  JINT2-6
JINT4       EQU  JINT3-6
JINT5       EQU  JINT4-6
JINT6       EQU  JINT5-6
JINT7       EQU  JINT6-6 ; 16
JTRAP0      EQU  JINT7-6
JTRAP1      EQU  JTRAP0-6
JTRAP2      EQU  JTRAP1-6
JTRAP3      EQU  JTRAP2-6
JTRAP4      EQU  JTRAP3-6
JTRAP5      EQU  JTRAP4-6
JTRAP6      EQU  JTRAP5-6
JTRAP7      EQU  JTRAP6-6
JTRAP8      EQU  JTRAP7-6
JTRAP9      EQU  JTRAP8-6
JTRAPA      EQU  JTRAP9-6
JTRAPB      EQU  JTRAPA-6
JTRAPC      EQU  JTRAPB-6
JTRAPD      EQU  JTRAPC-6
JTRAPE      EQU  JTRAPD-6
JTRAPF      EQU  JTRAPE-6
JLAST_ENTRY EQU  JTRAPF      

; jump table patching
JUMPLONG    EQU  $4EF9           ; opcode for jmp long

; Monitor's RAM area, 192 bytes
MONVARS     EQU  JLAST_ENTRY-192
OFFSET_OFF  EQU  0               ; 32 byte, for disassembler usage
FLAG        EQU  OFFSET_OFF+32   ; 2 byte, 16-bit monitor flag
BUFFER      EQU  FLAG+2          ; 80 byte
POINTER_NOW EQU  BUFFER+80       ; 4 byte
USER_DATA   EQU  POINTER_NOW+4   ; 32 byte, user D0-D7
USER_ADDR   EQU  USER_DATA+32    ; 28 byte, user A0-A6
USER_USP    EQU  USER_ADDR+28    ; 4 byte, A7 = USP
USER_SR     EQU  USER_USP+4      ; 2 byte
USER_SS     EQU  USER_SR+2       ; 4 byte
USER_PC     EQU  USER_SS+4       ; 4 byte
OFFSET      EQU  MONVARS+OFFSET_OFF

; Monitor's stack
SUPER_STACK EQU MONVARS-4	        ; top of supervisor stack, monitor worst-case stack usage is about 40-50 bytes
USER_STACK  EQU SUPER_STACK-80   ; top of user stack

; status register values
INT_ON   EQU  $2000    ; BOTH, SET SUPERVISOR MODE, S=1
INT_OFF  EQU  $2700
SUPERVISOR_BIT EQU 5
TRACE_BIT EQU 7

; serial communication
RDF    EQU 0
TXE    EQU 1

CR      EQU 13
LF      EQU 10
SP      EQU 32
BS      EQU 8
RS      EQU $1E
ESC     EQU $1B
BIT_ESC      EQU 0              ; ESC BIT POSITION #0

MAIN    EQU 0
UTIL    EQU 1

   SECTION MAIN
   ORG LOADADDR               
   
; ROM Exception vector table
; When running from RAM, this is just wasted space

   BRA SZERO               ; 4 bytes, if executing from RAMBASE. This is also the stack pointer value after reset
   dc.l SRESET
   dc.l JBUS_ERR, JADDR_ERR, JILLEGAL, JZERO_DIV, JCHK, JTRAPV, JPRIV_VIOL, JTRACE, JLINE_A, JLINE_F

   ORG LOADADDR+$64   
   dc.l JINT1, JINT2, JINT3, JINT4, JINT5, JINT6, JINT7
   dc.l JTRAP0, JTRAP1, JTRAP2, JTRAP3, JTRAP4, JTRAP5, JTRAP6, JTRAP7, JTRAP8, JTRAP9, JTRAPA, JTRAPB, JTRAPC, JTRAPD, JTRAPE, JTRAPF 
   ; end of exception vector table

   ORG LOADADDR+$400

SZERO:
      MOVE.W #INT_OFF,SR  ; INTERRUPT OFF, SUPERVISOR MODE SET
	  MOVEA.L #DOUT,A1
	  MOVEA.L #SEROUT,A2
LOOP:
	MOVE.B #0, A1
	MOVE.B #'0', A2
	MOVE.B #1, A1
	MOVE.B #'1', A2
	JMP LOOP
	

