*************************************************************************************************
*************************************************************************************************
////////////////////////////                                        /////////////////////////////
***************************FUNCTIONAL SIMULATOR FOR RISC-V[PHASE II]*****************************
///////////////////////////                                         /////////////////////////////
*************************************************************************************************
*************************************************************************************************


TEAM MEMBERS:-

-> Name: Chiranjiv Dutt
   Entry Number: 2019CSB1083

-> Name: Ganesh Aggarwal
   Entry Number: 2019CSB1085

-> Name: Gautam Manocha
   Entry Number: 2019CSB1086

-> Name: Shobit Prashant Nair
   Entry Number: 2019CSB1121

-> Name: Vanshal Singh
   Entry Number: 2019CSB1129

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
-> python RISC-V_Simulator_Group_4_Phase_2.py (to run the program)
-> A screen will open on your pc which will have 4 buttons on top left 
namely:Assemble,step,cycle-step,Run.
-> There will even be a drop down menu on bottom right of screen
-> Choose the type of pipelining you want to run the code before pressing anything else.
-> To run the code firstly click the Assemble button. The code will take up the input.
-> In order to run one cycle at a time click on the 'Cycle-Step' button
-> To run one step click on the 'Step' button. 
-> In order to run the whole code in one go at any time click 'Run' button

=================================================================
2. Input format with details
-> All the instructions in the .mc file which is to be run should be 
in the little endian notation and the way it was mentioned in the file.
-> At the end of machine code the last PC should be set to '0xffffc'
-> Then to give the memory as input use the same format as mentioned in file.
=================================================================
3. Output format with details
-> PC of the instruction that just fetched , decode etc. would be displayed.
-> All the other data like CPI etc. as required would be displayed at the end of code.
-> Memory updated would be shown in a window on the right but it won't be byte-wise but rather word-wise.
-> Registers values will also be updated in a window on the right.
-> Furthermore, there are drop down menus at the bottom of registers and memory to change
the data type in which the values need to be displayed.
-> There is even an output window which keeps on getting updated with whatever is happening in the code.

=================================================================
4. How to run

-> Firstly make a file in the same directory as of the code and name it as file.mc 
which should contain the machine code and data file.
-> python RISC-V_Simulator_Group_4_Phase_2.py (to run the program)
-> Consequently the instructions to further proceed in the program are displayed 

=================================================================
5. List of any libraries to compile and run it

(A) PyQt5
(B) sys

=================================================================
6. Work split among the team members
The complete project was made using Replit which is a real time editor that allows multiple users
to work together at the same time like google docs.
All of us worked together in each of the components while being on a meet. No explicit division of work
was made.  

=================================================================
7. GUI-what all data is being displayed and how to interpret it

-> 4 buttons are displayed on the GUI: "Run", "Step" , "Assemble"
 AND "Cycle-Step"
-> If "Run" is selected, the complete code is executed and everything is displayed.
-> If "Step" is selected, you can run the code one instruction at a time.
-> If "Assemble" is selected, which needs to be done at the start of the code the input file would be read.
-> If "Cycle-Step" is selected, you can run one cycle at a time.
# Data Segment 
-> Displays all the data along with its address
-> There is a scroll button on the right of data screen to scroll it up and down
# Registers
-> Displays the values of all the 31 registers(x0-x31)
-> There is a scroll button on the right of registers screen to scroll it up and down
# OUPUT
-> Displays the output of the code like what is happening in each step of each instruction
-> There is a scroll button on the right of output screen to scroll it up and down 

------------------------------------------END------------------------------------------------------
