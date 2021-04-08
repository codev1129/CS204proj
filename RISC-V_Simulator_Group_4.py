from tkinter import *

from sys import exit

def srl(s1,s2):
    # s1 , s2 in int
    if (s1>=0):
        return s1>>s2
    temp=bin(s1)[3:]
    temp='0'*(32-len(temp))+temp # 32 bit positive of the number
    temp1='0b'
    for i in temp:
        temp1+=str(1^int(i))
    temp1=int(temp1,2)+1
    return temp1>>s2


def two_compliment(s):
    temp='0b'
    for i in s:
        temp+=str(1^int(i))
    
    return -1*(int(temp,2)+1)
    
def init_registers():
    global registers
    registers = [0]*32
    registers[2]= 0x7ffffff0
    registers[3]= 0x10000000
    
def init(file_name,delimit):
    file = open(file_name,"r")
    instructions = file.readlines()
    init_registers()    
    
    global var
    global control
    global dict_data
    global dict_instructions
    
    
    var = {'ir_final':0,'pctemp':'0x0','pc':'0x0','ir':0,'alu2':0,'alu1':0,'mar':0,'mdr':0,'rm':0,'ry':0,'rz':0,'rs1':0,'rs2':0,'rd':0,'imm':0}
    control = {'type':'X','operation':'xxx'}
    dict_data={}
    dict_instructions={}
    
    delimiter = 0
    for i in instructions:
        if i[len(i)-1]=='\n':
            i = i[:len(i)-1]
        if i == delimit:
            delimiter = 1
            continue
        if delimiter:
            temp = i.split()
            dict_data[temp[0].lower()] = temp[1]
        else:
            temp = i.split()
            dict_instructions[temp[0]] = bin(int(temp[1],16))
    
def fetch():
    
    var['ir'] = dict_instructions[var['pc']][2:]
    var['ir'] = '0b'+(32-len(var['ir']))*'0'+var['ir']
    var['ir_final'] = var['ir']
    # print(var['ir'])
    var['pctemp'] = hex(int(var['pc'],16)+4)
    
    
    


