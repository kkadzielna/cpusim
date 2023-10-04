## CPU simulator
### About
A simple simulation of a CPU written in Python. The simulation can act as either a simple, scalar, serial CPU, a pipelined CPU or a 3-way superscalar CPU. Dependencies and hazards are handled via flushing and stalling by inserting NOP instructions. The superscalar processor is currently unable to handle control dependencies.  
The benchmarks folder contains short programs written in MIPS inspired assembly language to be executed by the simulation.  
A more detailed description as well as a description of simple experiments conducted using the simulator are provided in the slides file.
### How to run
Programs can be executed by running the command "python3 main.py filename mode", where "filename" denotes the name of the file with the assembly code to be executed by the CPU simulation, while "mode" signifies the mode the CPU will be used in. The available modes are "simple", "pipelined" and "superscalar". The provided programs are "bubblesort.txt", "fibonacci.txt", "raw.txt" and "indepenent_artithmetic.txt".  The input to those programs is currently hardcoded and cannot be provided as an argument.  
