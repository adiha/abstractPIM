from itertools import chain, combinations
import os
import tempfile
import re
import ntpath
from enum import Enum
import subprocess

SyntSet = Enum("SyntSet", "set0 set1 set2 set3 set4")

LIB_TEMPLATE = """
library(op_cond_all) {
  technology (cmos) ;
  delay_model : cmos2;
  time_unit : 1ns ;
  voltage_unit : 1V ;
  current_unit : 1mA ;
  capacitive_load_unit(1, pf);
  pulling_resistance_unit : 1ohm ;
  default_inout_pin_cap : 1.0 ;
  default_input_pin_cap : 1.0 ;
  default_output_pin_cap : 1.0 ;
  default_fanout_load : 10 ;
  
  leakage_power_unit : 1uW ;
  input_threshold_pct_fall : 50 ;
  input_threshold_pct_rise : 50 ;
  output_threshold_pct_fall : 50 ;
  output_threshold_pct_rise : 50 ;
  slew_derate_from_library : 0.75 ;
  slew_lower_threshold_pct_fall : 20 ;
  slew_lower_threshold_pct_rise : 20 ;
  slew_upper_threshold_pct_fall : 80 ;
  slew_upper_threshold_pct_rise : 80 ;
  in_place_swap_mode : match_footprint ;
  nom_process : 1 ;
  nom_temperature : 25 ;
  nom_voltage : 1.1 ;
  default_cell_leakage_power : 0 ;
  default_leakage_power_density : 0 ;
  default_intrinsic_rise : 0;
  default_intrinsic_fall : 0;
  
  wire_load("zero") {
resistance : 0;
capacitance : 0;
area : 1;
slope : 1;
fanout_length(1,2000);
}

CELLS
}
"""

CELL_TEMPLATE = """
cell(NAME) {
    area : AREA;
    dont_use : DONT_USE;
    INPUTS
    
    OUTPUTS
}
"""

INPUT_TEMPLATE = """
pin(PIN_NAME) {
      capacitance : 1.0 ;
      direction : input ;
    }
"""

OUTPUT_TEMPLATE = """
pin(PIN_NAME) {
    direction : output ;
    function : "FUNC" ;
    capacitance : 1.0 ;

    timing() {
      intrinsic_rise : RISE ;
      intrinsic_fall : FALL ;
      related_pin : "RELATED_PIN" ;
    }
}
"""

AND2 = """
type ( BUS2 ) {
 base_type : array ;
 data_type : bit ;
 bit_width : 2 ;
 bit_from : 1 ;
 downto : true ;
}

cell(c_and2_2) {
    area : 1;
    dont_use : false;
    bus (A) {
bus_type : BUS2 ;
direction : input ;
capacitance : 1 ;
}
bus (B) {
bus_type : BUS2 ;
direction : input ;
capacitance : 1 ;
}
bus (O) {
bus_type : BUS2 ;
direction : output ;
capacitance : 1 ;
function : "((A)&(B))" ;

    timing() {
      intrinsic_rise : 0 ;
      intrinsic_fall : 0 ;
      related_pin : "A B" ;
    }
    
       
}
}


"""

AND2_2 = """
cell(c_and2_3) {
    area : 1;
    single_bit_degenerate : "c_and2";
    dont_use : false;
pin(a0) {
      capacitance : 1.0 ;
      direction : input ;
    }
pin(a1) {
      capacitance : 1.0 ;
      direction : input ;
    }
pin(b0) {
      capacitance : 1.0 ;
      direction : input ;
    }
pin(b1) {
      capacitance : 1.0 ;
      direction : input ;
    }
pin(o0) {
    direction : output ;
    function : "a0&b0" ;

    timing() {
      intrinsic_rise : 0 ;
      intrinsic_fall : 0 ;
      related_pin : "a0 b0" ;
    }
}
pin(o1) {
    direction : output ;
    function : "a1&b1" ;

    timing() {
      intrinsic_rise : 0 ;
      intrinsic_fall : 0 ;
      related_pin : "a1 b1" ;
    }
}    
}
"""

