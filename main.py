import sys
import time

from simple import CPUSimple
from pipelined import CPUPipelined
from superscalar import CPUSuperscalar

if len(sys.argv) != 3:
    print("The correct command format is: python3 main.py program.txt mode")
else:
    filename =  sys.argv[1] 

    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    program = []
    for line in lines:
        elements = line.split(', ')
        instruction = elements[0]
        args = []
        for arg in elements[1:]:
            try:
                args.append(int(arg))
            except ValueError:
                args.append(arg)
        program.append((instruction, *args))


    mode = sys.argv[2]
    if mode == 'simple':
        cpu = CPUSimple()
    elif mode == 'pipelined':
        cpu = CPUPipelined()
    elif mode == 'superscalar':
        cpu = CPUSuperscalar()
    else:
        print('mode argument must be one of: simple, pipelined or superscalar')
    #what about values in memory to work on?    
    cpu.load_program(program)

    if sys.argv[1] == 'bubblesort.txt':
        unsorted_array = [3, 2, 8, 1, 9]
        cpu.mem[cpu.mem_size-1] = len(unsorted_array)
        cpu.mem[cpu.mem_size-2] = len(unsorted_array) - 1

        for i, val in enumerate(unsorted_array):
            cpu.mem[cpu.mem_size-3 - i] = val

    elif sys.argv[1] == 'fibonacci.txt':
        number = 10
        cpu.mem[cpu.mem_size-1] = number
    
    elif sys.argv[1] == 'raw.txt' or sys.argv[1] == 'independent_arithmetic.txt':
        cpu.mem[cpu.mem_size-10:cpu.mem_size] = [1]*10

    start_time = time.time()
    cpu.run()
    end_time = time.time()

    if sys.argv[1] == 'bubblesort.txt':
        sorted_array = [cpu.mem[cpu.mem_size-3 - i] for i in range(len(unsorted_array))]
        print('Unsorted: ' + str(unsorted_array))
        print('Sorted: ' + str(sorted_array))
        

    elif sys.argv[1] == 'fibonacci.txt':
        print('Fibonacci sequence for n = ' + str(number) + ': ' + str(cpu.mem[cpu.mem_size-1-number:cpu.mem_size-1]))


    print(f"Execution time: {end_time - start_time:.6f} seconds")