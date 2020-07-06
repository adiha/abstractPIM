# abstractPIM
abstractPIM: Bridging the Gap Between Processing-In-Memory Technology and Instruction Set Architecture

## Dependencies
In order to use abstractPIM, you will need a Linux machine with:
1. Python 3.6
2. Synopsys DC

## Manual
1. Configure: in the file simple_conf.cfg you will find the following content:
```ini
[input_output]
; input_path - write the name of the input file 
input_path=full_adder_1bit.v
; input_format - the allowed values: verilog
input_format=verilog
; output_path - write the desired name of the netlist generated using Synopsys DC 
output_path=full_adder_1bit_output

[SIMPLER_Mapping]
; Max_num_gates - write the maximum number of gates the tool allows
Max_num_gates=20000
; ROW_SIZE - write all the desired row sizes (including the cells storing the inputs)
ROW_SIZE=[512,1024]
; generate_json,print_mapping,print_warnings - the allowed values: True/False 
generate_json=False
print_mapping=True
print_warnings=True

```
Change the parameters according to your needs.

2. Run:
```sh
python3 simpler_main.py
```