# build_cell(name='name', area= area, inputs=['a', 'b'], outputs={'Y1: ['(!A)&(!B)', 'A B'], 'Y2' : [(!A)|(!B), 'A B']})
def build_cell(name, area, inputs, outputs, rise=0, fall=0, dont_use="false"):
    cell = CELL_TEMPLATE.replace("NAME", name).replace("AREA", str(area))
    cell_inputs = "\n".join([INPUT_TEMPLATE.replace("PIN_NAME", pin_name) for pin_name in inputs])
    cell_outputs = "\n".join([OUTPUT_TEMPLATE.replace("PIN_NAME", pin_name).replace("FUNC", l[0]).replace("RELATED_PIN", l[1]) for pin_name, l in outputs.items()])
    return cell.replace("INPUTS", cell_inputs).replace("OUTPUTS", cell_outputs).replace("RISE", str(rise)).replace("FALL", str(fall)).replace("DONT_USE", dont_use)
    
# The different opcodes that the controller supports and their latency
# MANDATORY_OPCODES_2 = [
    # build_cell(name="C_NOT_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    # build_cell(name="C_NOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
# ]

MANDATORY_OPCODES_2 = [
    #build_cell(name="C_NOT_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    #build_cell(name="C_NOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
]

# MANDATORY_OPCODES_3_4 = [
    # build_cell(name="C_NOT_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    # build_cell(name="C_NOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    # build_cell(name="C_NOR3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}),
    # build_cell(name="C_NOR4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}),
# ]

MANDATORY_OPCODES_3_4 = [
    # build_cell(name="C_NOT_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    # build_cell(name="C_NOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    # build_cell(name="C_NOR3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}),
    # build_cell(name="C_NOR4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}),
]

MANDATORY_OPCODES_3_4_BASIC_GATES = [
    # build_cell(name="C_NOT_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    # build_cell(name="C_NOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    # build_cell(name="C_NOR3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}),
    # build_cell(name="C_NOR4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}),
    
    # build_cell(name="C_AND2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}),
    # build_cell(name="C_AND3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)&(B)&(C)", "A B C"]}),
    # build_cell(name="C_AND4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)&(B)&(C)&(D)", "A B C D"]}),
    
    
    # build_cell(name="C_OR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    # build_cell(name="C_OR3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)|(B)|(C)", "A B C"]}),
    # build_cell(name="C_OR4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)|(B)|(C)|(D)", "A B C D"]}),
    
    
    # build_cell(name="C_XOR2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}),
    # build_cell(name="C_XOR3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"]}),
    # build_cell(name="C_XOR4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)^(B)^(C)^(D)", "A B C D"]}),
    
    
    # build_cell(name="C_NAND2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    # build_cell(name="C_NAND3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)|(!B)|(!C)", "A B C"]}),
    # build_cell(name="C_NAND4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)|(!B)|(!C)|(!D)", "A B C D"]}),
    
]


#OPCODES_BASIC = []

# Opcode timing when synthesizing with MANDATORY_OPCODES_2
# OPCODES_SET1 = [
    # build_cell(name="C_AND2_", area=3, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}),
    # build_cell(name="C_OR2_", area=2, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    # build_cell(name="C_XOR2_", area=5, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}),
    # build_cell(name="C_NAND2_", area=4, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
# ]

OPCODES_SET0 = [
    build_cell(name="c_inv1_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    #build_cell(name="c_nand2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    #build_cell(name="c_and2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}),
    #build_cell(name="c_or2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    build_cell(name="c_nor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    
]

OPCODES_SET1 = [
    build_cell(name="c_inv1_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}, rise=1, fall=1),
    build_cell(name="c_nor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}, rise=1, fall=1),
    build_cell(name="c_and2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}),
    build_cell(name="c_or2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    build_cell(name="c_xor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}),
    build_cell(name="c_xnor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["((A)&(B))|((!A)&(!B))", "A B"]}),
    build_cell(name="c_nand2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    build_cell(name="c_mux2to1_", area=1, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}, rise=0, fall=0),
    build_cell(name="c_mux4to1_", area=1, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}, rise=0, fall=0),
    build_cell(name="c_implies_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)|(B))", "A B"]}, rise=0, fall=0),
    build_cell(name="c_bout_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)&(B))", "A B"]}, rise=0, fall=0),
    #build_cell(name="c_xor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"]}),
]

