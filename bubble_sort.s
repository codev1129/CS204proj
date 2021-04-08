.data 
arr: .word 10 42 35 58 15 -20 -11
size: .word 7

.text
la x4 arr #address of first element
la x5 size 
lw x3 0(x5) #size of array
addi x2 x3 -1 # number of time loop need to be iterated
li x11 0 # j
li x22 2
outer_loop:
li x6 0 #index i
loop:
sll x8 x6 x22 #index*4 for address
add x7 x8 x4#addresss of ith number

lw x9 0(x7)
lw x10 4(x7)

bge x10 x9 skip 
sw x9 4(x7)
sw x10 0(x7)
skip:
addi x6 x6 1
beq x6 x2 exit
j loop
exit:
addi x11 x11 1
beq x11 x2 exit_outer_loop
j outer_loop
exit_outer_loop: