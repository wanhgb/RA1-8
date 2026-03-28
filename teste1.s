@ HENRY GAYER BRUSCHINI WAN
@ GRUPO
    .arch   armv7-a
    .fpu    vfpv3-d16
    .syntax unified

    .section .rodata
    .align  3

    E0:   .word 0x51EB851F, 0x40091EB8   @ 3.14
    E1:   .word 0x9999999A, 0x3FD99999   @ 0.4
    E2:   .word 0x00000000, 0x40240000   @ 10.0
    E3:   .word 0x00000000, 0x40140000   @ 5.0
    E4:   .word 0x00000000, 0x40200000   @ 8.0
    E5:   .word 0x00000000, 0x40000000   @ 2.0
    E6:   .word 0x00000000, 0x40080000   @ 3.0
    E7:   .word 0x00000000, 0x3FF00000   @ 1.0
    E8:   .word 0x00000000, 0x40340000   @ 20.0
    E9:   .word 0x00000000, 0x40100000   @ 4.0
    E10:   .word 0x00000000, 0x401C0000   @ 7.0
    E11:   .word 0x00000000, 0x40180000   @ 6.0
    E12:   .word 0x00000000, 0x40220000   @ 9.0

hex_table:
    .byte 0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07
    .byte 0x7F,0x6F,0x77,0x7C,0x39,0x5E,0x79,0x71


    .section .data
    .align  3
pilha_topo:
    .word   0
    .align  3
pilha_mem:
    .fill   256, 1, 0
    .align  3
VAR_DATA:
    .fill   16, 1, 0
    .align  3
resultados_mem:
    .fill   80, 1, 0


    .section .text
    .global _start

_start:
    LDR     sp, =0x00080000 
    PUSH    {r4, r5, r6, r7, r8, lr}
    LDR     r0, =pilha_topo
    MOV     r1, #0
    STR     r1, [r0]


    @ === expressao 1 ============================================

    @ push 3.14
    LDR     r4, =E0
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 0.4
    LDR     r4, =E1
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 1: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_1:
    LDR     r2, =1000000
espera_int_1:
    SUBS    r2, r2, #1
    BNE     espera_int_1
    SUBS    r1, r1, #1
    BNE     espera_ext_1

    @ === expressao 2 ============================================

    @ push 10
    LDR     r4, =E2
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 5
    LDR     r4, =E3
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ push 8
    LDR     r4, =E4
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '/'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VDIV.F64 D0, D0, D1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 2: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #8
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_2:
    LDR     r2, =1000000
espera_int_2:
    SUBS    r2, r2, #1
    BNE     espera_int_2
    SUBS    r1, r1, #1
    BNE     espera_ext_2

    @ === expressao 3 ============================================

    @ push 5
    LDR     r4, =E3
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '^'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    BL      pow_sub       @ D0 = A elevado a B
    BL      pilha_push

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 1
    LDR     r4, =E7
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 3: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #16
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_3:
    LDR     r2, =1000000
espera_int_3:
    SUBS    r2, r2, #1
    BNE     espera_int_3
    SUBS    r1, r1, #1
    BNE     espera_ext_3

    @ === expressao 4 ============================================

    @ push 20
    LDR     r4, =E8
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '%'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    BL      divmod_sub    @ resultado: D2 = resto
    FMRRD   r0, r1, D2
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 4
    LDR     r4, =E9
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 4: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #24
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_4:
    LDR     r2, =1000000
espera_int_4:
    SUBS    r2, r2, #1
    BNE     espera_int_4
    SUBS    r1, r1, #1
    BNE     espera_ext_4

    @ === expressao 5 ============================================

    @ push 7
    LDR     r4, =E10
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ push 1
    LDR     r4, =E7
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ grava topo da pilha na variavel MEMORIA
    LDR     r4, =pilha_topo
    LDR     r5, [r4]
    SUB     r5, r5, #1
    LDR     r4, =pilha_mem
    ADD     r4, r4, r5, LSL #3
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    LDR     r4, =VAR_DATA
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 5: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #32
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_5:
    LDR     r2, =1000000