OPCODES_SET2 = [
    build_cell(name="c_inv1_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}, rise=1, fall=1),
    build_cell(name="c_nor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}, rise=1, fall=1),
    build_cell(name="c_nor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}, rise=1, fall=1),
    build_cell(name="c_nor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}, rise=1, fall=1),
    build_cell(name="c_and2_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)&(B)&(C)", "A B C"]}),
    build_cell(name="c_and3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)&(B)&(C)", "A B C"]}),
    build_cell(name="c_and4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)&(B)&(C)&(D)", "A B C D"]}),
    build_cell(name="c_or2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    build_cell(name="c_or3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)|(B)|(C)", "A B C"]}),
    build_cell(name="c_or4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)|(B)|(C)|(D)", "A B C D"]}),
    build_cell(name="c_xor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}),
    build_cell(name="c_xor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"]}),
    build_cell(name="c_xor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)^(B)^(C)^(D)", "A B C D"]}),
    build_cell(name="c_xnor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["((A)&(B))|((!A)&(!B))", "A B"]}),
    build_cell(name="c_xnor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["((A)&(B)&(C))|((!A)&(!B)&(!C))", "A B C"]}),
    build_cell(name="c_xnor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["((A)&(B)&(C)&(D))|((!A)&(!B)&(!C)&(!D))", "A B C D"]}),
    build_cell(name="c_nand2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    build_cell(name="c_nand3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)|(!B)|(!C)", "A B C"]}),
    build_cell(name="c_nand4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)|(!B)|(!C)|(!D)", "A B C D"]}),
    build_cell(name="c_implies_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)|(B))", "A B"]}, rise=0, fall=0),
    build_cell(name="c_bout_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)&(B))", "A B"]}, rise=0, fall=0),
    build_cell(name="c_mux2to1_", area=1, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}, rise=0, fall=0),
    build_cell(name="c_mux4to1_", area=1, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}, rise=0, fall=0),
]

OPCODES_SET3 = [
    
    build_cell(name="c_inv1_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    build_cell(name="c_nor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    build_cell(name="c_nor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}),
    build_cell(name="c_nor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}),
    build_cell(name="c_and2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}),
    build_cell(name="c_and3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)&(B)&(C)", "A B C"]}),
    build_cell(name="c_and4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)&(B)&(C)&(D)", "A B C D"]}),
    build_cell(name="c_or2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}),
    build_cell(name="c_or3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)|(B)|(C)", "A B C"]}),
    build_cell(name="c_or4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)|(B)|(C)|(D)", "A B C D"]}),
    build_cell(name="c_xor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}),
    build_cell(name="c_xor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"]}),
    build_cell(name="c_xor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)^(B)^(C)^(D)", "A B C D"]}),
    build_cell(name="c_xnor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["((A)&(B))|((!A)&(!B))", "A B"]}),
    build_cell(name="c_xnor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["((A)&(B)&(C))|((!A)&(!B)&(!C))", "A B C"]}),
    build_cell(name="c_xnor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["((A)&(B)&(C)&(D))|((!A)&(!B)&(!C)&(!D))", "A B C D"]}),
    build_cell(name="c_nand2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    build_cell(name="c_nand3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)|(!B)|(!C)", "A B C"]}),
    build_cell(name="c_nand4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)|(!B)|(!C)|(!D)", "A B C D"]}),
    build_cell(name="c_implies_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)|(B))", "A B"]}, rise=0, fall=0),
    build_cell(name="c_bout_", area=1, inputs=["A", "B"], outputs={"Y1": ["((!A)&(B))", "A B"]}, rise=0, fall=0),
    build_cell(name="c_mux2to1_", area=1, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}, rise=0, fall=0),
    build_cell(name="c_mux4to1_", area=1, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}, rise=0, fall=0),
]

