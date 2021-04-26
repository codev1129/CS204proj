================================================
Functional Simulator for RISCV Processor
================================================
TEAM MEMBERS:
1) Gautam Manocha - 2019CSB1086
2) Chiranjiv Dutt - 2019CSB1083
3) Ganesh Aggarwal - 2019CSB1085
4) Vanshal Singh - 2019CSB1129
5) Shobit Nair - 2019CSB1121

README

Table of contents
1. Instructions to the user on how to use it
2. Input format with details
3. Output format with details
4. How to run
5. List of any libraries to compile and run it.
6. Work split among the team members 
7. GUI-what all data is being displayed and how to interpret it.

=================================================================
1. Instructions to the user on how to use it
-> python RISC-V_Simulator_Group_4.py (to run the program)
-> A screen will open on your pc which will show 2 active buttons 
namely, 'Press to get the machine code' and 'End and Close Program'
-> To run the code firstly click the 'Press to get the machine code' 
button then 2 more buttons will become active namely, 'Step' and 'Run'
-> In order to run one instruction at a time click on the 'Step' button 
-> If you want to restart the simulation click 'Press to get the machine 
code' button
-> In order to run the whole code in one go click 'Run' button

=================================================================
2. Input format with details
-> All the instructions in the .mc file which is to be run should be 
in the little endian notation and the way it was mentioned in the file.
-> At the end of machine code the last PC should be set to '0xffffc'
-> Then to give the memory as input use the same format as mentioned in file.
=================================================================
3. Output format with details
-> All the elements are updated in the data segment would be added in the .mc
file given in the input
-> PC, Cycle Count, IR, values of the registers(x0-x31),memory are displayed on the 
on the GUI.
-> Furthermore, there are drop down menus at the side of registers and memory to change
the data type in which the values need to be displayed.

=================================================================
4. How to run

-> Firstly make a file in the same directory as of the code and name it as file.mc 
which should contain the machine code and data file.
-> python RISC-V_Simulator_Group_4.py (to run the program)
-> Consequently the instructions to further proceed in the program are displayed 

=================================================================
5. List of any libraries to compile and run it
(A) tkinter
(B) sys

=================================================================
6. Work split among the team members
The complete project was made using Replit which is a real time editor that allows multiple users
to work together at the same time like google docs.
All of us worked together in each of the components while being on a meet. No explicit division of work
was made.  

=================================================================
7. GUI-what all data is being displayed and how to interpret it

-> 4 buttons are displayed on the GUI: "RUN", "STEP" , "END AND CLOSE PROGRAM"
 AND "PRESS TO GET THE MACHINE CODE"
-> If "RUN" is selected, the complete code is executed and Clock Cycle Count and PC and IR and OUTPUT
are displayed.
-> If "STEP" is selected, you can run the code one instruction at a time and PC, 
Clock Cycle Count, IR and OUTPUT are displayed at every step.
-> If "PRESS TO GET THE MACHINE CODE" is selected, every data displayed is reset to its initial value as in the beginning
of the code.
-> If "END AND CLOSE PROGRAM" is selected, the code ends and the screen vanishes
# Instruction Segment
-> Displays all the instructions along with their addresses and further highlights the current instruction to be executed
# Data Segment 
-> Displays all the data along with its address
-> There is a scroll button on the right of data screen to scroll it up and down
# Registers
-> Displays the values of all the 31 registers(x0-x31)
-> There is a scroll button on the right of registers screen to scroll it up and down
# OUPUT
-> Displays the output of the code like what is happening in each step of each instruction
-> There is a scroll button on the right of output screen to scroll it up and down 
=================================================================
8. Error in Machine Code

-> If any such machine code is passed which is invalid or was not asked to provide support for  the code will terminate 
with an error message displaying on the screen.

------------------------------------------END------------------------------------------------------
