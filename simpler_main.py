import configparser
import os
import tempfile
import SIMPLER_Mapping
import ast
import json
import synopsys_dc
import time
from shutil import copyfile
import ntpath

def main():
  
    # Read configuration parameters
    config = configparser.ConfigParser()
    config.readfp(open('simpler_conf.cfg'))
    input_path = config.get('input_output', 'input_path')
    input_dir = config.get('input_output', 'input_dir')
    run_dir = config.getboolean('input_output', 'run_dir')
    input_format = config.get('input_output', 'input_format')
    #BenchmarkStrings = ast.literal_eval(config.get("SIMPLER_Mapping", "BenchmarkStrings"))
    Max_num_gates = config.getint('SIMPLER_Mapping', 'Max_num_gates')
    ROW_SIZE = [int(i) for i in ast.literal_eval(config.get("SIMPLER_Mapping", "ROW_SIZE"))]
    output_path = config.get('input_output', 'output_path')
    generate_json = config.getboolean('SIMPLER_Mapping', 'generate_json')
    print_mapping = config.getboolean('SIMPLER_Mapping', 'print_mapping')
    print_warnings = config.getboolean('SIMPLER_Mapping', 'print_warnings')
    
    if run_dir:
        input_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]
    else:
        input_paths = [input_path]
    
    syn_output_path = "syn_output_path.v"
    
    # Compile library
    synopsys_dc.compile_lib(synopsys_dc.SyntSet.set0)
    
    for path in input_paths:
        t1 = time.time()
        synopsys_dc.synt(path, syn_output_path)
        
        # Find multi-output cells and merge them
        SIMPLER_Mapping.mergeGates_HA(syn_output_path)
        SIMPLER_Mapping.mergeGates_HS("syn_output_path2.v")
        copyfile("syn_output_path2.v", "syn_res_dir/%s_%d.v" % (ntpath.basename(path), synopsys_dc.SyntSet.set0.value-1))
        
        # Mapping into the memory array
        #SIMPLER_Mapping.SIMPLER_Main([abc_output_path], Max_num_gates, ROW_SIZE, input_path.split(".")[0], generate_json, print_mapping, print_warnings)
        SIMPLER_Mapping.SIMPLER_Main(["syn_output_path3.v"], Max_num_gates, ROW_SIZE, path.split(".")[0], generate_json, print_mapping, print_warnings)
            

        # Clean files
        # os.remove(abc_output_path)
        t2 = time.time()
        print("Total execution time:", t2 - t1)
if __name__ == "__main__":
    main()
