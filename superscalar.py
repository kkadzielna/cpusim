import queue

class CPUSuperscalar:
    def __init__(self, mem_size=1024, reg_size=32):
        self.pipeline_registers = [None] * 10 
        self.mem_size = mem_size
        self.mem = [0] * mem_size
        self.reg_size = reg_size
        self.rf = [0] * reg_size
        self.pc = 0
        self.finished = False

# ----METRICS----
        self.cycle_cntr = 0
        self.instr_cntr = 0
# ----CONTROL DEPENDENCIES----
        self.control_dependency = False
        self.control_index = None
        self.pushed_op = queue.Queue()
        self.nop_counter = 0
        self.triplet_index = None

# -----------------------------------------------------------------------------------
# ----INSTRUCTION FUNCTIONS----
  
    def load(self, s1, r):
        self.rf[r] = self.mem[self.rf[s1]]

    def load_value(self, s1, r):
        self.rf[r] = self.mem[s1]
    
    def store(self, s1, r):
        self.mem[self.rf[s1]] = self.rf[r]

    def store_value(self, s1, r):
        self.mem[s1] = self.rf[r]
    
    def add(self, s1, s2, r):
        self.rf[r] = self.rf[s1] + self.rf[s2]

    def sub(self, s1, s2, r):
        self.rf[r] = self.rf[s1] - self.rf[s2]     

    def mul(self, s1, s2, r):
        self.rf[r] = self.rf[s1] * self.rf[s2]
    
    def _and(self, s1, s2, r):
        self.rf[r] = self.rf[s1] and self.rf[s2]
    
    def _or(self, s1, s2, r):
        self.rf[r] = self.rf[s1] or self.rf[s2]
    
    def jump(self, target_addr):
        self.pc = target_addr
    
    def branch_lt(self, s1, s2, target_addr):
        if self.rf[s1] < self.rf[s2]:
            self.pc = target_addr
    
    def branch_zero(self, s1, target_addr):
        if self.rf[s1] == 0:
            self.pc = target_addr
    
    def stop(self):
        self.finished = True
    
    def mov(self, s1, s2):
        self.rf[s1] = self.rf[s2]

    def cmp_lt(self, s1, s2, r):
        if self.rf[s1] < self.rf[s2]:
            self.rf[r] = True
        else:
            self.rf[r] = False
    
    def cmp_eq(self, s1, s2, r):
        if self.rf[s1] == self.rf[s2]:
            self.rf[r] = True
        else:
            self.rf[r] = False

    def nop(self):
        pass

# -----------------------------------------------------------------------------------
# ----PROCESSOR FUNCTIONS----

    def load_program(self, program):
        self.mem[0:len(program)] = program
        n = self.mem_size
        self.mem[900] = n-1
        self.mem[901] = n
        self.pc = 0

    def fetch(self):
        instr = self.mem[self.pc]
        self.pc += 1
        return instr

    def decode(self, instr):
        op = instr[0]
        if op == 'NOP':
            return self.nop,
        if op == 'LOAD':
            return self.load, instr[1], instr[2]
        elif op == 'VLOAD':
            return self.load_value, instr[1], instr[2]
        elif op == 'STORE':
            return self.store, instr[1], instr[2]
        elif op == 'VSTORE':
            return self.store_value, instr[1], instr[2]
        elif op == 'ADD':
            return self.add, instr[1], instr[2], instr[3]
        elif op == 'SUB':
            return self.sub, instr[1], instr[2], instr[3]
        elif op == 'MUL':
            return self.mul, instr[1], instr[2], instr[3]
        elif op == 'AND':
            return self._and, instr[1], instr[2], instr[3]
        elif op == 'OR':
            return self._or, instr[1], instr[2], instr[3]
        elif op == 'JUMP':
            return self.jump, instr[1]
        elif op == 'BRANCH_LT':
            return self.branch_lt, instr[1], instr[2], instr[3]
        elif op == 'BRANCH_ZERO':
            return self.branch_zero, instr[1], instr[2]
        elif op == 'STOP':
            return self.stop,
        elif op == 'MOV':
            return self.mov, instr[1], instr[2]
        elif op == 'CMP_LT':
            return self.cmp_lt, instr[1], instr[2], instr[3]
        elif op == 'CMP_EQ':
            return self.cmp_eq, instr[1], instr[2], instr[3]

    def execute(self, *operation):
        function = operation[0]
        if len(operation) > 1:
            args = operation[1:]
            function(*args)
        else:
            function()
        self.instr_cntr += 1 