OPCODES_SET4 = [
    build_cell(name="c_inv1_", area=1, inputs=["A"], outputs={"Y1": ["(!A)", "A"]}),
    build_cell(name="c_nor2_", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)&(!B)", "A B"]}),
    build_cell(name="c_nor3_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)&(!B)&(!C)", "A B C"]}),
    build_cell(name="c_nor4_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)&(!B)&(!C)&(!D)", "A B C D"]}),
    #build_cell(name="c_and2", area=10000, inputs=["A", "B"], outputs={"Y1": ["(A)&(B)", "A B"]}, rise=5, fall=5),
    #build_cell(name="c_and3", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)&(B)&(C)", "A B C"]}, rise=1, fall=1),
    #build_cell(name="c_and4", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)&(B)&(C)&(D)", "A B C D"]}),
    #build_cell(name="c_or2", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)|(B)", "A B"]}, rise=5, fall=5),
    #build_cell(name="c_or3", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)|(B)|(C)", "A B C"]}),
    #build_cell(name="c_or4", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)|(B)|(C)|(D)", "A B C D"]}),
    #build_cell(name="c_xor2", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"]}, rise=5, fall=5),
    #build_cell(name="c_xor3", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"]}),
    #build_cell(name="c_xor4", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(A)^(B)^(C)^(D)", "A B C D"]}),
    #build_cell(name="c_xnor2", area=1, inputs=["A", "B"], outputs={"Y1": ["((A)&(B))|((!A)&(!B))", "A B"]}),
    #build_cell(name="c_xnor3", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["((A)&(B)&(C))|((!A)&(!B)&(!C))", "A B C"]}),
    #build_cell(name="c_xnor4", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["((A)&(B)&(C)&(D))|((!A)&(!B)&(!C)&(!D))", "A B C D"]}),
    #build_cell(name="c_nand2", area=1, inputs=["A", "B"], outputs={"Y1": ["(!A)|(!B)", "A B"]}),
    #build_cell(name="c_nand3", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(!A)|(!B)|(!C)", "A B C"]}),
    #build_cell(name="c_nand4", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["(!A)|(!B)|(!C)|(!D)", "A B C D"]}),
    # build_cell(name="c_xnor16", area=1, inputs=[
        # "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15",
        # "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", 
    # ], 
    # outputs={
        # "P0": ["!((A0)^(B0))", "A0 B0"], 
        # "P1": ["!((A1)^(B1))", "A1 B1"],
        # "P2": ["!((A2)^(B2))", "A2 B2"],
        # "P3": ["!((A3)^(B3))", "A3 B3"],
        # "P4": ["!((A4)^(B4))", "A4 B4"],
        # "P5": ["!((A5)^(B5))", "A5 B5"],
        # "P6": ["!((A6)^(B6))", "A6 B6"],
        # "P7": ["!((A7)^(B7))", "A7 B7"],
        # "P8": ["!((A8)^(B8))", "A8 B8"],
        # "P9": ["!((A9)^(B9))", "A9 B9"],
        # "P10": ["!((A10)^(B10))", "A10 B10"],
        # "P11": ["!((A11)^(B11))", "A11 B11"],
        # "P12": ["!((A12)^(B12))", "A12 B12"],
        # "P13": ["!((A13)^(B13))", "A13 B13"],
        # "P14": ["!((A14)^(B14))", "A14 B14"],
        # "P15": ["!((A15)^(B15))", "A15 B15"]
    # }, rise=0, fall=0),
    #build_cell(name="c_fa_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"], "Y2": ["((A)&(B))|((C)&((A)^(B)))", "A B C"]}, rise=0, fall=0),
    #build_cell(name="c_ha_", area=1, inputs=["A", "B"], outputs={"Y1": ["(A)^(B)", "A B"], "Y2": ["((A)&(B))", "A B"]}, rise=0, fall=0),
    #build_cell(name="c_mux2to1", area=1, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}, rise=0, fall=0),
    #build_cell(name="c_mux4to1", area=1, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}, rise=0, fall=0),
    #build_cell(name="c_sub", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["A ^ B ^ C", "A B C"], "Y2": ["((!A) & B) | (B & C) | (C & (!A))", "A B C"]}, rise=0, fall=0)
]

SETS = [OPCODES_SET0, OPCODES_SET1, OPCODES_SET2, OPCODES_SET3, OPCODES_SET4]

# OPCODES_SET3 = [
    # build_cell(name="C_FA_", area=11, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"], "Y2": ["((A)&(B))|((C)&((A)^(B)))", "A B C"]}),
    # build_cell(name="C_SUB_", area=14, inputs=["A", "B", "C"], outputs={"Y1": ["A ^ B ^ C", "A B C"], "Y2": ["((!A) & B) | (B & C) | (C & (!A))", "A B C"]}),
    # build_cell(name="C_MUX2to1_", area=4, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}),
    # build_cell(name="C_MUL2bit_", area=11, inputs=["A1", "A0", "B1", "B0"], outputs={"P0": ["((A0)&(B0))", "A0 B0"], 
                                                                                 # "P1": ["((A0)&(B1))^((A1)&(B0))", "A0 B0 A1 B1"], 
                                                                                 # "P2": ["((A1)&(B1))^((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                 # "P3": ["((A1)&(B1))&((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                # }),
