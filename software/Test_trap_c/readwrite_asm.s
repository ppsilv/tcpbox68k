	.file	"readwrite.c"
| GNU C23 (GCC) version 15.1.0 (m68k-elf)
|	compiled by GNU C version 13.3.0, GMP version 6.3.0, MPFR version 4.2.1, MPC version 1.3.1, isl version none
| GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
| options passed: -mcpu=68000 -Os
	.text
	.align	2
	.globl	outch
	.type	outch, @function
outch:
	move.l %d2,-(%sp)	|,
| readwrite.c:32:     asm volatile (
	move.b 11(%sp),%d2	| c,
#APP
| 32 "readwrite.c" 1
	movem.l %d0/%d1/%a0,-(%sp)
	move.b %d2, %d1	|
	move.w #2, %d0
	trap #1
	movem.l (%sp)+,%d0/%d1/%a0
| 0 "" 2
| readwrite.c:42: }
#NO_APP
	move.l (%sp)+,%d2	|,
	rts	
	.size	outch, .-outch
	.align	2
	.globl	read_char
	.type	read_char, @function
read_char:
| readwrite.c:47:     asm volatile (
#APP
| 47 "readwrite.c" 1
	MOVE.W #1, %D0
	TRAP #1
	MOVE.L %D0, %a0	| result
| 0 "" 2
| readwrite.c:56: }
#NO_APP
	move.w %a0,%d1	|,
	moveq #0,%d0	|
	move.b %d1,%d0	|,
	rts	
	.size	read_char, .-read_char
	.align	2
	.globl	write_char
	.type	write_char, @function
write_char:
| readwrite.c:60:     trap_param = c; // Garante que o valor não seja otimizado
	move.l 4(%sp),trap_param	| c, trap_param
| readwrite.c:61:     asm volatile (
	move.l trap_param,%a0	| trap_param, trap_param.0_1
#APP
| 61 "readwrite.c" 1
	MOVE.W #2, %D0
	MOVE.L %a0, %D1	| trap_param.0_1
	TRAP #1
| 0 "" 2
| readwrite.c:69: }
#NO_APP
	rts	
	.size	write_char, .-write_char
	.section	.text.startup,"ax",@progbits
	.align	2
	.globl	main
	.type	main, @function
main:
	subq.l #4,%sp	|,
	move.l %a3,-(%sp)	|,
	move.l %a2,-(%sp)	|,
| readwrite.c:74:     outch('A');
	pea 65.w		|
	lea outch,%a2	|, tmp33
	jsr (%a2)		| tmp33
| readwrite.c:75:     outch('A');
	pea 65.w		|
	jsr (%a2)		| tmp33
| readwrite.c:76:     outch('A');
	pea 65.w		|
	jsr (%a2)		| tmp33
| readwrite.c:77:     outch('A');
	pea 65.w		|
	jsr (%a2)		| tmp33
| readwrite.c:78:     outch('A');
	pea 65.w		|
	jsr (%a2)		| tmp33
| readwrite.c:79:     write_char('A');
	pea 65.w		|
	lea write_char,%a2	|, tmp38
	jsr (%a2)		| tmp38
| readwrite.c:80:     write_char('B');
	pea 66.w		|
	jsr (%a2)		| tmp38
| readwrite.c:81:     write_char('C');
	pea 67.w		|
	jsr (%a2)		| tmp38
| readwrite.c:82:     write_char('\n');
	lea (32,%sp),%sp	|,
	pea 10.w		|
	jsr (%a2)		| tmp38
| readwrite.c:85:     write_char('D');
	pea 68.w		|
	jsr (%a2)		| tmp38
| readwrite.c:86:     write_char('i');
	pea 105.w		|
	jsr (%a2)		| tmp38
| readwrite.c:87:     write_char('g');
	pea 103.w		|
	jsr (%a2)		| tmp38
| readwrite.c:88:     write_char('i');
	pea 105.w		|
	jsr (%a2)		| tmp38
| readwrite.c:89:     write_char('t');
	pea 116.w		|
	jsr (%a2)		| tmp38
| readwrite.c:90:     write_char('e');
	pea 101.w		|
	jsr (%a2)		| tmp38
| readwrite.c:91:     write_char(':');
	pea 58.w		|
	jsr (%a2)		| tmp38
| readwrite.c:92:     write_char(' ');
	lea (32,%sp),%sp	|,
	pea 32.w		|
	jsr (%a2)		| tmp38
	addq.l #4,%sp	|,
.L5:
| readwrite.c:96:         int c = read_char();
	jsr read_char		|
| readwrite.c:97:         write_char('\n');
	pea 10.w		|
	move.l %d0,12(%sp)	|,
	jsr (%a2)		| tmp64
| readwrite.c:98:         write_char('R');
	pea 82.w		|
	jsr (%a2)		| tmp64
| readwrite.c:99:         write_char('e');
	pea 101.w		|
	jsr (%a2)		| tmp64
| readwrite.c:100:         write_char('c');
	pea 99.w		|
	jsr (%a2)		| tmp64
| readwrite.c:101:         write_char('e');
	pea 101.w		|
	jsr (%a2)		| tmp64
| readwrite.c:102:         write_char('b');
	pea 98.w		|
	jsr (%a2)		| tmp64
| readwrite.c:103:         write_char('i');
	pea 105.w		|
	jsr (%a2)		| tmp64
| readwrite.c:104:         write_char(':');
	pea 58.w		|
	jsr (%a2)		| tmp64
| readwrite.c:105:         write_char(' ');
	lea (32,%sp),%sp	|,
	pea 32.w		|
	jsr (%a2)		| tmp64
| readwrite.c:106:         write_char(c);
	move.l 12(%sp),-(%sp)	|,
	jsr (%a2)		| tmp64
| readwrite.c:107:         write_char('\n');
	pea 10.w		|
	jsr (%a2)		| tmp64
| readwrite.c:108:         write_char(':');
	pea 58.w		|
	jsr (%a2)		| tmp64
| readwrite.c:109:         write_char(' ');
	pea 32.w		|
	jsr (%a2)		| tmp64
	lea (20,%sp),%sp	|,
	jra .L5		|
	.size	main, .-main
	.text
	.align	2
	.globl	_start
	.type	_start, @function
_start:
| readwrite.c:15:     main();
	jsr main		|
	.size	_start, .-_start
	.globl	trap_param
	.section	.bss
	.align	2
	.type	trap_param, @object
	.size	trap_param, 4
trap_param:
	.zero	4
	.globl	trap_result
	.align	2
	.type	trap_result, @object
	.size	trap_result, 4
trap_result:
	.zero	4
	.ident	"GCC: (GNU) 15.1.0"