def decode():
    
    
    global output_frame
    
    opcode = hex(int('0b'+var['ir'][len(var['ir'])-7:],2))
    var['ir']=var['ir'][:len(var['ir'])-7]
    if (opcode=='0x33'):
        # add and or sll slt sra srl sub xor mul div rem
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['rs2'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        func7 = hex(int('0b'+var['ir'][len(var['ir'])-7:],2))
        var['ir']=var['ir'][:len(var['ir'])-7]

        var['alu1']= registers[int(var['rs1'],16)]
        var['alu2']= registers[int(var['rs2'],16)]

        control['type']='R'
        if func3=='0x0':
            if func7=='0x0':
                control['operation']='+'
            elif func7=='0x1':
                control['operation']='*'
            elif func7=='0x20':
                control['operation']='-'
        if func3=='0x4':
            if func7=='0x0':
                control['operation']='^'
            elif func7=='0x1':
                control['operation']='/'
        if func3=='0x6':
            if func7=='0x0':
                control['operation']='|'
            elif func7=='0x1':
                control['operation']='%'
        if func3=='0x7':
            if func7=='0x0':
                control['operation']='&'
        if func3=='0x5':
            if func7=='0x0':
                control['operation']='>>>'
            elif func7=='0x20':
                control['operation']='>>'
        if func3=='0x1' and func7=='0x0':
            control['operation']='<<'
        if func3=='0x2' and func7=='0x0':
            control['operation']='<'
        
    
    elif (opcode=='0x13'):
        #addi andi ori
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-12:]
        var['ir']=var['ir'][:len(var['ir'])-12]
        
        var['alu1']= registers[int(var['rs1'],16)]
        
        control['type']='I'
        if func3=='0x0':
            control['operation']='+'
        if func3=='0x7':
            control['operation']='&'
        if func3=='0x6':
            control['operation']='|'
        
            
    elif (opcode=='0x3'):
        # lb lh lw
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-12:]
        var['ir']=var['ir'][:len(var['ir'])-12]
        
        var['alu1']= registers[int(var['rs1'],16)]
        
        control['type']='I'
        if func3=='0x0':
            control['operation']='lb'
        if func3=='0x1':
            control['operation']='lh'
        if func3=='0x2':
            control['operation']='lw'
        
        
    elif (opcode=='0x67'):
        # jalr
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-12:]
        var['ir']=var['ir'][:len(var['ir'])-12]
        
        var['alu1']= registers[int(var['rs1'],16)]
        
        control['type']='I'
        control['operation']='jalr'
        
        
    elif (opcode=='0x23'):
        # sb sw sh
        temp = var['ir'][len(var['ir'])-5:]
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['rs2'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-7:]+temp
        var['ir']=var['ir'][:len(var['ir'])-7]
        
        var['alu1']= registers[int(var['rs1'],16)]
        
        control['type']='S'
        if func3=='0x0':
            control['operation']='sb'
        if func3=='0x1':
            control['operation']='sh'
        if func3=='0x2':
            control['operation']='sw'
        
        
    elif (opcode=='0x63'):
        # beq bne bge blt
        temp = var['ir'][len(var['ir'])-5:]
        var['ir']=var['ir'][:len(var['ir'])-5]
        func3 = hex(int('0b'+var['ir'][len(var['ir'])-3:],2))
        var['ir']=var['ir'][:len(var['ir'])-3]
        var['rs1'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['rs2'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        temp1 = var['ir'][len(var['ir'])-7]
        var['ir']=var['ir'][:len(var['ir'])-7]
        
        var['imm']='0b'+temp1[0]+temp[4]+temp1[1:]+temp[:4]+'0'
        
        var['alu2']= registers[int(var['rs2'],16)]
        var['alu1']= registers[int(var['rs1'],16)]
        
        control['type']='SB'
        if func3=='0x0':
            control['operation']='=='
        if func3=='0x1':
            control['operation']='!='
        if func3=='0x5':
            control['operation']='>='
        if func3=='0x4':
            control['operation']='<'
        
            
    elif (opcode=='0x17'):
        # auipc
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-20:]+'0'*12
        var['ir']=var['ir'][:len(var['ir'])-20]
        
        control['type']='U'
        control['operation']='auipc'
        
        
    elif (opcode=='0x37'):
        # lui
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]
        var['imm'] = '0b'+var['ir'][len(var['ir'])-20:]+'0'*12
        var['ir']=var['ir'][:len(var['ir'])-20]
        
        control['type']='U'
        control['operation']='lui'
        
        
    elif (opcode=='0x6f'):
        # jal
        var['rd'] = hex(int('0b'+var['ir'][len(var['ir'])-5:],2))
        var['ir']=var['ir'][:len(var['ir'])-5]

        temp = var['ir'][2:]
        var['ir']=var['ir'][:2] 
        var['imm']='0b'+temp[0]+temp[12:]+temp[11]+temp[1:11]+'0'
        
        control['type']='UJ'
        control['operation']='jal'
        
    else:
        
        output_frame.insert(END,"Given OP-Code is invalid so exiting......")
        return 1
    
    
    if type(var['imm'])==str and len(var['imm'])>2:
        if var['imm'][:3]=='0b1':
            var['imm']=two_compliment(var['imm'][2:])
        else:
            var['imm']=int(var['imm'],2)
    return 0
    