# ]


OPCODES_SET3 = [
    # [
        # build_cell(name="C_FA_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"], "Y2": ["((A)&(B))|((C)&((A)^(B)))", "A B C"]}),
        # build_cell(name="C_HA_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)", "A B C"], "Y2": ["((A)&(B))", "A B"]}),
    # ],
    # [
       # build_cell(name="C_SUB_", area=1, inputs=["A", "B", "C"], outputs={"Y1": ["A ^ B ^ C", "A B C"], "Y2": ["((!A) & B) | (B & C) | (C & (!A))", "A B C"]}),
    # ],
    # [
        # build_cell(name="C_MUX2to1_", area=1, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}),
        # build_cell(name="C_MUX4to1_", area=1, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}),
    # ],
    # [
        # build_cell(name="C_MUL2bit_", area=1, inputs=["A1", "A0", "B1", "B0"], outputs={"P0": ["((A0)&(B0))", "A0 B0"], 
                                                                                 # "P1": ["((A0)&(B1))^((A1)&(B0))", "A0 B0 A1 B1"], 
                                                                                 # "P2": ["((A1)&(B1))^((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                 # "P3": ["((A1)&(B1))&((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                    # }),
    # ],
    # [
        # build_cell(name="C_AND_SUPER_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y1": ["((A)&(B))", "A B"], 
                                                                                   # "Y2": ["((A)&(B)&(C))", "A B C"], 
                                                                                   # "Y3": ["((A)&(B)&(C)&(D))", "A B C D"], 
                                                                                    # }),
    # ],
    # [
        # build_cell(name="C_OR_SUPER_", area=1, inputs=["A", "B", "C", "D"], outputs={ "Y4": ["((A)|(B))", "A B"], 
                                                                                   # "Y5": ["((A)|(B)|(C))", "A B C"], 
                                                                                   # "Y6": ["((A)|(B)|(C)|(D))", "A B C D"],
                                                                                    # }),
    # ],
    # [
        # build_cell(name="C_XOR_SUPER_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y7": ["((A)^(B))", "A B"], 
                                                                                   # "Y8": ["((A)^(B)^(C))", "A B C"], 
                                                                                   # "Y9": ["((A)^(B)^(C)^(D))", "A B C D"],
                                                                                    # }),
    # ],
    # [
        # build_cell(name="C_NAND_SUPER_", area=1, inputs=["A", "B", "C", "D"], outputs={"Y10": ["((!A)|(!B))", "A B"], 
                                                                                   # "Y11": ["((!A)|(!B)|(!C))", "A B C"], 
                                                                                   # "Y12": ["((!A)|(!B)|(!C)|(!D))", "A B C D"],
                                                                                    # }),
    # ]
]

# OPCODES_SET3 = [
    # [
        # build_cell(name="C_FA_", area=11, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)^(C)", "A B C"], "Y2": ["((A)&(B))|((C)&((A)^(B)))", "A B C"]}),
        # build_cell(name="C_HA_", area=5, inputs=["A", "B", "C"], outputs={"Y1": ["(A)^(B)", "A B C"], "Y2": ["((A)&(B))", "A B"]}),
    # ],
    # [
        # build_cell(name="C_SUB_", area=14, inputs=["A", "B", "C"], outputs={"Y1": ["A ^ B ^ C", "A B C"], "Y2": ["((!A) & B) | (B & C) | (C & (!A))", "A B C"]}),
    # ],
    # [
        # build_cell(name="C_MUX2to1_", area=4, inputs=["A", "B", "sel"], outputs={"Y1": ["((A)&(!sel))|((B)&(sel))", "A B sel"]}),
        # build_cell(name="C_MUX4to1_", area=13, inputs=["A", "B", "C", "D", "sel1", "sel0"], outputs={"Y1": ["((A)&(!sel1)&(!sel0))|((B)&(!sel1)&(sel0))|((C)&(sel1)&(!sel0))|((D)&(sel1)&(sel0))", "A B C D sel1 sel0"]}),
    # ],
    # [
        # build_cell(name="C_MUL2bit_", area=11, inputs=["A1", "A0", "B1", "B0"], outputs={"P0": ["((A0)&(B0))", "A0 B0"], 
                                                                                 # "P1": ["((A0)&(B1))^((A1)&(B0))", "A0 B0 A1 B1"], 
                                                                                 # "P2": ["((A1)&(B1))^((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                 # "P3": ["((A1)&(B1))&((A0)&(B1)&(A1)&(B0))", "A0 B0 A1 B1"],
                                                                                    # }),
    # ]
