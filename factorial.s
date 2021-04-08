li x5 123
li x4 19
j main
fact:
    addi sp sp -16
    sw x1 0(sp)
    sw x6 4(sp)
    sw x5 8(sp)
    sw x4 12(sp)
    li x4 1 # for compare
    beq x4 x6 label
    addi x6 x6 -1
    jal x1 fact
    label:
    addi sp sp 16
    addi x5 x6 0
    lw x6 4(sp)
    lw x1 0(sp)
    mul x6 x5 x6
    lw x5 8(sp)
    lw x4 12(sp)
    jalr x0 x1 0
main:
    li x6 5
    jal x1 fact