# ------------------------------------------------------------------------------------
# ----DEPENDENCY HELPER FUNCTIONS----

# Get the all registers/memory locations used in one instruction (read and write)

    def get_used_registers(self, instruction):
        op, *operands = instruction
        used_registers = []

        if (op == 'LOAD' or op == 'STORE' or op == 'VLOAD' or op == 'VSTORE') and isinstance(operands[-2], int):
            used_registers.append(operands[-1])
        else:
            for operand in operands: 
                if isinstance(operand, int):
                    used_registers.append(operand)
        return used_registers

    def get_used_memories(self, instruction):
        op, *operands = instruction
        used_mem = []
        if (op == 'LOAD' or op == 'STORE') and isinstance(operands[-2], int):
            used_mem.append(operands[-2])
        return used_mem
    
    def get_used_value_memories(self, instruction):
        op, *operands = instruction
        used_vmem = []
        if (op == 'VLOAD' or op == 'VSTORE') and isinstance(operands[-2], int):
            used_vmem.append(operands[-2])
        return used_vmem

# Get all the registers/memory locations modified in the instructions in the pipeline (fetch stage) before the instruction of interest (write only)

    def get_modified_registers(self, j):
        modified_registers = set()
        modified_memory = set()
        modified_value_memory = set()

        # j here is provided by the caller and it's meant to be the index in the pipeline of the instruction of interest
        for i in range(0, j):
            prev_instruction = self.pipeline_registers[i]
            if prev_instruction is not None:
                op, *operands = prev_instruction 
                if op != 'STORE' and op != 'VSTORE' and op!= 'NOP' and op != 'STOP' and op != 'JUMP' and op != 'BRANCH_LT' and op != 'BRANCH_ZERO':
                    modified_registers.add(operands[-1])
                if op == 'STORE':
                    modified_memory.add(operands[-2])
                if op == 'VSTORE':
                    modified_value_memory.add(operands[-2])
        return modified_registers, modified_memory, modified_value_memory

# Check if any of the used registers/memory locations have been modified by the previus instructions in the pipeline 

    def has_dependencies(self, i, k, used_reg, used_mem, used_vmem):
        used_registers = used_reg[i]
        used_memories = used_mem[i]
        used_value_memories = used_vmem[i]
        modified_registers = self.get_modified_registers(k)[0]
        modified_memories = self.get_modified_registers(k)[1]
        modified_value_memories = self.get_modified_registers(k)[2]
        return any(reg in modified_registers for reg in used_registers) or any(mem in modified_memories for mem in used_memories) or any(vmem in modified_value_memories for vmem in used_value_memories)  

# -----------------------------------------------------------------------------------
# ----PIPELINE STAGES----

#pipeline registers 0, 1, 2 are holding fetched instructions. They're a fetch buffer esssentially
    def fetch_stage(self):
        for j in range(0,3):

            if self.pipeline_registers[j] == ('NOP',) and self.nop_counter > 0:
                self.nop_counter -= 1 
            elif not self.pushed_op.empty():
                self.pipeline_registers[j] = self.pushed_op.get()
            else:
                self.pipeline_registers[j] = self.fetch()

            instr = self.pipeline_registers[j]

            if instr is None or instr is 0:
                self.finished = True
                return
            
            # ----CONTROL DEPENDECIES---
            if instr[0] == 'JUMP':
                self.control_dependency = True
                self.control_dependency_index = self.pc - 1 
                self.addr_index = instr[-1]
                self.diff = abs(self.control_dependency_index - self.addr_index)
                self.triplet_index = j
            elif instr[0] == 'BRANCH_LT' and self.rf[instr[1]] < self.rf[instr[2]]:
                self.control_dependency = True
                self.control_dependency_index = self.pc
                self.addr_index = instr[-1]
                self.diff = abs(self.control_dependency_index - self.addr_index)
                self.triplet_index = j
            elif instr[0] == 'BRANCH_ZERO' and self.rf[instr[1]] == 0:
                self.control_dependency = True
                self.control_dependency_index = self.pc
                self.addr_index = instr[-1]
                self.diff = abs(self.control_dependency_index - self.addr_index)
                self.triplet_index = j


        # ---- DATA DEPENDENCIES----
        self.used_reg = []
        self.used_mem = []
        self.used_vmem = []
        self.has_dep = []
        i = 0
        # for each of the fetched instructions I get a bool: has dependency or doesn't 
        for instr in self.pipeline_registers[0:3]:
            
            temp_reg = self.get_used_registers(instr)
            temp_mem = self.get_used_memories(instr)
            temp_vmem = self.get_used_value_memories(instr)
            self.used_reg.append(temp_reg)
            self.used_mem.append(temp_mem)
            self.used_vmem.append(temp_vmem)
            self.has_dep.append(self.has_dependencies(i, i, self.used_reg, self.used_mem, self.used_vmem))                               
            
            i += 1