def execute():
    
    
    global output_frame
    
    var['mar']='error'
    var['ry']='error'
    if control['type']=='R':
        if control['operation']!='>>>':
            var['rz'] = int(eval(str(var['alu1'])+control['operation']+str(var['alu2'])))
        else:
            var['rz'] = srl(var['alu1'],var['alu2'])
        var['pc']= var['pctemp']
    # R type done
    if control['type']=='I':
        if control['operation'][0]!='l' and control['operation'][0]!='j': # addi andi ori
            var['rz']= eval(str(var['alu1'])+control['operation']+str(var['imm']))
            var['mar']= 'error'
            var['pc']= var['pctemp']
            
        if control['operation'][0]=='l': # lb lh lw
            
            temp= var['alu1']+var['imm']
            # print("temp",hex(temp),"-----------------")
            if (temp>=0):
                temp= hex(temp)[2:]
                var['mar']= '0x'+(8-len(temp))*'0'+temp
            else:
                temp= bin(temp)[3:]
                temp1=''
                for i in temp:
                    temp1+=str(1^int(i))
                    
                temp='0b'+'1'*(32-len(temp1))+temp1
                var['mar']= hex(int(temp,2)+1) 
                
            var['pc']= var['pctemp']
            
        if control['operation'][0]=='j': # jalr
            var['pc']= hex(var['alu1']+var['imm'])
            var['mar']= 'error'
            
    if control['type']=='S': # sb sh sw
        var['rz']= var['alu1']+var['imm']
        
        var['pc']= var['pctemp']
        temp= var['rz']
        if (temp>=0):
            temp= hex(temp)[2:]
            var['mar']= '0x'+(8-len(temp))*'0'+temp
        else:
            temp= bin(temp)[3:]
            temp1=''
            for i in temp:
                temp1+=str(1^int(i))
                
            temp='0b'+'1'*(32-len(temp1))+temp1
            var['mar']= hex(int(temp,2)+1) 
        
        temp= registers[int(var['rs2'],16)]
        if (temp>=0):
            temp= hex(temp)[2:]
            var['mdr']= '0x'+(8-len(temp))*'0'+temp
        else:
            temp= bin(temp)[3:]
            temp1=''
            for i in temp:
                temp1+=str(1^int(i))
                
            temp='0b'+'1'*(32-len(temp1))+temp1
            var['mdr']= hex(int(temp,2)+1) 
        
    if control['type']=='U': # lui auipc
        # var['imm']+=(1<<32)
        var['rz']= (var['imm'] if control['operation']=='lui' else var['imm']+int(var['pc'],16))
        
        var['pc']= var['pctemp']
    
    if control['type']=='SB': #beq bne blt bge
        if eval(str(var['alu1'])+control['operation']+str(var['alu2'])):
            var['pc']=hex(int(var['pc'],16)+var['imm'])
        else:
            var['pc']= var['pctemp']

    if control['type']=='UJ': # jal
        var['pc']= hex(int(var['pc'],16)+var['imm'])

def memory_read_write():
    
    
    if control['type']=='R':
        var['ry']= var['rz']
        
    if control['type']=='I':
        if control['operation'][0]!='l' or control['operation'][0]!='j':
            var['ry']= var['rz']
        if control['operation']=='lb':
            var['ry']= dict_data.get(var['mar'],'0x00')
            var['ry']='0x'+var['ry'][2]*6+var['ry'][2:]
        if control['operation']=='lh':
            var['ry']='0x'
            for i in range(1,-1,-1):
                temp= dict_data.get(hex(int(var['mar'],16)+i),'0x00')[2:]
                if (len(temp)<2):
                    temp=('0'+temp if int('0x'+temp,16)<8 else 'f'+temp)
                var['ry']+= temp
            var['ry']='0x'+var['ry'][2]*4+var['ry'][2:]
        if control['operation']=='lw':
            var['ry']='0x'
            for i in range(3,-1,-1):
                temp= dict_data.get(hex(int(var['mar'],16)+i),'0x00')[2:]
                if (len(temp)<2):
                    temp=('0'+temp if int('0x'+temp,16)<8 else 'f'+temp)
                var['ry']+= temp
            # print(var['ry'],var['mar'])
            # print("==================")
            
        
        if control['operation'][0]=='j':
            var['ry']= var['pctemp']
    
    if control['type']== 'S':
        if control['operation']=='sb':
            var['mdr']='0x'+var['mdr'][len(var['mdr'])-2:]
            dict_data[var['mar']]= var['mdr']
        if control['operation']=='sh':
            var['mdr']=var['mdr'][len(var['mdr'])-4:]
            for i in range(2):
                dict_data[hex(int(var['mar'],16)+(1-i))]= '0x'+var['mdr'][i*2:(i+1)*2]
        if control['operation']=='sw':
            var['mdr']=var['mdr'][len(var['mdr'])-8:]
            # print("mar",var['mar'],"mdr",var['mdr'],"==============")
            for i in range(4):
                dict_data[hex(int(var['mar'],16)+(3-i))]= '0x'+var['mdr'][i*2:(i+1)*2]
            
    if control['type']== 'U':
        var['ry']= var['rz']
    
    if control['type']== 'UJ':
        var['ry']= var['pctemp']
        
    if type(var['ry'])==str and var['ry']!='error':
        temp= bin(int(var['ry'],16))
        if len(temp)==34:
            var['ry']=two_compliment(temp[2:])
        else:
            var['ry']= int(var['ry'],16)
            