espera_int_5:
    SUBS    r2, r2, #1
    BNE     espera_int_5
    SUBS    r1, r1, #1
    BNE     espera_ext_5

    @ === expressao 6 ============================================

    @ push 4
    LDR     r4, =E9
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 5
    LDR     r4, =E3
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ push 10.0
    LDR     r4, =E2
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 6: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #40
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_6:
    LDR     r2, =1000000
espera_int_6:
    SUBS    r2, r2, #1
    BNE     espera_int_6
    SUBS    r1, r1, #1
    BNE     espera_ext_6

    @ === expressao 7 ============================================

    @ push 6
    LDR     r4, =E11
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '/'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VDIV.F64 D0, D0, D1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ grava topo da pilha na variavel MEM
    LDR     r4, =pilha_topo
    LDR     r5, [r4]
    SUB     r5, r5, #1
    LDR     r4, =pilha_mem
    ADD     r4, r4, r5, LSL #3
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    LDR     r4, =VAR_DATA
    ADD     r4, r4, #8
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 7: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #48
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_7:
    LDR     r2, =1000000
espera_int_7:
    SUBS    r2, r2, #1
    BNE     espera_int_7
    SUBS    r1, r1, #1
    BNE     espera_ext_7

    @ === expressao 8 ============================================

    @ push 9
    LDR     r4, =E12
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '-'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VSUB.F64 D0, D0, D1
    BL      pilha_push

    @ le variavel MEM da memoria
    LDR     r4, =VAR_DATA
    ADD     r4, r4, #8
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '*'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VMUL.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 8: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #56
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_8:
    LDR     r2, =1000000
espera_int_8:
    SUBS    r2, r2, #1
    BNE     espera_int_8
    SUBS    r1, r1, #1
    BNE     espera_ext_8

    @ === expressao 9 ============================================

    @ push 2
    LDR     r4, =E5
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '^'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    BL      pow_sub       @ D0 = A elevado a B
    BL      pilha_push

    @ le variavel MEM da memoria
    LDR     r4, =VAR_DATA
    ADD     r4, r4, #8
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '+'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    VADD.F64 D0, D0, D1
    BL      pilha_push

    @ fim expressao 9: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #64
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_9:
    LDR     r2, =1000000