# pipeline registers 3, 4, 5 are holding decoded instructions
    def decode_stage(self):

        # a flag indicating whether there was a stall at the previous loop iteration (is the last decoded instruction in the pipeline a NOP)
        nop = False

        self.pushed_op = queue.Queue()
        j = 0
        for i in range(0,3):

            dependency_detected = False
            instruction = self.pipeline_registers[j]

            if instruction is None or instruction is 0: 
                self.finished = True
                return

 
            # ----DATA DEPENDENCIES----
            # if the instruction j has a dependency set the dependency detected flag to true 
            if self.has_dep[j]:
                dependency_detected = True

            # if there's a dependency in instruction j and flag indicating stall is false
            # insert a NOP at the curr slot in the pipeline (i+3)
            # set the stalling flag to true
            if dependency_detected and not nop:
                operation = self.decode(('NOP',))
                self.pipeline_registers.insert(i+3, operation)
                self.instr_cntr -= 1 
                nop = True      
            # if there is no dependency set stalling flag to false, insert decoded instruction into the pipeline
            # indicate instruction decoding progress
            else:
                nop = False
                operation = self.decode(instruction)
                self.pipeline_registers[i+3] = operation
                j += 1
        i+=1 

        for x in range(0,i-j):
            self.pushed_op.put(self.pipeline_registers[2-x])

        
#exectue executed the decoded instructions at registers 6, 7, 8
    def execute_stage(self):
        j = 0
        for j in range(3):
            operation = self.pipeline_registers[j+3]

            if operation is 0 or operation is None: 
                self.finished = True
                return
            
            # ----CONTROL DEPENDENCIES----
            if self.control_dependency:# and j == self.triplet_index:
                # for all already fetched and/or decoded instructions that are before it in the pipeline (ahead in the code) 
                # decode the instructions as nop, when the loop is finished decode the jump into pipeline at i+3
                diff_count = 0
                for n, prev_instr in enumerate(self.pipeline_registers[:j+6]):

                    if diff_count < self.diff: 
                        if self.pipeline_registers[n] == ("NOP",):
                            self.instr_cntr += 1 
                            #diff_count -= 1
                        if n > 2:
                            self.pipeline_registers[n] = self.decode(('NOP',))
                        else:
                            self.pipeline_registers[n] = ('NOP',)
                        self.instr_cntr -= 1 
                        diff_count += 1
                        self.nop_counter += 1
                    else:
                        break


                self.control_dependency = False
                break


            self.execute(*operation)


            if operation[0] == 'NOP':
                self.pipeline_registers[j+6] = None
            else:
                self.pipeline_registers[j+6] = self.pipeline_registers[j+7]
                self.pipeline_registers[j+7] = None


    def run(self):
        while not self.finished:
            self.fetch_stage()
            self.decode_stage()
            self.execute_stage()
            self.cycle_cntr += 1

        print('instructions: ' + str(self.instr_cntr))   
        print('cycles: ' + str(self.cycle_cntr))   
        print('instructions per cycle: ' + str(self.instr_cntr/self.cycle_cntr)) 
        instr =  float(self.instr_cntr)
        cycl = float(self.cycle_cntr)
        ipc = float(self.instr_cntr/self.cycle_cntr)
        return  instr, cycl, ipc
  #-----------------------------------------------------------------------------------          
            