def write_back():
    
    if var['ry']!='error':
        registers[int(var['rd'],16)]= var['ry']




def run_all():
    while(var['pc'] in dict_instructions):
        run_next(1)
    show_registers()
    show_memory()
    for i in dict_instructions.keys():
            t=int(i,16)//4
            q=hex(int(dict_instructions[i],2))
            
            machinecode[t]= Label(myframe,text=i+" :  "+"0X"+"0"*(8-len(q[2:]))+q[2:],bg='white',fg='black')
            
            machinecode[t].grid(row=2+t,column=0)
    global run
    global step
    run = Button(root,text="Run",padx=20,pady=10,command=run_all,state= DISABLED).grid(row=1,column=1)
    step = Button(root,text="Step",padx=20,pady=10,command=lambda:run_next(0),state= DISABLED).grid(row=1,column=0)
    init_all = Button(root,text="Press to get the machine code",padx=20,pady=10,command=initialize).grid(row=0,column=0,columnspan=2)
      
def choose_reg(selection):
    global show_type_reg
    show_type_reg=selection
    show_registers()    

def choose_mem(selection):
    global show_type_mem
    show_type_mem=selection
    show_memory()   


def initialize():
    init("file.mc","0xffffc")
    
    global step
    global run
    global reg_buttons
    global clock
    
    clock=0
    step = Button(root,text="Step",padx=20,pady=10,command=lambda:run_next(0)).grid(row=1,column=0)
    run = Button(root,text="Run",padx=20,pady=10,command=run_all).grid(row=1,column=1)
    reg= Button(root,text="")
    
    global show_type_reg
    global a
    global option_reg
    label_reg = Label(root,text="Choose the data type").grid(row=0,column=5)
    show_type_reg='decimal' 
    show_registers()
    a = StringVar(root)
    a.set(show_type_reg)
    option_reg= OptionMenu(root,a,'decimal','unsigned','hex',command=choose_reg)
    option_reg.grid(row=1,column=5)

    global show_type_mem
    global b
    global option_mem
    label_mem = Label(root,text="Choose the data type").grid(row=104,column=5)
    show_type_mem='decimal' 
    show_memory()
    b = StringVar(root)
    b.set(show_type_mem)
    option_mem= OptionMenu(root,b,'decimal','unsigned','hex',command=choose_mem)
    option_mem.grid(row=105,column=5)
    
    global machinecode
    global myframe
    myframe= Frame(root,relief=SUNKEN,borderwidth=5)
    myframe.grid(row=0,column=6,rowspan=400)
    machinecode=[0]*len(dict_instructions.keys())
    mainlabel= Label(myframe,text="  PC  :  Machine Code").grid(row=0,column=0)
    linelabel= Label(myframe,text="_____________________").grid(row=1,column=0)
    for i in dict_instructions.keys():
            t=int(i,16)//4
            q=hex(int(dict_instructions[i],2))
            if (i==var['pc']):
                machinecode[t]= Label(myframe,text=i+" :  "+"0X"+"0"*(8-len(q[2:]))+q[2:],bg='blue',fg='white')
            else:
                machinecode[t]= Label(myframe,text=i+" :  "+"0X"+"0"*(8-len(q[2:]))+q[2:],bg='white',fg='black')
            
            machinecode[t].grid(row=2+t,column=0)
    
    global clock_label       
    clock_label = Label(root,text="Clock Cycle = "+str(clock),borderwidth=5,relief=SUNKEN,width=20).grid(row=150,column=0)
    temp=hex(int(str(var['ir_final']),2))
    
    global label1
    global scrollbar_output
    global output_frame
    label1=Label(root,text="OUTPUT",width=20).grid(row=301,column=3,pady=5)
    scrollbar_output = Scrollbar(root)
    scrollbar_output.grid(row=301,column=4,rowspan=100)
    
    output_frame = Listbox(root,yscrollcommand=scrollbar_output.set,width=50,relief=SUNKEN,borderwidth=5)
    output_frame.grid(row=302,column=3,rowspan=100)
    
    scrollbar_output.config( command = output_frame.yview )
    
    

