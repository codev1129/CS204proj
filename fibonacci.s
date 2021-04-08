j main
fibo:
	addi sp sp -8
    sw x6 0(sp)
    sw x7 4(sp)
    li x6 0
    li x7 1
    bne x5 x0 skip
    li x10 0
    jalr x0 x1 0
    skip:
    bne x5 x7 skip_1
    li x10 1
    jalr x0 x1 0
    skip_1:
    li x8 2 # counter
    loop:
    	add x7 x7 x6
        sub x6 x7 x6
        bne x8 x5 s
        add x10 x0 x7
        addi sp sp 8
        lw x7 4(sp)
        lw x6 0(sp)
        jalr x0 x1 0
        s:
    	addi x8 x8 1
        j loop
        
main:    
	li x5 11
    jal x1 fibo
