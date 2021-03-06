# -*- coding: utf-8 -*-
"""
Created on Thu May  6 23:51:51 2021

@author: asus
"""

import sys
import time
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from test2 import Ui_cache_window


aflag=0


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

def addToTagAdd(s):
    # s is in hex
    block_offset = int(s,16)%cache_block_size
    tag = int(s,16) - block_offset
    index = (tag//cache_block_size)%num_sets
    tagAdd = '0b'+bin(tag)[2:]+'0'*(num_index_bits-len(bin(index))+2)+bin(index)[2:]+'0'*(num_block_offset_bits-len(bin(block_offset))+2)+bin(block_offset)[2:]
    return tagAdd

def getBlockOffset(s):
    # s is bin string
    return int('0b'+s[-num_block_offset_bits:],2)

def getIndex(s):
    s = s[:-num_block_offset_bits]
    if num_index_bits==0:
        return 0
    return int('0b'+s[-num_index_bits:],2)

def getTag(s):
    s = s[:-(num_block_offset_bits+num_index_bits)]
    return hex(int(s,2))

def two_compliment(s):
    temp='0b'
    for i in s:
        temp+=str(1^int(i))
    
    return -1*(int(temp,2)+1)
    
def dataReadCache(s,h):
    # s is the address
    data_tag_add = addToTagAdd(s)
    data_tag = getTag(data_tag_add)
    data_index = getIndex(data_tag_add)
    data_offset = getBlockOffset(data_tag_add)
    value = 'error'
    # [ [ [ []->block  ] ] -> sets   ]->cache
    for i in data_cache[data_index]:
        if hex(int(i[0],16))==hex(int(data_tag,16)):
            value = '0x'+i[1][2+data_offset*2:data_offset*2+4]
            lru_data[i[0]] = n_asso-1
            h.append([data_tag,1])
        else:
            if i[0] in lru_data:
                lru_data[i[0]] = max(0,lru_data[i[0]]-1)
    if value=='error':
        
        # miss
        h.append([data_tag,0])
        if len(data_cache[data_index])==n_asso:
            # need to evict from alu
            mini = [0,lru_data[data_cache[data_index][0][0]]]
            for i in range(1,n_asso):
                if mini[1]<lru_data[data_cache[data_index][i][0]]:
                    mini = [i,lru_data[data_cache[data_index][i][0]]]
            # evict the mini
            lru_data.pop(data_cache[data_index][mini[0]][0])
            temp = '0x'
            for i in range(int(data_tag,16),int(data_tag,16)+cache_block_size):
                temp += dict_data.get(hex(i),'0x00')[2:]
            data_cache[data_index][mini[0]] = [data_tag,temp]
            lru_data[data_tag] = n_asso-1
            value = dict_data.get(s,'0x00')
        
        else:
            temp = '0x'
            for i in range(int(data_tag,16),int(data_tag,16)+cache_block_size):
                temp += dict_data.get(hex(i),'0x00')[2:]
            data_cache[data_index].append([data_tag,temp])
            lru_data[data_tag] = n_asso-1
            value = dict_data.get(s,'0x00')
    return value     

def dataWriteCache(s,data,h):
    
    data_tag_add = addToTagAdd(s)
    data_tag = getTag(data_tag_add)
    data_index = getIndex(data_tag_add)
    data_offset = getBlockOffset(data_tag_add)
    h.append([data_tag,0])
    for i in range(len(data_cache[data_index])):
        if hex(int(data_cache[data_index][i][0],16))==hex(int(data_tag,16)):
            value = '0x'+data_cache[data_index][i][1][2:2+data_offset*2]
            value += data[2:]
            value += data_cache[data_index][i][1][data_offset*2+4:]
            data_cache[data_index][i][1] = value
            lru_data[data_cache[data_index][i][0]] = n_asso-1
            h.pop()
            h.append([data_tag,1])
            
        else:
            if data_cache[data_index][i][0] in lru_data:
                lru_data[data_cache[data_index][i][0]] = max(0,lru_data[data_cache[data_index][i][0]]-1)
    

def init_registers():
    global registers
    registers = [0]*32
    registers[2]= 0x7ffffff0
    registers[3]= 0x10000000
    
def init(file_name,delimit,frwrd):
    f = open("output.txt","w")
    f.close()
    file = open(file_name,"r")
    instructions = file.readlines()
    init_registers()    
    
    global inst
    global lru_inst
    global lru_data
    global instruction_count
    global under_progress
    global jump_dict
    global branch_dict
    global num_cycles
    global num_data_transfer
    global num_alu_inst
    global num_control
    global num_stalls
    global num_data_hazard
    global num_control_hazard
    global num_mis
    global num_stalls_data
    global num_stalls_control
    global num_flushes
    global variables
    global control
    global dict_data
    global dict_instructions
    global control_set
    global rd_use
    global default_var
    global default_control
    global forwarding
    global data_forwarding
    global num_instructions
    global num_stalls
    global inst_cache
    global data_cache
    
    instruction_count=0
    under_progress={}
    
    inst={}    
    lru_inst={}
    lru_data={}
    inst_cache=[]
    for i in range(num_sets):
        inst_cache.append([])
    data_cache=[]
    for i in range(num_sets):
        data_cache.append([])
    num_data_transfer = 0
    num_stalls_data = 0
    num_stalls_control = 0
    num_flushes = 0
    num_control_hazard = 0
    num_stalls=0
    num_mis = 0
    num_alu_inst=0
    num_control=0
    num_data_hazard = 0    
    num_cycles=0
    jump_dict={}
    branch_dict={}
    default_var = {'ir_final':0,'pctemp':'0x0','pc':'0x0','ir':0,'alu2':0,'alu1':0,'mar':0,'mdr':0,'rm':0,'ry':0,'rz':0,'rs1':0,'rs2':0,'rd':0,'imm':0}
    default_control = {'type':'X','operation':'xxx'}
    h_s = 0 # 0 means no error 1 means opcode doesnt exist 2 means data_hazard 3 means control_hazard 
    num_instructions=0
    
    data_forwarding = frwrd
    
    forwarding={}
    default_var = {'ir_final':0,'pctemp':'0x0','pc':'0x0','ir':0,'alu2':0,'alu1':0,'mar':0,'mdr':0,'rm':0,'ry':0,'rz':0,'rs1':0,'rs2':0,'rd':0,'imm':0}
    variables = {0:default_var}
    default_control = {'type':'X','operation':'xxx'}
    control_set = {0:default_control}
    dict_data={}
    dict_instructions={}
    rd_use = {}
    
    delimiter = 0
    for i in instructions:
        if i[len(i)-1]=='\n':
            i = i[:len(i)-1]
        t=i.split()
        if len(t)==2:
            if t[1] == delimit:
                delimiter = 1
                continue
        elif i==delimit:
            delimiter = 1
            continue
        if delimiter:
            temp = i.split()
            dict_data[temp[0].lower()] = temp[1]
        else:
            temp = i.split()
            dict_instructions[temp[0]] = temp[1]
    
def fetch(num_instruction):
    global misses
    global hits
    var = variables[num_instruction].copy() 
    inst_tag_add = addToTagAdd(var['pc'])
    inst_tag = getTag(inst_tag_add)
    inst_index = getIndex(inst_tag_add)
    inst_offset = getBlockOffset(inst_tag_add)
    var['ir'] = 'error'
    
    for i in inst_cache[inst_index]:
        if hex(int(i[0],16))==hex(int(inst_tag,16)):
            print("It was a hit")
            var['ir'] = '0x'+i[1][2+inst_offset*2:inst_offset*2+10]
            lru_inst[i[0]] = n_asso-1
            hits+=1
        else:
            if i[0] in lru_inst:
                lru_inst[i[0]] = max(0,lru_inst[i[0]]-1)
    
    if var['ir']=='error':
        # miss
        misses+=1
        print("It was a miss")
        if len(inst_cache[inst_index])==n_asso:
            # need to evict from alu
            print("It was a conflict")
            mini = [0,lru_inst[inst_cache[inst_index][0][0]]]
            for i in range(1,n_asso):
                if mini[1]<lru_inst[inst_cache[inst_index][i][0]]:
                    mini = [i,lru_inst[inst_cache[inst_index][i][0]]]
            # evict the mini
            lru_inst.pop(inst_cache[inst_index][mini[0]][0])
            temp = '0x'
            for i in range(int(inst_tag,16),int(inst_tag,16)+cache_block_size,4):
                t = dict_instructions.get(hex(i),'0x00')[2:]
                temp += '0'*(8-len(t))+t
            inst_cache[inst_index][mini[0]] = [inst_tag,temp]
            lru_inst[inst_tag] = n_asso-1
            var['ir'] = dict_instructions[var['pc']]
        
        else:
            temp = '0x'
            for i in range(int(inst_tag,16),int(inst_tag,16)+cache_block_size,4):
                t=dict_instructions.get(hex(i),'0x00')[2:]
                temp += '0'*(8-len(t))+t
            inst_cache[inst_index].append([inst_tag,temp])
            lru_inst[inst_tag] = n_asso-1
            var['ir'] = dict_instructions[var['pc']]
    
    var['ir'] = bin(int(var['ir'],16))[2:]
    var['ir'] = '0b'+(32-len(var['ir']))*'0'+var['ir']
    var['ir_final'] = var['ir']
    # print(var['ir'])
    var['pctemp'] = hex(int(var['pc'],16)+4)
    

        
    variables[num_instruction] = var.copy()
    if num_instruction+1 not in variables:
        variables[num_instruction+1] = default_var.copy()
        control_set[num_instruction+1] = default_control.copy()
    if var['pc'] in jump_dict:
        variables[num_instruction+1]['pc'] = jump_dict[var['pc']]
    else:
        variables[num_instruction+1]['pc'] = var['pctemp']
    


def decode(num_instruction,stalling):
    
    control = control_set[num_instruction].copy()
    global num_data_hazard
    global num_control_hazard
    global num_stalls_data
    global num_flushes
    global num_stalls_control
    global num_cycles
    global num_mis
    global num_stalls
    
    var = variables[num_instruction].copy()
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
            else:
                return 1
        elif func3=='0x4':
            if func7=='0x0':
                control['operation']='^'
            elif func7=='0x1':
                control['operation']='/'
            else:
                return 1
        elif func3=='0x6':
            if func7=='0x0':
                control['operation']='|'
            elif func7=='0x1':
                control['operation']='%'
            else:
                return 1
        elif func3=='0x7':
            if func7=='0x0':
                control['operation']='&'
            else:
                return 1
        elif func3=='0x5':
            if func7=='0x0':
                control['operation']='>>>'
            elif func7=='0x20':
                control['operation']='>>'
            else:
                return 1
        elif func3=='0x1' and func7=='0x0':
            control['operation']='<<'
        elif func3=='0x2' and func7=='0x0':
            control['operation']='<'
        else:
            return 1
    
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
        elif func3=='0x7':
            control['operation']='&'
        elif func3=='0x6':
            control['operation']='|'
        else:
            return 1
            
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
        elif func3=='0x1':
            control['operation']='lh'
        elif func3=='0x2':
            control['operation']='lw'
        else:
            return 1
        
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
        var['alu2']= registers[int(var['rs2'],16)]
        
        control['type']='S'
        if func3=='0x0':
            control['operation']='sb'
        elif func3=='0x1':
            control['operation']='sh'
        elif func3=='0x2':
            control['operation']='sw'
        else:
            return 1
        
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
        elif func3=='0x1':
            control['operation']='!='
        elif func3=='0x5':
            control['operation']='>='
        elif func3=='0x4':
            control['operation']='<'
        else:
            return 1
            
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
        
        return 1
    
    
    if type(var['imm'])==str and len(var['imm'])>2:
        if var['imm'][:3]=='0b1':
            var['imm']=two_compliment(var['imm'][2:])
        else:
            var['imm']=int(var['imm'],2)
    
    if stalling:
       
        if var['rs1'] in rd_use:
           
            for i in rd_use[var['rs1']]:
                if num_instruction>i:
                    num_stalls_data += 1
                    return 2        
        if var['rs2'] in rd_use:
            for i in rd_use[var['rs2']]:
                if num_instruction>i:
                    num_stalls_data += 1
                    return 2        
    else:
        
        forward = {}
        if var['rs1'] in rd_use:
            forward[var['rs1']]=1
        if var['rs2'] in rd_use:
            forward[var['rs2']]=1
        if len(forward):
            forwarding[num_instruction] = forward.copy()
    
    if type(var['rd']) == str and int(var['rd'],16)!=0:
        if var['rd'] not in rd_use:
            rd_use[var['rd']]={}
        rd_use[var['rd']][num_instruction] = 1
        
    stop=0
        
    if control['type']=='UJ': # jal
        nextpc= hex(int(var['pc'],16)+var['imm'])
        if (nextpc!=var['pc']):
            jump_dict[hex(int(var['pctemp'],16)-4)] = var['pc']
            variables[(num_instruction)]['pc']=nextpc
            var['pc'] = nextpc
            stop = 1
    
    if control['type']=='I':
        if control['operation'][0]=='j': # jalr
            nextpc = hex(var['alu1']+var['imm'])
            var['mar']= 'error'
            if (nextpc!=var['pc']):
                jump_dict[hex(int(var['pctemp'],16)-4)] = var['pc']
                variables[(num_instruction)]['pc']=nextpc
                var['pc'] = nextpc
                stop = 1
    
    if control['type']=='SB': #beq bne blt bge
        if stalling==0:
            if num_instruction in forwarding:
                num_data_hazard += 1
                if var['rs1'] in forwarding[num_instruction]:
                    if var['rs1'] in rd_use:
                        l=list(rd_use[var['rs1']].keys())
                        for i in range(len(l)-1,-1,-1):
                            if num_instruction >l[i]:
                                
                                if variables[l[i]]['ry']!='error':
                                    var['alu1'] = variables[l[i]]['ry']
                                    print("Data forwarding is being done to handle data hazard in instruction at",var['pc'])
                                else:
                                    forwarding.pop(num_instruction)
                                    num_stalls_data += 1
                                    return 2
                if var['rs2'] in forwarding[num_instruction]:
                    if var['rs2'] in rd_use:
                        l=list(rd_use[var['rs2']].keys())
                        for i in range(len(l)-1,-1,-1):
                            if num_instruction >l[i]:
                                if variables[l[i]]['ry']!='error':
                                    var['alu2'] = variables[l[i]]['ry']
                                    print("Data forwarding is being done to handle data hazard in instruction at",var['pc'])
                                else:
                                    forwarding.pop(num_instruction)
                                    num_stalls_data += 1
                                    return 2
                forwarding.pop(num_instruction)
        
        if eval(str(var['alu1'])+control['operation']+str(var['alu2'])):
            
            var['pc']=hex(int(var['pc'],16)+var['imm'])
            if (var['pc']!=var['pctemp']):
                
                variables[(num_instruction)]['pc']=var['pc']
                
                stop = 1
        else:
            var['pc']= var['pctemp']
    
    variables[num_instruction] = var.copy()
    control_set[num_instruction] = control.copy()
    
    if stop:
        num_cycles+=1
        num_mis += 1
        num_flushes +=1
        num_stalls_control += 1
        num_stalls+=1
        return 3
    
    return 0
    
def execute(num_instruction,data_forwarding): 
    
    var = variables[num_instruction].copy()
    var['mar']='error'
    var['ry']='error'
    control = control_set[num_instruction].copy()
    
    global num_data_hazard
    
    if control['operation']=='*':
        x=1
    if data_forwarding:
        if num_instruction in forwarding:
            print("Data forwarding is being done to handle data hazard in instruction at",var['pc'])
            num_data_hazard += 1
            if var['rs1'] in forwarding[num_instruction]:
                if var['rs1'] in rd_use:
                    l=list(rd_use[var['rs1']].keys())
                    for i in range(len(l)-1,-1,-1):
                        if num_instruction>l[i]:
                            var['alu1'] = variables[l[i]]['ry']
                        else:
                            var['alu1'] = registers[int(var['rs1'],16)]
                else:
                    var['alu1'] = registers[int(var['rs1'],16)]
        
            if var['rs2'] in forwarding[num_instruction]:
                if var['rs2'] in rd_use:
                    l=list(rd_use[var['rs2']].keys())
                    for i in range(len(l)-1,-1,-1):
                        if num_instruction>l[i]:
                            var['alu2'] = variables[l[i]]['ry']
                        else:
                            var['alu2'] = registers[int(var['rs2'],16)]
                else:
                    var['alu2'] = registers[int(var['rs2'],16)]
            forwarding.pop(num_instruction)
                
    
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
        
        temp= var['alu2']
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
        
    
    variables[num_instruction] = var.copy()
    control_set[num_instruction] = control.copy()

def memory_read_write(num_instruction):
    global hits
    global misses
    var = variables[num_instruction].copy()
    control = control_set[num_instruction].copy()
    done={}
    if control['type']=='R':
        var['ry']= var['rz']
        
    if control['type']=='I':
        
        
        if control['operation'][0]!='l' or control['operation'][0]!='j':
            var['ry']= var['rz']
        if control['operation']=='lb':
            h=[]
            var['ry']= dataReadCache(hex(int(var['mar'],16)),h)[2:]
            if len(h)>0:
                hits+=1
            else:
                misses+=1
            var['ry']='0x'+var['ry'][2]*6+var['ry'][2:]
            if h[0][1]:
                hits+=1
            else:
                misses+=1
        if control['operation']=='lh':
            var['ry']='0x'
            h=[]
            for i in range(1,-1,-1):
                temp= dataReadCache(hex(int(var['mar'],16)+i),h)[2:]
                if (len(temp)<2):
                    temp=('0'+temp if int('0x'+temp,16)<8 else 'f'+temp)
                var['ry']+= temp
            var['ry']='0x'+var['ry'][2]*4+var['ry'][2:]
            for i in h:
                if i[0] not in done:
                    if i[1]:
                        hits+=1
                    else:
                        misses+=1
                    done[i[0]]=1
        if control['operation']=='lw':
            var['ry']='0x'
            h=[]
            for i in range(3,-1,-1):
                temp= dataReadCache(hex(int(var['mar'],16)+i),h)[2:]
                if (len(temp)<2):
                    temp=('0'+temp if int('0x'+temp,16)<8 else 'f'+temp)
                var['ry']+= temp
            for i in h:
                if i[0] not in done:
                    if i[1]:
                        hits+=1
                    else:
                        misses+=1
                    done[i[0]]=1
            # print(var['ry'],var['mar'])
            # print("==================")
            
        
        if control['operation'][0]=='j':
            var['ry']= var['pctemp']
    h=[]
    if control['type']== 'S':
        if control['operation']=='sb':
            var['mdr']='0x'+var['mdr'][len(var['mdr'])-2:]
            dict_data[var['mar']]= var['mdr']
            dataWriteCache(var['mar'],var['mdr'],h)
        if control['operation']=='sh':
            var['mdr']=var['mdr'][len(var['mdr'])-4:]
            for i in range(2):
                dict_data[hex(int(var['mar'],16)+(1-i))]= '0x'+var['mdr'][i*2:(i+1)*2]
                dataWriteCache(hex(int(var['mar'],16)+(1-i)),'0x'+var['mdr'][i*2:(i+1)*2],h)
        if control['operation']=='sw':
            var['mdr']=var['mdr'][len(var['mdr'])-8:]
            # print("mar",var['mar'],"mdr",var['mdr'],"==============")
            for i in range(4):
                dict_data[hex(int(var['mar'],16)+(3-i))]= '0x'+var['mdr'][i*2:(i+1)*2]
                dataWriteCache(hex(int(var['mar'],16)+(3-i)),'0x'+var['mdr'][i*2:(i+1)*2],h)
        for i in h:
            if i[0] not in done:
                if i[1]:
                    hits+=1
                else:
                    misses+=1
                done[i[0]]=1
            
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
    variables[num_instruction] = var.copy()
            
def write_back(num_instruction):
    var = variables[num_instruction].copy()
    global num_alu_inst
    global num_data_transfer
    global num_control
    
    if control_set[num_instruction]['operation'] in ['lb','lw','lh','sb','sh','sw']:
        num_data_transfer+=1
    
    if control_set[num_instruction]['type'] not in ['SB','UJ'] and control_set[num_instruction]['operation']!='jalr':
        num_alu_inst += 1
    
    else:
        num_control+=1
    
    if var['ry']!='error':
        # print(var['ry'],var['rd'],var['pc'])
        registers[int(var['rd'],16)]= var['ry']
        if var['rd']!='0x0':
            for i in rd_use[var['rd']]:
                if i==num_instruction:
                    rd_use[var['rd']].pop(i)
                    break
            if rd_use[var['rd']]=={}:
                rd_use.pop(var['rd'])
    registers[0]=0
    variables[num_instruction] = var.copy()


def cycle_step():
    f = open("output.txt","a")
    sys.stdout = f
    global instruction_count
    global data_forwarding
    global num_instructions
    global num_stalls
    global num_cycles
    global last
    global inst
    global num_control
    global first_done
    
    cycle_complete = 0
    last = 0
    
    if (first_done and instruction_count in variables and variables[instruction_count]['pc'] in dict_instructions):
        
        if instruction_count>3 and under_progress.get(instruction_count-4,0)==4:
            write_back((instruction_count-4))
            under_progress[instruction_count-4]+=1
            under_progress.pop(instruction_count-4)
            cycle_complete=1
            
            num_instructions+=1
            inst['r'] = hex(int(variables[instruction_count-4]['pctemp'],16)-4)
            print("The register write back stage of instruction at",inst['r'],"was completed.")
            variables.pop(instruction_count-4)
            control_set.pop(instruction_count-4)
        else:
            if 'r' in inst:
                inst.pop('r')
        
        if instruction_count>2 and under_progress.get(instruction_count-3,0)==3:
            memory_read_write((instruction_count-3))
            under_progress[instruction_count-3]+=1
            inst['m'] = hex(int(variables[instruction_count-3]['pctemp'],16)-4)
            print("The memory access stage of instruction at",inst['m'],"was completed.")
        else:
            if 'm' in inst:
                inst.pop('m')
        
        if instruction_count>1 and under_progress.get(instruction_count-2,0)==2:
            execute((instruction_count-2),data_forwarding)
            under_progress[instruction_count-2]+=1
            inst['e'] = hex(int(variables[instruction_count-2]['pctemp'],16)-4)
            print("The execute stage of instruction at",inst['e'],"was completed.")
        else:
            if 'e' in inst:
                inst.pop('e')
        
        if instruction_count>0 and under_progress.get(instruction_count-1,0)==1:
            h_s = decode((instruction_count-1),(data_forwarding+1)%2)
            if h_s == 2:
                variables[instruction_count] = variables[instruction_count-1].copy()
                variables.pop(instruction_count-1)
                for i in rd_use:
                    for j in rd_use[i]:
                        if j==instruction_count-1:
                            rd_use[i].pop(instruction_count-1)
                            rd_use[instruction_count]=1
                control_set[instruction_count] = control_set[instruction_count-1].copy()
                control_set.pop(instruction_count-1)
                under_progress[instruction_count]=1
                under_progress.pop(instruction_count-1)
                instruction_count+=1
                num_stalls+=1
                print("Furthermore this cycle is being stalled.")
                return cycle_complete
            
            elif h_s==3:
                
                if instruction_count in under_progress:
                    under_progress.pop(instruction_count)
                    print("Flush was implemented. Instruction at pc",variables[instruction_count],"is flushed.")
                    variables[(instruction_count)] = default_var.copy()
                    control_set[instruction_count] = default_control.copy()
                
                if instruction_count not in variables:
                    control_set[instruction_count] = default_control.copy()
                    variables[instruction_count] = default_var.copy()
                variables[(instruction_count)]['pc'] = variables[(instruction_count-1)]['pc']
            
            under_progress[instruction_count-1]+=1
            inst['d'] = hex(int(variables[instruction_count-1]['pctemp'],16)-4)
            print("The decode stage of instruction at",inst['d'],"was completed.")
            
            if instruction_count not in variables:
                variables[instruction_count] = default_var.copy()
                variables[instruction_count]['pc'] = variables[instruction_count-1]['pctemp']
                control_set[instruction_count] = default_control.copy()
        else:
            if 'd' in inst:
                inst.pop('d')
    
        if instruction_count in variables and variables[instruction_count]['pc'] in dict_instructions:
            fetch(instruction_count)
            under_progress[instruction_count]=1
            inst['f'] = hex(int(variables[instruction_count]['pctemp'],16)-4)
            instruction_count+=1
            print("The fetch stage of instruction at",inst['f'],"was completed.")
        else:
            if 'f' in inst:
                inst.pop('f')
            first_done=0
        
        return cycle_complete
    
    if (len(under_progress.keys())): # because there can maximum be 4 extra cycles after the code has terminated
        if under_progress.get((instruction_count-4),0)==4:
            write_back((instruction_count-4))
            under_progress[instruction_count-4]+=1
            under_progress.pop(instruction_count-4)
            inst['r'] = hex(int(variables[instruction_count-4]['pctemp'],16)-4)
            print("The register write back stage of instruction at",inst['r'],"was completed.")
            variables.pop(instruction_count-4)
            control_set.pop(instruction_count-4)
            num_instructions+=1
            cycle_complete=1
            last = 1
        else:
            if 'r' in inst:
                inst.pop('r')
            
            
        if under_progress.get((instruction_count-3),0)==3:
            memory_read_write((instruction_count-3))
            under_progress[instruction_count-3]+=1
            inst['m'] = hex(int(variables[instruction_count-3]['pctemp'],16)-4)
            print("The memory access stage of instruction at",inst['m'],"was completed.")
            last = 0
        else:
            if 'm' in inst:
                inst.pop('m')
            
        if under_progress.get((instruction_count-2),0)==2:
            execute((instruction_count-2),data_forwarding)
            under_progress[instruction_count-2]+=1
            inst['e'] = hex(int(variables[instruction_count-2]['pctemp'],16)-4)
            print("The execute stage of instruction at",inst['e'],"was completed.")
            last = 0
        else:
            if 'e' in inst:
                inst.pop('e')
            
        if instruction_count>0 and under_progress.get(instruction_count-1,0)==1:
            h_s = decode((instruction_count-1),(data_forwarding+1)%2)
            if h_s == 2:
                variables[instruction_count] = variables[instruction_count-1].copy()
                variables.pop(instruction_count-1)
                control_set[instruction_count] = control_set[instruction_count-1].copy()
                control_set.pop(instruction_count-1)
                under_progress[instruction_count]=1
                under_progress.pop(instruction_count-1)
                instruction_count+=1
                num_stalls+=1
                print("Furthermore this cycle is being stalled.")
                return cycle_complete
            
            elif h_s==3:
                if instruction_count in under_progress:
                    under_progress.pop(instruction_count)
                    print("Flush was implemented. Instruction at pc",variables[instruction_count],"is flushed.")
                    variables[(instruction_count)] = default_var.copy()
                    control_set[instruction_count] = default_control.copy()
                
                if instruction_count not in variables:
                    control_set[instruction_count] = default_control.copy()
                    variables[instruction_count] = default_var.copy()
                variables[(instruction_count)]['pc'] = variables[(instruction_count-1)]['pc']
            
            under_progress[instruction_count-1]+=1
            
            inst['d'] = hex(int(variables[instruction_count-1]['pctemp'],16)-4)
            print("The decode stage of instruction at",inst['d'],"was completed.")
            
            if instruction_count not in variables:
                variables[instruction_count] = default_var.copy()
                variables[instruction_count]['pc'] = variables[instruction_count-1]['pctemp']
                control_set[instruction_count] = default_control.copy()
            last = 0
        else:
            if 'd' in inst:
                inst.pop('d')
    
        if (instruction_count in variables) and variables[instruction_count]['pc'] in dict_instructions:
            fetch(instruction_count)
            under_progress[instruction_count]=1
            last = 0
            inst['f'] = hex(int(variables[instruction_count]['pctemp'],16)-4)
            print("The fetch stage of instruction at",inst['f'],"was completed.")
        instruction_count+=1
        return cycle_complete
    
def step():
    cycle_complete=0
    while(cycle_complete==0):
        cycle_complete = cycle_step()
    
def run_all():
    global last
    last = 0
    while(last==0):
        step()
          
cache_size = int(input("Enter the size of cache: "))


cache_block_size = int(input("Enter the size of block: "))
n_asso = int(input("Enter the n of n-associativity: "))
num_sets = (cache_size//cache_block_size)//n_asso
num_index_bits = int(math.log(num_sets,2))
num_block_offset_bits = int(math.log(cache_block_size,2))
hits = 0
misses = 0
    
# # init("file.mc.txt","0xffffc",1)
first_done=1
last = 0
# # run_all()
# # cycle_step()


# num_cycles += instruction_count
# cpi = num_cycles/(num_instructions)
# # print(num_cycles,num_instructions,cpi,num_data_transfer,num_alu_inst,num_stalls,num_data_hazard,num_control_hazard,num_mis,num_stalls_data,num_stalls_control,num_flushes)
# values = {'hits':hits,'misses':misses,'cycles':num_cycles,'instructions':num_instructions,'cpi':cpi,'data-transfer':num_data_transfer,'alu':num_alu_inst,'control':num_control,'stalls':num_stalls,'data-hazards':num_data_hazard,'control-hazards':num_control_hazard,'branch-mispredictions':num_mis,'stalls-data-hazards':num_stalls_data,'stalls-control-hazards':num_stalls_control}

#--------------------------------------------

l=[]    
for i in range(32):
    l.append(hex(0))
tp=[]   
for i in range(32):
    tp.append(0)
dict_data={}
tpdict={}
tpp={}
values={}


inst={}








class Ui_mainWindow(object):
    def setupUi(self, mainWindow):

        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1044, 957)
        mainWindow.setMinimumSize(QtCore.QSize(10, 10))
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Register = QtWidgets.QScrollArea(self.centralwidget)
        self.Register.setGeometry(QtCore.QRect(630, 40, 381, 291))
        self.Register.setMinimumSize(QtCore.QSize(40, 40))
        self.Register.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.Register.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Register.setWidgetResizable(True)
        self.Register.setObjectName("Register")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 358, 1519))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.x0 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x0.setMinimumSize(QtCore.QSize(40, 40))
       
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_cache_window()
        self.ui.setupUi(self.window)


        font = QtGui.QFont()
        font.setPointSize(10)
        self.x0.setFont(font)
        self.x0.setFrameShape(QtWidgets.QFrame.Box)
        self.x0.setObjectName("x0")
        self.verticalLayout.addWidget(self.x0)
        self.x1 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x1.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x1.setFont(font)
        self.x1.setFrameShape(QtWidgets.QFrame.Box)
        self.x1.setObjectName("x1")
        self.verticalLayout.addWidget(self.x1)
        self.x2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x2.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x2.setFont(font)
        self.x2.setFrameShape(QtWidgets.QFrame.Box)
        self.x2.setObjectName("x2")
        self.verticalLayout.addWidget(self.x2)
        self.x3 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x3.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x3.setFont(font)
        self.x3.setFrameShape(QtWidgets.QFrame.Box)
        self.x3.setObjectName("x3")
        self.verticalLayout.addWidget(self.x3)
        self.x4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x4.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x4.setFont(font)
        self.x4.setFrameShape(QtWidgets.QFrame.Box)
        self.x4.setObjectName("x4")
        self.verticalLayout.addWidget(self.x4)
        self.x5 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x5.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x5.setFont(font)
        self.x5.setFrameShape(QtWidgets.QFrame.Box)
        self.x5.setObjectName("x5")
        self.verticalLayout.addWidget(self.x5)
        self.x6 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x6.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x6.setFont(font)
        self.x6.setFrameShape(QtWidgets.QFrame.Box)
        self.x6.setObjectName("x6")
        self.verticalLayout.addWidget(self.x6)
        self.x7 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x7.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x7.setFont(font)
        self.x7.setFrameShape(QtWidgets.QFrame.Box)
        self.x7.setObjectName("x7")
        self.verticalLayout.addWidget(self.x7)
        self.x8 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x8.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x8.setFont(font)
        self.x8.setFrameShape(QtWidgets.QFrame.Box)
        self.x8.setObjectName("x8")
        self.verticalLayout.addWidget(self.x8)
        self.x9 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x9.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x9.setFont(font)
        self.x9.setFrameShape(QtWidgets.QFrame.Box)
        self.x9.setObjectName("x9")
        self.verticalLayout.addWidget(self.x9)
        self.x10 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x10.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x10.setFont(font)
        self.x10.setFrameShape(QtWidgets.QFrame.Box)
        self.x10.setObjectName("x10")
        self.verticalLayout.addWidget(self.x10)
        self.x11 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x11.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x11.setFont(font)
        self.x11.setFrameShape(QtWidgets.QFrame.Box)
        self.x11.setObjectName("x11")
        self.verticalLayout.addWidget(self.x11)
        self.x12 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x12.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x12.setFont(font)
        self.x12.setFrameShape(QtWidgets.QFrame.Box)
        self.x12.setObjectName("x12")
        self.verticalLayout.addWidget(self.x12)
        self.x13 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x13.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x13.setFont(font)
        self.x13.setFrameShape(QtWidgets.QFrame.Box)
        self.x13.setObjectName("x13")
        self.verticalLayout.addWidget(self.x13)
        self.x14 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x14.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x14.setFont(font)
        self.x14.setFrameShape(QtWidgets.QFrame.Box)
        self.x14.setObjectName("x14")
        self.verticalLayout.addWidget(self.x14)
        self.x15 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x15.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x15.setFont(font)
        self.x15.setFrameShape(QtWidgets.QFrame.Box)
        self.x15.setObjectName("x15")
        self.verticalLayout.addWidget(self.x15)
        self.x16 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x16.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x16.setFont(font)
        self.x16.setFrameShape(QtWidgets.QFrame.Box)
        self.x16.setObjectName("x16")
        self.verticalLayout.addWidget(self.x16)
        self.x17 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x17.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x17.setFont(font)
        self.x17.setFrameShape(QtWidgets.QFrame.Box)
        self.x17.setObjectName("x17")
        self.verticalLayout.addWidget(self.x17)
        self.x18 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x18.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x18.setFont(font)
        self.x18.setFrameShape(QtWidgets.QFrame.Box)
        self.x18.setObjectName("x18")
        self.verticalLayout.addWidget(self.x18)
        self.x19 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x19.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x19.setFont(font)
        self.x19.setFrameShape(QtWidgets.QFrame.Box)
        self.x19.setObjectName("x19")
        self.verticalLayout.addWidget(self.x19)
        self.x20 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x20.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x20.setFont(font)
        self.x20.setFrameShape(QtWidgets.QFrame.Box)
        self.x20.setObjectName("x20")
        self.verticalLayout.addWidget(self.x20)
        self.x21 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x21.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x21.setFont(font)
        self.x21.setFrameShape(QtWidgets.QFrame.Box)
        self.x21.setObjectName("x21")
        self.verticalLayout.addWidget(self.x21)
        self.x22 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x22.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x22.setFont(font)
        self.x22.setFrameShape(QtWidgets.QFrame.Box)
        self.x22.setObjectName("x22")
        self.verticalLayout.addWidget(self.x22)
        self.x23 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x23.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x23.setFont(font)
        self.x23.setFrameShape(QtWidgets.QFrame.Box)
        self.x23.setObjectName("x23")
        self.verticalLayout.addWidget(self.x23)
        self.x24 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x24.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x24.setFont(font)
        self.x24.setFrameShape(QtWidgets.QFrame.Box)
        self.x24.setObjectName("x24")
        self.verticalLayout.addWidget(self.x24)
        self.x25 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x25.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x25.setFont(font)
        self.x25.setFrameShape(QtWidgets.QFrame.Box)
        self.x25.setObjectName("x25")
        self.verticalLayout.addWidget(self.x25)
        self.x26 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x26.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x26.setFont(font)
        self.x26.setFrameShape(QtWidgets.QFrame.Box)
        self.x26.setObjectName("x26")
        self.verticalLayout.addWidget(self.x26)
        self.x27 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x27.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x27.setFont(font)
        self.x27.setFrameShape(QtWidgets.QFrame.Box)
        self.x27.setObjectName("x27")
        self.verticalLayout.addWidget(self.x27)
        self.x28 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x28.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x28.setFont(font)
        self.x28.setFrameShape(QtWidgets.QFrame.Box)
        self.x28.setObjectName("x28")
        self.verticalLayout.addWidget(self.x28)
        self.x29 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x29.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x29.setFont(font)
        self.x29.setFrameShape(QtWidgets.QFrame.Box)
        self.x29.setObjectName("x29")
        self.verticalLayout.addWidget(self.x29)
        self.x30 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x30.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x30.setFont(font)
        self.x30.setFrameShape(QtWidgets.QFrame.Box)
        self.x30.setObjectName("x30")
        self.verticalLayout.addWidget(self.x30)
        self.x31 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.x31.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.x31.setFont(font)
        self.x31.setFrameShape(QtWidgets.QFrame.Box)
        self.x31.setObjectName("x31")
        self.verticalLayout.addWidget(self.x31)
        self.Register.setWidget(self.scrollAreaWidgetContents)
        self.c1 = QtWidgets.QComboBox(self.centralwidget)
        self.c1.setGeometry(QtCore.QRect(630, 330, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.c1.setFont(font)
        self.c1.setObjectName("c1")
        self.c1.addItem("")
        self.c1.addItem("")
        self.c1.addItem("")
        self.c2 = QtWidgets.QComboBox(self.centralwidget)
        self.c2.setGeometry(QtCore.QRect(630, 830, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.c2.setFont(font)
        self.c2.setObjectName("c2")
        self.c2.addItem("")
        self.c2.addItem("")
        self.c2.addItem("")
        self.assemble = QtWidgets.QPushButton(self.centralwidget)
        self.assemble.setGeometry(QtCore.QRect(20, 10, 111, 41))
        self.assemble.setObjectName("assemble")
        self.step = QtWidgets.QPushButton(self.centralwidget)
        self.step.setGeometry(QtCore.QRect(130, 10, 121, 41))
        self.step.setObjectName("step")
        self.cyclestep = QtWidgets.QPushButton(self.centralwidget)
        self.cyclestep.setGeometry(QtCore.QRect(250, 10, 121, 41))
        self.cyclestep.setObjectName("cyclestep")
        self.run = QtWidgets.QPushButton(self.centralwidget)
        self.run.setGeometry(QtCore.QRect(370, 10, 111, 41))
        self.run.setObjectName("run")
        self.memory = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.memory.setGeometry(QtCore.QRect(630, 430, 381, 401))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.memory.setFont(font)
        self.memory.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.memory.setPlainText("")
        self.memory.setObjectName("memory")
        self.output = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.output.setGeometry(QtCore.QRect(30, 330, 561, 251))
        self.output.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.output.setObjectName("output")
        self.output.setFont(font)
        self.fetch = QtWidgets.QLabel(self.centralwidget)
        self.fetch.setGeometry(QtCore.QRect(30, 80, 561, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.fetch.setFont(font)
        self.fetch.setFrameShape(QtWidgets.QFrame.Box)
        self.fetch.setObjectName("fetch")
        self.decode = QtWidgets.QLabel(self.centralwidget)
        self.decode.setGeometry(QtCore.QRect(30, 120, 561, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.decode.setFont(font)
        self.decode.setFrameShape(QtWidgets.QFrame.Box)
        self.decode.setObjectName("decode")
        self.execute = QtWidgets.QLabel(self.centralwidget)
        self.execute.setGeometry(QtCore.QRect(30, 160, 561, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.execute.setFont(font)
        self.execute.setFrameShape(QtWidgets.QFrame.Box)
        self.execute.setObjectName("execute")
        self.MA = QtWidgets.QLabel(self.centralwidget)
        self.MA.setGeometry(QtCore.QRect(30, 200, 561, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.MA.setFont(font)
        self.MA.setFrameShape(QtWidgets.QFrame.Box)
        self.MA.setObjectName("MA")
        self.RU = QtWidgets.QLabel(self.centralwidget)
        self.RU.setGeometry(QtCore.QRect(30, 240, 561, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.RU.setFont(font)
        self.RU.setFrameShape(QtWidgets.QFrame.Box)
        self.RU.setObjectName("RU")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(630, 10, 381, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 300, 561, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtWidgets.QFrame.Box)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(630, 400, 381, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setFrameShape(QtWidgets.QFrame.Box)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(29, 600, 571, 271))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 548, 579))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cycles = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.cycles.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.cycles.setFont(font)
        self.cycles.setFrameShape(QtWidgets.QFrame.Box)
        self.cycles.setObjectName("cycles")
        self.verticalLayout_2.addWidget(self.cycles)
        self.ti = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.ti.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.ti.setFont(font)
        self.ti.setFrameShape(QtWidgets.QFrame.Box)
        self.ti.setObjectName("ti")
        self.verticalLayout_2.addWidget(self.ti)
        self.cpi = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.cpi.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.cpi.setFont(font)
        self.cpi.setFrameShape(QtWidgets.QFrame.Box)
        self.cpi.setObjectName("cpi")
        self.verticalLayout_2.addWidget(self.cpi)
        self.ndt = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.ndt.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.ndt.setFont(font)
        self.ndt.setFrameShape(QtWidgets.QFrame.Box)
        self.ndt.setObjectName("ndt")
        self.verticalLayout_2.addWidget(self.ndt)
        self.alu = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.alu.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.alu.setFont(font)
        self.alu.setFrameShape(QtWidgets.QFrame.Box)
        self.alu.setObjectName("alu")
        self.verticalLayout_2.addWidget(self.alu)
        self.ci = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.ci.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.ci.setFont(font)
        self.ci.setFrameShape(QtWidgets.QFrame.Box)
        self.ci.setObjectName("ci")
        self.verticalLayout_2.addWidget(self.ci)
        self.stall = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.stall.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.stall.setFont(font)
        self.stall.setFrameShape(QtWidgets.QFrame.Box)
        self.stall.setObjectName("stall")
        self.verticalLayout_2.addWidget(self.stall)
        self.dh = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.dh.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.dh.setFont(font)
        self.dh.setFrameShape(QtWidgets.QFrame.Box)
        self.dh.setObjectName("dh")
        self.verticalLayout_2.addWidget(self.dh)
        self.ch = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.ch.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.ch.setFont(font)
        self.ch.setFrameShape(QtWidgets.QFrame.Box)
        self.ch.setObjectName("ch")
        self.verticalLayout_2.addWidget(self.ch)
        self.bm = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.bm.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.bm.setFont(font)
        self.bm.setFrameShape(QtWidgets.QFrame.Box)
        self.bm.setObjectName("bm")
        self.verticalLayout_2.addWidget(self.bm)
        self.sdh = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.sdh.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.sdh.setFont(font)
        self.sdh.setFrameShape(QtWidgets.QFrame.Box)
        self.sdh.setObjectName("sdh")
        self.verticalLayout_2.addWidget(self.sdh)
        self.sch = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.sch.setMinimumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.sch.setFont(font)
        self.sch.setFrameShape(QtWidgets.QFrame.Box)
        self.sch.setObjectName("sch")
        self.verticalLayout_2.addWidget(self.sch)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.parallel = QtWidgets.QComboBox(self.centralwidget)
        self.parallel.setGeometry(QtCore.QRect(770, 830, 241, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.parallel.setFont(font)
        self.parallel.setObjectName("parallel")
        self.parallel.addItem("")
        self.parallel.addItem("")
        self.cache = QtWidgets.QPushButton(self.centralwidget)
        self.cache.setGeometry(QtCore.QRect(480, 10, 111, 41))
        self.cache.setObjectName("cache")

        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.actionOff = QtWidgets.QAction(mainWindow)
        self.actionOff.setObjectName("actionOff")
        self.actionData_Forwarding = QtWidgets.QAction(mainWindow)
        self.actionData_Forwarding.setObjectName("actionData_Forwarding")
        self.actionStalling = QtWidgets.QAction(mainWindow)
        self.actionStalling.setObjectName("actionStalling")
        self.actionData_Forwarding_2 = QtWidgets.QAction(mainWindow)
        self.actionData_Forwarding_2.setObjectName("actionData_Forwarding_2")
        self.actionData_Stalling = QtWidgets.QAction(mainWindow)
        self.actionData_Stalling.setObjectName("actionData_Stalling")

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "MainWindow"))
        self.x0.setText(_translate("mainWindow", "x0 : "))
        self.x1.setText(_translate("mainWindow", "x1 :"))
        self.x2.setText(_translate("mainWindow", "x2 :"))
        self.x3.setText(_translate("mainWindow", "x3 : "))
        self.x4.setText(_translate("mainWindow", "x4 : "))
        self.x5.setText(_translate("mainWindow", "x5 :"))
        self.x6.setText(_translate("mainWindow", "x6 :"))
        self.x7.setText(_translate("mainWindow", "x7 :"))
        self.x8.setText(_translate("mainWindow", "x8 :"))
        self.x9.setText(_translate("mainWindow", "x9 :"))
        self.x10.setText(_translate("mainWindow", "x10 : "))
        self.x11.setText(_translate("mainWindow", "x11 :"))
        self.x12.setText(_translate("mainWindow", "x12 :"))
        self.x13.setText(_translate("mainWindow", "x13 :"))
        self.x14.setText(_translate("mainWindow", "x14 : "))
        self.x15.setText(_translate("mainWindow", "x15 :"))
        self.x16.setText(_translate("mainWindow", "x16 :"))
        self.x17.setText(_translate("mainWindow", "x17 :"))
        self.x18.setText(_translate("mainWindow", "x18 :"))
        self.x19.setText(_translate("mainWindow", "x19 :"))
        self.x20.setText(_translate("mainWindow", "x20 :"))
        self.x21.setText(_translate("mainWindow", "x21 : "))
        self.x22.setText(_translate("mainWindow", "x22 : "))
        self.x23.setText(_translate("mainWindow", "x23 : "))
        self.x24.setText(_translate("mainWindow", "x24 : "))
        self.x25.setText(_translate("mainWindow", "x25 : "))
        self.x26.setText(_translate("mainWindow", "x26 :"))
        self.x27.setText(_translate("mainWindow", "x27 : "))
        self.x28.setText(_translate("mainWindow", "x28 : "))
        self.x29.setText(_translate("mainWindow", "x29 : "))
        self.x30.setText(_translate("mainWindow", "x30 :"))
        self.x31.setText(_translate("mainWindow", "x31 :"))
        self.c1.setItemText(0, _translate("mainWindow", "Hex"))
        self.c1.setItemText(1, _translate("mainWindow", "Decimal"))
        self.c1.setItemText(2, _translate("mainWindow", "Unsigned"))
        self.c2.setItemText(0, _translate("mainWindow", "Hex"))
        self.c2.setItemText(1, _translate("mainWindow", "Decimal"))
        self.c2.setItemText(2, _translate("mainWindow", "Unsigned"))
        self.assemble.setText(_translate("mainWindow", "Assemble"))
        self.step.setText(_translate("mainWindow", "Step"))
        self.cyclestep.setText(_translate("mainWindow", "Cycle-Step"))
        self.run.setText(_translate("mainWindow", "Run"))
        self.fetch.setText(_translate("mainWindow", "Fetch : "))
        self.decode.setText(_translate("mainWindow", "Decode :"))
        self.execute.setText(_translate("mainWindow", "Execute : "))
        self.MA.setText(_translate("mainWindow", "Memory Access :"))
        self.RU.setText(_translate("mainWindow", "Register Update : "))
        self.label.setText(_translate("mainWindow", "Registers"))
        self.label_2.setText(_translate("mainWindow", "Output Window"))
        self.label_3.setText(_translate("mainWindow", "Memory"))
        self.cycles.setText(_translate("mainWindow", "Number of Cycles : "))
        self.ti.setText(_translate("mainWindow", "Total Instructions Executed :"))
        self.cpi.setText(_translate("mainWindow", "CPI : "))
        self.ndt.setText(_translate("mainWindow", "Number of Data-transfer : "))
        self.alu.setText(_translate("mainWindow", "Number of ALU Instructions : "))
        self.ci.setText(_translate("mainWindow", "Number of Control Instructions : "))
        self.stall.setText(_translate("mainWindow", "Number of Stalls/Bubbles : "))
        self.dh.setText(_translate("mainWindow", "Data Hazards : "))
        self.ch.setText(_translate("mainWindow", "Control Hazards : "))
        self.bm.setText(_translate("mainWindow", "Branch Mispredictions :"))
        self.sdh.setText(_translate("mainWindow", "Stalls due to Data Hazards :"))
        self.sch.setText(_translate("mainWindow", "Stalls due to Control Hazards :"))
        self.parallel.setItemText(0, _translate("mainWindow", "Pipeline - Stalling"))
        self.parallel.setItemText(1, _translate("mainWindow", "Pipeline - Data Forwarding"))

        self.actionOff.setText(_translate("mainWindow", "Off"))
        self.actionData_Forwarding.setText(_translate("mainWindow", "Data Forwarding"))
        self.actionStalling.setText(_translate("mainWindow", "Stalling"))
        self.actionData_Forwarding_2.setText(_translate("mainWindow", "Data Forwarding"))
        self.actionData_Stalling.setText(_translate("mainWindow", "Data Stalling"))
        self.cache.setText(_translate("mainWindow", "Cache"))

    def openWindow(self):
        self.window.show()



    def assemblechange(self,mainWindow):
        
        self.parallel.currentTextChanged.connect(self.assemblechange)
        temp=self.parallel.currentText()
        flag=-1
        if(temp=="Pipeline - Stalling"):
            flag=0
        else:
            flag=1
        self.assemble.clicked.connect(lambda: init("file.mc","0xffffc",flag))
        self.assemble.clicked.connect(self.registersfunc)
        self.assemble.clicked.connect(self.memory1)
        self.assemble.clicked.connect(self.codeend)
        

    def stepchange(self , mainWindow):
        self.step.clicked.connect(lambda: step())
        self.step.clicked.connect(self.registersfunc)
        self.step.clicked.connect(self.memory1)
        self.step.clicked.connect(self.output1)
        self.step.clicked.connect(self.stage_update)
        self.step.clicked.connect(self.codeend)
        # self.step.clicked.connect(self.cache_value_update)
        self.step.clicked.connect(self.update_rld)
        self.step.clicked.connect(self.update_rli)
        self.step.clicked.connect(self.update_dc)
        self.step.clicked.connect(self.update_ic)

    
    def cyclechange(self , mainWindow):
        self.cyclestep.clicked.connect(lambda: cycle_step())
        self.cyclestep.clicked.connect(self.registersfunc)
        self.cyclestep.clicked.connect(self.memory1)
        self.cyclestep.clicked.connect(self.output1)
        self.cyclestep.clicked.connect(self.stage_update)
        self.cyclestep.clicked.connect(self.codeend)
        # self.cyclestep.clicked.connect(self.cache_value_update)
        self.cyclestep.clicked.connect(self.update_rld)
        self.cyclestep.clicked.connect(self.update_rli)
        self.cyclestep.clicked.connect(self.update_dc)
        self.cyclestep.clicked.connect(self.update_ic)
        

    def runchange(self , mainWindow):
        self.run.clicked.connect(lambda :run_all())
        self.run.clicked.connect(self.registersfunc)   
        self.run.clicked.connect(self.memory1)
        self.run.clicked.connect(self.output1)
        self.run.clicked.connect(self.stage_update)
        self.run.clicked.connect(self.codeend)
        # self.run.clicked.connect(self.cache_value_update)
        self.run.clicked.connect(self.update_rld)
        self.run.clicked.connect(self.update_rli)
        self.run.clicked.connect(self.update_dc)
        self.run.clicked.connect(self.update_ic)

    
    def cachechange(self, mainWindow):
        #self.cache.clicked.connect(self.cache_value_update)
        self.cache.clicked.connect(self.update_rld)
        self.cache.clicked.connect(self.update_rli)
        self.cache.clicked.connect(self.update_dc)
        self.cache.clicked.connect(self.update_ic)

    def config(self,mainWindow):
        self.register_print()  #initialize register file   
        self.c1.currentTextChanged.connect(self.registersfunc)     #if c1 is clicked
        self.c2.currentTextChanged.connect(self.memory2)
        self.parallel.currentTextChanged.connect(self.assemblechange)
        self.cache.clicked.connect(self.openWindow)
 
        # self.exit.clicked.connect(self.pressexit)



    
    def codeend(self):
        if(last==1):
            global cpi
            global instruction_count
            global num_cycles
            global num_data_transfer
            global num_alu_inst
            global num_control
            global num_stalls
            global num_data_hazard
            global num_control_hazard
            global num_mis
            global num_stalls_data
            global num_stalls_control
            global num_instructions
            num_cycles += instruction_count
            cpi = num_cycles/num_instructions
            global values
            values = {'cycles':num_cycles,'instructions':num_instructions,'cpi':cpi,'data-transfer':num_data_transfer,'alu':num_alu_inst,'control':num_control,'stalls':num_stalls,'data-hazards':num_data_hazard,'control-hazards':num_control_hazard,'branch-mispredictions':num_mis,'stalls-data-hazards':num_stalls_data,'stalls-control-hazards':num_stalls_control, 'hit':hits,'miss':misses,'mem_access':hits+misses}

            self.value_update()
            self.cache_value_update()


    def stage_update(self):
        if(inst.get("f")!= None):
            self.fetch.setText("Fetch : " + inst["f"])
        else:
            self.fetch.setText("Fetch : ")
        if(inst.get("d")!= None):
            self.decode.setText("Decode : " + inst["d"])
        else:
            self.decode.setText("Decode : ")
        if(inst.get("e")!= None):
            self.execute.setText("Execute : " + inst["e"])
        else:
            self.execute.setText("Execute : ")
        if(inst.get("m")!= None):
            self.MA.setText("Memory Access : " + inst["m"])
        else:
            self.MA.setText("Memory Access : ")
        if(inst.get("r")!= None):
            self.RU.setText("Register Update : " + inst["r"])
        else:
            self.RU.setText("Register Update : ")



    def output1(self):
        data=open("output.txt")
        f=""
        for x in data:
            f=f+x
        self.output.setPlainText(f)
        data.close()


    def memory1(self):
        self.make_memory()
        strtemp=self.c2.currentText()
        if(strtemp=="Hex"):
            self.mh()
        elif(strtemp=="Decimal"):
            self.md()
        else:
            self.musg()  
        self.mem_print()     



    def memory2(self):
        strtemp=self.c2.currentText()
        if(strtemp=="Hex"):
            self.mh()
        elif(strtemp=="Decimal"):
            self.md()
        else:
            self.musg()       
        self.mem_print()

        


    def make_memory(self):
        tpdict.clear()
        for (x,y) in dict_data.items():
            temp=int(x,16)
            row=temp//4
            row=row*4
            col=temp%4
            col=3-col
            val=(256**col)*(int(y,16))
            if(tpdict.get(row)==None):
                tpdict[row]=val
            else:
                tpdict[row]+=val
        for (x,y) in tpdict.items():
            tpp[hex(x)]=hex(y)
    

    def mh(self):
        for (x,y) in tpdict.items():
            tpp[hex(x)]=hex(y)
    def musg(self):
        for (x,y) in tpdict.items():
            tpp[hex(x)]=(y+2**32 if y <0 else y)
    def md(self):
        for (x,y) in tpdict.items():
            tpp[hex(x)]=(y if y<(1<<31) else y-(1<<32))

        
    def mem_print(self):
        ans=""
        for (x,y) in tpp.items():
            temp= str(x)+": "+str(y)+"\n"
            ans=ans+temp
        self.memory.setPlainText(ans)

    def registersfunc(self):    #change format or updates the register value
        strtemp=self.c1.currentText()
        if(strtemp=="Hex"):
            self.converttohex()
        elif(strtemp=="Decimal"):
            self.converttodec()
        else:
            self.converttounsigned()
        self.register_print()
       
    def converttodec(self):
        tp = registers[:]
        for i in range(32):
            l[i]=(tp[i] if tp[i]<(1<<31) else tp[i]-(1<<32))

    def converttohex(self):
        tp = registers[:]
        for i in range(32):
            l[i]=hex(tp[i])  
    
    def converttounsigned(self):
        tp = registers[:]
        for i in range(32):
            l[i]=(tp[i]+2**32 if tp[i]<0 else tp[i])

    def value_update(self):

        self.cycles.setText("Cycles : " + str(values["cycles"]) )
        self.ti.setText("Instructions : "+ str(values["instructions"]))
        self.cpi.setText("CPI : "+ str(values["cpi"]))
        self.ndt.setText("Data-Transfer : "+ str(values["data-transfer"]))
        self.alu.setText("ALU : "+ str(values["alu"]))
        self.ci.setText("Control : "+ str(values["control"]))
        self.stall.setText("Stalls : "+ str(values["stalls"]))
        self.dh.setText("Data-Hazards : "+ str(values["data-hazards"]))
        self.ch.setText("Control-Hazards : "+ str(values["control-hazards"]))
        self.bm.setText("Branch-Misprecdictions : "+ str(values["branch-mispredictions"]))
        self.sdh.setText("Stalls-Data-Hazards : "+ str(values["stalls-data-hazards"]))
        self.sch.setText("Stalls-Control-Hazards : "+ str(values["stalls-control-hazards"]))

    def register_print(self):   
        self.x0.setText( "x0 : " + str(l[0]) )
        self.x1.setText(  "x1 : " + str(l[1]))
        self.x2.setText(   "x2 : "+ str(l[2]))
        self.x3.setText(   "x3 : " + str(l[3]))
        self.x4.setText(   "x4 : " + str(l[4]))
        self.x5.setText(   "x5 : "+ str(l[5]))
        self.x6.setText(   "x6 : " + str(l[6] ))
        self.x7.setText(   "x7 : " + str(l[7] ))
        self.x8.setText(   "x8 : " + str(l[8] ))
        self.x9.setText(   "x9 : " +str(l[9] ))
        self.x10.setText(   "x10 : " +str(l[10] ))
        self.x11.setText(   "x11 : " +str(l[11] ))
        self.x12.setText(   "x12 : " +str(l[12] ))
        self.x13.setText(   "x13 : " +str(l[13] ))
        self.x14.setText(   "x14 : " + str(l[14] ))
        self.x15.setText(   "x15 : " +str(l[15] ))
        self.x16.setText(   "x16 : " +str(l[16] ))
        self.x17.setText(   "x17 : " + str(l[17] ))
        self.x18.setText(   "x18 : "+ str(l[18] ))
        self.x19.setText(   "x19 : "+ str(l[19] ))
        self.x20.setText(   "x20 : "+ str(l[20] ))
        self.x21.setText(   "x21 : " + str(l[21] ))
        self.x22.setText(   "x22 : " + str(l[22] ))
        self.x23.setText(   "x23 : " +str(l[23] ))
        self.x24.setText(   "x24 : " +str(l[24] ))
        self.x25.setText(   "x25 : " + str(l[25] ))
        self.x26.setText(   "x26 : " +str(l[26] ))
        self.x27.setText(   "x27 : " +str(l[27] ))
        self.x28.setText(   "x28 : " +str(l[28] ))
        self.x29.setText(   "x29 : " +str(l[29] ))
        self.x30.setText(   "x30 : " +str(l[30] ))
        self.x31.setText(   "x31 : " +str(l[31] ))
    
    def cache_value_update(self):
        self.ui.hit.setText("Number of Hits : " + str(values["hit"]))
        self.ui.miss.setText("Number of Misses : " + str(values["miss"]))
        self.ui.mem_access.setText("Number of Memory Accesses : " + str(values["mem_access"]))

    def update_rld(self):
        ans=""
        for (x,y) in lru_data.items():
            temp= str(x)+": "+str(y)+"\n"
            ans=ans+temp
        self.ui.rlwd.setPlainText(ans)        
    def update_rli(self):
        ans=""
        for (x,y) in lru_inst.items():
            temp= str(x)+": "+str(y)+"\n"
            ans=ans+temp
        self.ui.rlwi.setPlainText(ans)        


    def update_dc(self):
        global n_asso
        ans=""
        for x in data_cache:
            cnt=0
            for y in x:
                temp='[ ' + str(y[0])+" : "+str(y[1]) +' ]'
                ans=ans+temp+"\n"
                cnt+=1
            left=n_asso-cnt
            for i in range(left):
                ans=ans+"[ EMPTY ]\n"
            ans=ans+"-------------------------------------\n"
        self.ui.dcw.setPlainText(ans)
                


    def update_ic(self):

        global n_asso
        ans=""
        for x in inst_cache:
            cnt=0
            for y in x:
                temp='[ ' + str(y[0])+" : "+str(y[1]) +' ]'
                ans=ans+temp+"\n"
                cnt+=1
            left=n_asso-cnt
            for i in range(left):
                ans=ans+"[ EMPTY ]\n"
            ans=ans+"-------------------------------------\n"
        self.ui.icw.setPlainText(ans)
        


    # def pressexit(self):
    #     sys.exit(app.exec_())




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    ui.config(mainWindow)
    ui.stepchange(mainWindow)
    ui.cyclechange(mainWindow)
    ui.runchange(mainWindow)
    ui.assemblechange(mainWindow)
    ui.cachechange(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())





















#----------------------------------------------