def run_next(n):
    global root
    if (var['pc'] in dict_instructions):
        global clock
        clock+=1
        
        global clock_label       
        
        
        global output_frame
        
        fetch()
        
        
        x=decode()
        if (x==0):
            
            execute()
            memory_read_write()
            write_back()
            registers[0]=0
            output_frame.insert(END,"We have fetched the machine code with the help of PC and got the IR from the same and updated PC-TEMP")
            output_frame.insert(END,"We extracted the type of instruction and other data like names andvalues of registers and the immidiate values from the machine code")
            output_frame.insert(END,"Type of command: "+control['type']+" and operation is "+control["operation"])
            output_frame.insert(END,"We executed the extracted instruction and updated the PC and RZ/MAR/MDR")
            output_frame.insert(END,"We read/written data from/to the memory and updated the RY")
            output_frame.insert(END,"We updated the RD register as extracted from the IR")
            output_frame.insert(END,"_________________________________________________________")
        
        if n==0:
            show_registers()
            show_memory()
            clock_label = Label(root,text="Clock Cycle = "+str(clock),borderwidth=5,relief=SUNKEN,width=20).grid(row=150,column=0)
            temp = hex(int(str(var['ir_final']),2))
            labelir= Label(root,text="IR : "+"0x"+(8-len(temp[2:]))*'0'+temp[2:],relief=SUNKEN,borderwidth=5,width=20).grid(row=500,column=3)
            
            
            for i in dict_instructions.keys():
                t=int(i,16)//4
                q=hex(int(dict_instructions[i],2))
                if (i==var['pc']):
                    machinecode[t]= Label(myframe,text=i+" :  "+"0X"+"0"*(8-len(q[2:]))+q[2:],bg='blue',fg='white')
                else:
                    machinecode[t]= Label(myframe,text=i+" :  "+"0X"+"0"*(8-len(q[2:]))+q[2:],bg='white',fg='black')
                
                machinecode[t].grid(row=2+t,column=0)
        
        if (x):
            
            
            messagebox.showinfo("ERROR", "Given OP-Code is invalid so exiting......")
            root.destroy()
            
        
    else:
        global step
        global run
        run = Button(root,text="Run",padx=20,pady=10,command=run_all,state= DISABLED).grid(row=1,column=1)
        step = Button(root,text="Step",padx=20,pady=10,command=lambda:run_next(0),state= DISABLED).grid(row=1,column=0)
        init_all = Button(root,text="Press to get the machine code",padx=20,pady=10,command=initialize).grid(row=0,column=0,columnspan=2)
        
def output():       
    global label1
    global scrollbar_output
    global output_frame
    label1=Label(root,text="OUTPUT",width=20).grid(row=301,column=3,pady=5)
    scrollbar_output = Scrollbar(root)
    scrollbar_output.grid(row=301,column=4,rowspan=100)
    
    output_frame = Listbox(root,yscrollcommand=scrollbar_output.set,width=100,relief=SUNKEN,borderwidth=5)
    output_frame.grid(row=302,column=3,rowspan=100)
    
    scrollbar_output.config( command = output_frame.yview )



root = Tk() # main window
root.title("RISC-V Simulator")
root.geometry("800x700")