# ]

OPCODES = OPCODES_SET2 + OPCODES_SET3
#OPCODES = OPCODES_SET2
MANDATORY_OPCODES = MANDATORY_OPCODES_3_4

BENCHMARKS_DIR = "/home/adi/SIMPLER-MAGIC/EPFL"

BENCHMARKS = [
    #"/users/epadih/EPFL/arithmetic/adder/verilog/adder.v",
    #"/users/epadih/EPFL/arithmetic/max/verilog/max.v",
    #"/users/epadih/EPFL/arithmetic/bar/verilog/bar.v",
    #"/users/epadih/EPFL/arithmetic/sin/verilog/sin.v",
    #"/users/epadih/EPFL/random_control/decoder/verilog/dec.v",
    #"/users/epadih/EPFL/random_control/round_robin_arbiter/verilog/arbiter.v",
    #"/users/epadih/EPFL/random_control/int2float/verilog/int2float.v",
    "/users/epadih/EPFL/random_control/router/verilog/router.v",
    "/users/epadih/EPFL/random_control/priority/verilog/priority.v",
    "/users/epadih/EPFL/random_control/i2c/verilog/i2c.v",
    "/users/epadih/EPFL/random_control/alu_ctrl/verilog/ctrl.v",
    "/users/epadih/EPFL/random_control/voter/verilog/voter.v",
    "/users/epadih/EPFL/random_control/cavlc/verilog/cavlc.v",
]


RESULT_PATH = "new_results/output_set3_trans.txt"

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return list(chain.from_iterable(combinations(xs, n) for n in range(1, len(xs) + 1)))

def compile_lib(syntSet):
    # Create a Liberty library which includes a subset of the opcodes
    open("libs/gate_subset.lib", 'w').write(LIB_TEMPLATE.replace("CELLS", "\n".join(SETS[syntSet.value - 1])))
    
    # Compile library
    subprocess.run("dc_shell -f dc_scripts/compile_lib.dc", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
def synt(benchmark_fname, synt_output_path):
    
    # Create synthesis script
    synt_script = open("dc_scripts/synt.dc", 'r').read()
    synt_script = synt_script.replace('input.v', str(benchmark_fname))
    # synt_output_path = tempfile.mktemp()
    synt_script = synt_script.replace('output.v', synt_output_path)
    
    # Run synthesis script
    synt_script_path = "dc_scripts/synt_temp.dc"
    open(synt_script_path, "w").write(synt_script)
    subprocess.run('dc_shell -f "%s"' % synt_script_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    # Check the used opcodes and the total number of cycles
    synt_opcodes = []
    num_of_cycles = 0
    num_of_opcodes = 0
    
    # Extract the names of the gates from the gate subset
    # gate_names = [re.findall("cell\((.*?)\) ", op_decleration)[0] for op_decleration in gate_subset if op_decleration != ""]
    
    # for op_decleration in gate_subset:
        # if "cell" in op_decleration:
        
            # Extract the gate name and time from its declaration
            # op_name = re.findall("cell\((.*?)\) ", op_decleration)[0]
            # op_time = int(re.findall("area : (\d+?);", op_decleration)[0])
            # op_time = OPCODE_TIME[op_name]
            
            # If the opcode is in the netlist, add it to the synthesis opcode list
            # count_op = open(synt_output_path, 'r').read().count(op_name)
            # if (count_op != 0):
                # synt_opcodes.append(op_name)
                # num_of_opcodes += count_op
                # num_of_cycles += count_op * op_time
    
    # Write results
    #open(RESULT_PATH, "a").write("%s, %s, %d, %d\n" % (str(benchmark_fname.stem), str(synt_opcodes), num_of_opcodes, num_of_cycles))
    # open(RESULT_PATH, "a").write("%s, set=%s, trans=%d, cycles=%d\n" % (str(ntpath.basename(benchmark_fname)), SyntSet.namenum_of_opcodes, num_of_cycles))
    
    # Clean files
    # os.remove(synt_script_path)
    # os.remove(synt_output_path)
            
if __name__ == "__main__":
    main()