espera_int_9:
    SUBS    r2, r2, #1
    BNE     espera_int_9
    SUBS    r1, r1, #1
    BNE     espera_ext_9

    @ === expressao 10 ============================================

    @ push 3
    LDR     r4, =E6
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ push 9
    LDR     r4, =E12
    LDR     r0, [r4]
    LDR     r1, [r4, #4]
    FMDRR   D0, r0, r1
    BL      pilha_push

    @ operador '//'
    BL      pilha_pop        @ D0 = B (operando direito)
    FMRRD   r0, r1, D0
    FMDRR   D1, r0, r1
    BL      pilha_pop        @ D0 = A (operando esquerdo)
    BL      divmod_sub    @ resultado: D0 = quociente
    BL      pilha_push

    @ fim expressao 10: salva resultado e mostra no display
    BL      pilha_pop
    LDR     r4, =resultados_mem
    ADD     r4, r4, #72
    FMRRD   r0, r1, D0
    STR     r0, [r4]
    STR     r1, [r4, #4]
    VCVT.S32.F64  S0, D0    @ converte double para inteiro
    VMOV    r0, S0
    BL      print_dec
    MOV     r1, #50
espera_ext_10:
    LDR     r2, =1000000
espera_int_10:
    SUBS    r2, r2, #1
    BNE     espera_int_10
    SUBS    r1, r1, #1
    BNE     espera_ext_10

    @ todos os resultados estao em resultados_mem
    POP     {r4, r5, r6, r7, r8, lr}
fim:
    B       fim

@ pilha_push: empilha D0 no topo da pilha de doubles
pilha_push:
    PUSH    {r0, r1, r4, r5, lr}
    LDR     r4, =pilha_topo
    LDR     r5, [r4]              @ r5 = indice do topo
    LDR     r4, =pilha_mem
    ADD     r4, r4, r5, LSL #3    @ r4 = &pilha_mem[topo]
    FMRRD   r0, r1, D0            @ extrai os 64 bits de D0 em r0:r1
    STR     r0, [r4]              @ grava word low
    STR     r1, [r4, #4]          @ grava word high
    LDR     r4, =pilha_topo
    ADD     r5, r5, #1
    STR     r5, [r4]              @ incrementa topo
    POP     {r0, r1, r4, r5, pc}

@ pilha_pop: desempilha topo para D0
pilha_pop:
    PUSH    {r0, r1, r4, r5, lr}
    LDR     r4, =pilha_topo
    LDR     r5, [r4]
    SUB     r5, r5, #1            @ decrementa topo
    STR     r5, [r4]
    LDR     r4, =pilha_mem
    ADD     r4, r4, r5, LSL #3
    LDR     r0, [r4]              @ le word low
    LDR     r1, [r4, #4]          @ le word high
    FMDRR   D0, r0, r1            @ reconstroi D0 a partir de r0:r1
    POP     {r0, r1, r4, r5, pc}

@ divmod_sub: recebe D0=A e D1=B, retorna D0=quociente e D2=resto
divmod_sub:
    PUSH    {r4, r5, r6, r7, lr}
    VCVT.S32.F64  S0, D0
    VCVT.S32.F64  S2, D1
    VMOV    r4, S0               @ r4 = parte inteira de A
    VMOV    r5, S2               @ r5 = parte inteira de B
    MOV     r6, #0               @ r6 = quociente
    CMP     r5, #0
    BEQ     divisao_por_zero
loop_divisao:
    CMP     r4, r5
    BLT     fim_divisao
    SUB     r4, r4, r5
    ADD     r6, r6, #1
    B       loop_divisao
fim_divisao:
    VMOV    S8,  r6
    VCVT.F64.S32  D0, S8         @ D0 = quociente como double
    VMOV    S10, r4
    VCVT.F64.S32  D2, S10        @ D2 = resto como double
    POP     {r4, r5, r6, r7, pc}
divisao_por_zero:
    MOV     r6, #0
    MOV     r4, #0
    B       fim_divisao

@ pow_sub: recebe D0=base e D1=expoente, retorna D0=resultado
@ funciona apenas com expoentes inteiros nao negativos
pow_sub:
    PUSH    {r4, r5, r6, lr}
    VCVT.S32.F64  S0, D0
    VCVT.S32.F64  S2, D1
    VMOV    r4, S0               @ r4 = base
    VMOV    r5, S2               @ r5 = expoente
    @ valida: expoente deve ser inteiro nao negativo
    CMP     r5, #0
    BMI     expoente_invalido     @ negativo: erro
    MOV     r6, #1               @ r6 = resultado (comeca em 1)
    CMP     r5, #0
    BEQ     fim_potencia
loop_potencia:
    MUL     r6, r6, r4
    SUBS    r5, r5, #1
    BGT     loop_potencia
fim_potencia:
    VMOV    S8, r6
    VCVT.F64.S32  D0, S8
    POP     {r4, r5, r6, pc}
expoente_invalido:
    @ expoente negativo: retorna 0.0 como indicador de erro
    MOV     r6, #0
    B       fim_potencia

@ --- apresentação no display ---@ print_dec: exibe r0 como numero decimal nos displays HEX3-HEX0
@ extrai cada digito com divisao por 10 via subtracao
print_dec:
    PUSH    {r1, r2, r3, r4, r5, r6, r7, lr}
    LDR     r1, =0xFF200020
    LDR     r2, =hex_table
    MOV     r3, #0               @ word que sera gravado no display
    MOV     r4, #0               @ deslocamento em bits (0, 8, 16, 24)
    MOV     r7, #4               @ 4 digitos
loop_display:
    CMP     r7, #0
    BEQ     fim_display
    MOV     r5, #0               @ r5 = quociente
    MOV     r6, r0               @ r6 = valor atual
divide_por_10:
    CMP     r6, #10
    BLT     pega_digito
    SUB     r6, r6, #10
    ADD     r5, r5, #1
    B       divide_por_10
pega_digito:
    LDRB    r6, [r2, r6]         @ r6 = segmentos do digito
    ORR     r3, r3, r6, LSL r4
    ADD     r4, r4, #8
    MOV     r0, r5               @ proximo digito
    SUB     r7, r7, #1
    B       loop_display
fim_display:
    STR     r3, [r1]
    POP     {r1, r2, r3, r4, r5, r6, r7, pc}