step = Button(root,text="Step",padx=20,pady=10,command=lambda:run_next(0),state = DISABLED).grid(row=1,column=0)
run = Button(root,text="Run",padx=20,pady=10,command=run_all,state = DISABLED).grid(row=1,column=1)
init_all = Button(root,text="Press to get the machine code",padx=20,pady=10,command=initialize).grid(row=0,column=0,columnspan=2)
end = Button(root,text="End and Close Program",padx=20,pady=10,command=root.destroy).grid(row=5,column=0,columnspan=2)




def show_registers():
    label1=Label(root,text="REGISTERS").grid(row=0,column=3,padx=5,pady=2)
    scrollbar = Scrollbar(root)
    scrollbar.grid(row=1,column=4,rowspan=100)
    
    reg_frame = Listbox(root,yscrollcommand=scrollbar.set,width=50)
    reg_frame.grid(row=1,column=3,rowspan=100)
    
    scrollbar.config( command = reg_frame.yview )
    for i in range(32):
        
        if show_type_reg=='decimal':
            reg_frame.insert(END,"Register:X"+str(i)+" : "+str(registers[i]))
        elif show_type_reg=='unsigned':
            if registers[i]<0:
                reg_frame.insert(END,"Register:X"+str(i)+" : "+str(registers[i]+(1<<32)))
            else:
                reg_frame.insert(END,"Register:X"+str(i)+" : "+str(registers[i]))
        else:
            if registers[i]<0:
                reg_frame.insert(END,"Register:X"+str(i)+" : "+hex(registers[i]+(1<<32)))
            else:
                reg_frame.insert(END,"Register:X"+str(i)+" : "+hex(registers[i]))

def hex_int(s):
    if int(s,16)>=(1<<7):
        return int(s,16)-(1<<8)
    return int(s,16)



def show_memory():
    label1=Label(root,text="MEMORY").grid(row=103,column=3,padx=5,pady=2)
    scrollbar = Scrollbar(root)
    scrollbar.grid(row=104,column=4,rowspan=100)
    
    mem_frame = Listbox(root,yscrollcommand=scrollbar.set,width=50)
    mem_frame.grid(row=104,column=3,rowspan=100)
    
    scrollbar.config( command = mem_frame.yview )
    if len(dict_data.keys()):
        temp=(int(min(dict_data.keys()),16)//4)*4
        for i in range(temp,max((int(max(dict_data.keys()),16)//4)*4+4,temp+0x100),4):
            my_str=''
            if show_type_mem=='hex':
                my_str= str(dict_data.get(hex(i),'0x00'))+" "+str(dict_data.get(hex(i+1),'0x00'))+" "+str(dict_data.get(hex(i+2),'0x00'))+" "+str(dict_data.get(hex(i+3),'0x00'))
            elif show_type_mem=='unsigned':
                my_str=str(int(dict_data.get(hex(i),'0x00'),16))+" "+str(int(dict_data.get(hex(i+1),'0x00'),16))+" "+str(int(dict_data.get(hex(i+2),'0x00'),16))+" "+str(int(dict_data.get(hex(i+3),'0x00'),16))
            else:
                my_str=str(hex_int(dict_data.get(hex(i),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+1),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+2),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+3),"0x00")))
            mem_frame.insert(END,hex(i)+" : "+my_str)
    else:
        for i in range(0x10000000,0x10000100,4):
            my_str=''
            if show_type_mem=='hex':
                my_str= str(dict_data.get(hex(i),'0x00'))+" "+str(dict_data.get(hex(i+1),'0x00'))+" "+str(dict_data.get(hex(i+2),'0x00'))+" "+str(dict_data.get(hex(i+3),'0x00'))
            elif show_type_mem=='unsigned':
                my_str=str(int(dict_data.get(hex(i),'0x00'),16))+" "+str(int(dict_data.get(hex(i+1),'0x00'),16))+" "+str(int(dict_data.get(hex(i+2),'0x00'),16))+" "+str(int(dict_data.get(hex(i+3),'0x00'),16))
            else:
                my_str=str(hex_int(dict_data.get(hex(i),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+1),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+2),'0x00')))+" "+str(hex_int(dict_data.get(hex(i+3),"0x00")))
            mem_frame.insert(END,hex(i)+" : "+my_str)





root.mainloop()
