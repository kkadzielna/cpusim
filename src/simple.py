class CPUSimple:
    def __init__(self, mem_size=1024, reg_size=32):
        self.pipeline_registers = [None] * 5
        self.mem_size = mem_size
        self.mem = [0] * mem_size
        self.reg_size = reg_size
        self.rf = [0] * reg_size
        self.pc = 0
        self.finished = False
# ----METRICS----
        self.cycle_cntr = 0
        self.instr_cntr = 0

#-----------------------------------------------------------------------------------

    def load(self, s1, r):
        self.rf[r] = self.mem[self.rf[s1]]

    def load_value(self, s1, r):
        self.rf[r] = self.mem[s1]

    def add(self, s1, s2, r):
        self.rf[r] = self.rf[s1] + self.rf[s2]

    def sub(self, s1, s2, r):
        self.rf[r] = self.rf[s1] - self.rf[s2]     

    def mul(self, s1, s2, r):
        self.rf[r] = self.rf[s1] * self.rf[s2]
    
    def store(self, s1, r):
        self.mem[self.rf[s1]] = self.rf[r]

    def store_value(self, s1, r):
        self.mem[s1] = self.rf[r]
    
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
        self.cycle_cntr += 1
        return instr

    def decode(self, instr):
        op = instr[0]
        self.cycle_cntr += 1
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
        self.cycle_cntr += 1

#-----------------------------------------------------------------------------------

    def run(self):
        self.pc = 0
        self.finished = False
        while not self.finished: 
            instr = self.fetch()
            if instr is None:
                self.finished = True
                continue
            operation = self.decode(instr)
            self.execute(*operation)
        print('instructions: ' + str(self.instr_cntr))   
        print('cycles: ' + str(self.cycle_cntr))   
        print('instructions per cycle: ' + str(self.instr_cntr/self.cycle_cntr))   
        instr =  float(self.instr_cntr)
        cycl = float(self.cycle_cntr)
        ipc = float(self.instr_cntr/self.cycle_cntr)
        return  instr, cycl, ipc
#-----------------------------------------------------------------------------------






