''' 
This file contains an implementation of the SIMPLER algorithm.

Written by:
    Rotem Ben-Hur - rotembenhur@campus.technion.ac.il
    Ronny Ronen - 
    Natan Peled - natanpeled@campus.technion.ac.il

The "RUN TIME parameters" part includes the next parameters:
    ROW_SIZE - a list of row sizes to run the algorithm with.
    JSON_CODE_GEN - to create an execution sequence JSON file, set this flag to TRUE.
    PRINT_CODE_GEN - to enable information print, set the flag to True. 
    PRINT_WARNING - to enable warnings print, set the flag to True.
    Max_num_gates - the maximum number of gates the tool generates a mapping to 
    SORT_ROOTS - for arbitrary roots order set to 'NO'. For ascending roots order (by CU value) set to 'ASCEND'.
                 For descending roots order (by CU value) set to 'DESCEND'.

''' 

#import numpy as np
import simplejson
from collections import OrderedDict
import time
import re
from collections import OrderedDict
import itertools
import math
import copy

#================ Globals variables and Classes =================

GATE_TIME_NOR4 = {
     "c_nor2_" : 1,
     "c_nor3_" : 1,
     "c_nor4_" : 1,
     "c_inv1_" : 1,
     "c_and2_" : 3,
     "c_or2_" : 2,
     "c_nand2_" : 4,
     "c_xor2_" : 6,
     "c_bout_" : 2,
     "c_implies_" : 3,
     "c_xnor2_" : 5,
     "c_and3_" : 4,
     "c_or3_" : 2,
     "c_nand3_" : 5,
     "c_xor3_" : 11,
     "c_xnor3_" : 7,
     "c_and4_" : 5,
     "c_or4_" : 2,
     "c_nand4_" : 6,
     "c_xor4_" : 14,
     "c_xnor4_" : 8,
     "c_ha_" : 7,
     "c_hs_" : 6,
     "c_mux2to1_" : 7,
     "c_mux4to1_" : 16,
}


GATE_TIME_NOT_AND_OR = {
    "c_nor2_" : 2,
    "c_nor3_" : 3,
    "c_nor4_" : 4,
    "c_inv1_" : 1,
    "c_and2_" : 1,
    "c_or2_" : 1,
    "c_nand2_" : 2,
    "c_xor2_" : 5,
    "c_bout_" : 2,
    "c_implies_" : 2,
    "c_xnor2_" : 5,
    "c_and3_" : 2,
    "c_or3_" : 2,
    "c_nand3_" : 3,
    "c_xor3_" : 9,
    "c_xnor3_" : 6,
    "c_and4_" : 3,
    "c_or4_" : 3,
    "c_nand4_" : 4,
    "c_xor4_" : 15,
    "c_xnor4_" : 8,
    "c_ha_" : 6,
    "c_hs_" : 5,
    "c_mux2to1_" : 4,
    "c_mux4to1_" : 11,
}

GATE_TIME_NOT_NOR_AND_OR = {
    "c_nor2_" : 1,
    "c_nor3_" : 2,
    "c_nor4_" : 3,
    "c_inv1_" : 1,
    "c_and2_" : 1,
    "c_or2_" : 1,
    "c_nand2_" : 2,
    "c_xor2_" : 4,
    "c_bout_" : 2,
    "c_implies_" : 2,
    "c_xnor2_" : 4,
    "c_and3_" : 2,
    "c_or3_" : 2,
    "c_nand3_" : 3,
    "c_xor3_" : 7,
    "c_xnor3_" : 5,
    "c_and4_" : 3,
    "c_or4_" : 3,
    "c_nand4_" : 4,
    "c_xor4_" : 11,
    "c_xnor4_" : 7,
    "c_ha_" : 7,
    "c_hs_" : 7,
    "c_mux2to1_" : 4,
    "c_mux4to1_" : 10,
}


GATE_INTERMEDIATE_CALC_CELLS_NOT_NOR_AND_OR = {
    "c_nor2_" : 0,
    "c_nor3_" : 1,
    "c_nor4_" : 2,
    "c_inv1_" : 0,
    "c_and2_" : 0,
    "c_or2_" : 0,
    "c_nand2_" : 1,
    "c_xor2_" : 3,
    "c_bout_" : 1,
    "c_implies_" : 1,
    "c_xnor2_" : 3,
    "c_and3_" : 1,
    "c_or3_" : 1,
    "c_nand3_" : 2,
    "c_xor3_" : 6,
    "c_xnor3_" : 4,
    "c_and4_" : 2,
    "c_or4_" : 2,
    "c_nand4_" : 3,
    "c_xor4_" : 10,
    "c_xnor4_" : 6,
    "c_ha_" : 5,
    "c_hs_" : 5,
    "c_mux2to1_" : 3,
    "c_mux4to1_" : 9,
}


GATE_TIME_NOT_NOR = {
    "c_nor2_" : 1,
    "c_nor3_" : 3,
    "c_nor4_" : 5,
    "c_inv1_" : 1,
    "c_and2_" : 3,
    "c_or2_" : 2,
    "c_nand2_" : 4,
    "c_xor2_" : 6,
    "c_bout_" : 2,
    "c_implies_" : 2,
    "c_xnor2_" : 5,
    "c_and3_" : 6,
    "c_or3_" : 4,
    "c_nand3_" : 7,
    "c_xor3_" : 11,
    "c_xnor3_" : 11,
    "c_and4_" : 9,
    "c_or4_" : 6,
    "c_nand4_" : 10,
    "c_xor4_" : 16,
    "c_xnor4_" : 16,
    "c_ha_" : 7,
    "c_hs_" : 6,
    "c_mux2to1_" : 7,
    "c_mux4to1_" : 16,
}

GATE_TIME_ALL234 = {
    "c_nor2_" : 1,
    "c_nor3_" : 1,
    "c_nor4_" : 1,
    "c_inv1_" : 1,
    "c_and2_" : 1,
    "c_or2_" : 1,
    "c_nand2_" : 1,
    "c_xor2_" : 1,
    "c_bout_" : 1,
    "c_implies_" : 1,
    "c_xnor2_" : 1,
    "c_and3_" : 1,
    "c_or3_" : 1,
    "c_nand3_" : 1,
    "c_xor3_" : 1,
    "c_xnor3_" : 1,
    "c_and4_" : 1,
    "c_or4_" : 1,
    "c_nand4_" : 1,
    "c_xor4_" : 1,
    "c_xnor4_" : 1,
    "c_ha_" : 2,
    "c_hs_" : 2,
    "c_mux2to1_" : 1,
    "c_mux4to1_" : 1,
}

GATE_INTERMEDIATE_CALC_CELLS_ALL234 = {
     "c_nor2_" : 0,
     "c_nor3_" : 0,
     "c_nor4_" : 0,
     "c_inv1_" : 0,
     "c_and2_" : 0,
     "c_or2_" : 0,
     "c_nand2_" : 0,
     "c_xor2_" : 0,
     "c_bout_" : 0,
     "c_implies_" : 0,
     "c_xnor2_" : 0,
     "c_and3_" : 0,
     "c_or3_" : 0,
     "c_nand3_" : 0,
     "c_xor3_" : 0,
     "c_xnor3_" : 0,
     "c_and4_" : 0,
     "c_or4_" : 0,
     "c_nand4_" : 0,
     "c_xor4_" : 0,
     "c_xnor4_" : 0,
     "c_ha_" : 0,
     "c_hs_" : 0,
     "c_mux2to1_" : 0,
     "c_mux4to1_" : 0,
}

GATE_TIME_NOT_NOR_AND_OR_234 = {
    "c_nor2_" : 1,
    "c_nor3_" : 1,
    "c_nor4_" : 1,
    "c_inv1_" : 1,
    "c_and2_" : 1,
    "c_or2_" : 1,
    "c_nand2_" : 2,
    "c_xor2_" : 4,
    "c_bout_" : 2,
    "c_implies_" : 2,
    "c_xnor2_" : 4,
    "c_and3_" : 1,
    "c_or3_" : 1,
    "c_nand3_" : 2,
    "c_xor3_" : 7,
    "c_xnor3_" : 3,
    "c_and4_" : 1,
    "c_or4_" : 1,
    "c_nand4_" : 2,
    "c_xor4_" : 11,
    "c_xnor4_" : 3,
    "c_ha_" : 3,
    "c_hs_" : 3,
    "c_mux2to1_" : 4,
    "c_mux4to1_" : 10,
}

GATE_INTERMEDIATE_CALC_CELLS_NOT_AND_OR_234 = {
     "c_nor2_" : 0,
     "c_nor3_" : 0,
     "c_nor4_" : 0,
     "c_inv1_" : 0,
     "c_and2_" : 0,
     "c_or2_" : 0,
     "c_nand2_" : 1,
     "c_xor2_" : 3,
     "c_bout_" : 1,
     "c_implies_" : 1,
     "c_xnor2_" : 3,
     "c_and3_" : 0,
     "c_or3_" : 0,
     "c_nand3_" : 1,
     "c_xor3_" : 6,
     "c_xnor3_" : 2,
     "c_and4_" : 0,
     "c_or4_" : 0,
     "c_nand4_" : 1,
     "c_xor4_" : 10,
     "c_xnor4_" : 2,
     "c_ha_" : 1,
     "c_hs_" : 1,
     "c_mux2to1_" : 3,
     "c_mux4to1_" : 9,
}

GATE_TIME = GATE_TIME_NOT_NOR

# Initialization cycles
GATE_TIME.update((x, y+1) for x, y in GATE_TIME.items())

GATE_INTERMEDIATE_CALC_CELLS_NOR4 = {
     "c_nor2_" : 0,
     "c_nor3_" : 0,
     "c_nor4_" : 0,
     "c_inv1_" : 0,
     "c_and2_" : 2,
     "c_or2_" : 1,
     "c_nand2_" : 3,
     "c_xor2_" : 5,
     "c_bout_" : 1,
     "c_implies_" : 2,
     "c_xnor2_" : 4,
     "c_and3_" : 3,
     "c_or3_" : 1,
     "c_nand3_" : 4,
     "c_xor3_" : 10,
     "c_xnor3_" : 6,
     "c_and4_" : 4,
     "c_or4_" : 1,
     "c_nand4_" : 5,
     "c_xor4_" : 13,
     "c_xnor4_" : 7,
     "c_ha_" : 5,
     "c_hs_" : 4,
     "c_mux2to1_" : 6,
     "c_mux4to1_" : 15,
}

GATE_INTERMEDIATE_CALC_CELLS_NOT_AND_OR = {
    "c_nor2_" : 1,
    "c_nor3_" : 2,
    "c_nor4_" : 3,
    "c_inv1_" : 0,
    "c_and2_" : 0,
    "c_or2_" : 0,
    "c_nand2_" : 1,
    "c_xor2_" : 4,
    "c_bout_" : 1,
    "c_implies_" : 1,
    "c_xnor2_" : 4,
    "c_and3_" : 1,
    "c_or3_" : 1,
    "c_nand3_" : 2,
    "c_xor3_" : 8,
    "c_xnor3_" : 5,
    "c_and4_" : 2,
    "c_or4_" : 2,
    "c_nand4_" : 3,
    "c_xor4_" : 14,
    "c_xnor4_" : 7,
    "c_ha_" : 4,
    "c_hs_" : 3,
    "c_mux2to1_" : 3,
    "c_mux4to1_" : 10,
}

GATE_INTERMEDIATE_CALC_CELLS_NOT_NOR = {
    "c_nor2_" : 1,
    "c_nor3_" : 2,
    "c_nor4_" : 4,
    "c_inv1_" : 0,
    "c_and2_" : 2,
    "c_or2_" : 1,
    "c_nand2_" : 3,
    "c_xor2_" : 5,
    "c_bout_" : 1,
    "c_implies_" : 1,
    "c_xnor2_" : 4,
    "c_and3_" : 5,
    "c_or3_" : 3,
    "c_nand3_" : 6,
    "c_xor3_" : 10,
    "c_xnor3_" : 10,
    "c_and4_" : 8,
    "c_or4_" : 5,
    "c_nand4_" : 9,
    "c_xor4_" : 15,
    "c_xnor4_" : 15,
    "c_ha_" : 5,
    "c_hs_" : 4,
    "c_mux2to1_" : 6,
    "c_mux4to1_" : 15,
}

GATE_INTERMEDIATE_CALC_CELLS = GATE_INTERMEDIATE_CALC_CELLS_NOT_NOR

GATE_NUM_OF_OUTS = {
    "c_nor2_" : 1,
    "c_nor3_" : 1,
    "c_nor4_" : 1,
    "c_inv1_" : 1,
    "c_and2_" : 1,
    "c_or2_" : 1,
    "c_nand2_" : 1,
    "c_xor2_" : 1,
    "c_bout_" : 1,
    "c_implies_" : 1,
    "c_xnor2_" : 1,
    "c_and3_" : 1,
    "c_or3_" : 1,
    "c_nand3_" : 1,
    "c_xor3_" : 1,
    "c_xnor3_" : 1,
    "c_and4_" : 1,
    "c_or4_" : 1,
    "c_nand4_" : 1,
    "c_xor4_" : 1,
    "c_xnor4_" : 1,
    "c_ha_" : 2,
    "c_hs_" : 2,
    "c_mux2to1_" : 1,
    "c_mux4to1_" : 1,
}

# BITWISE_VER = {
    # "c_nor2" : "c_bw16_nor2",
    # "c_inv1" : "c_bw16_inv1",
    # "c_and2" : "c_bw16_and2",
    # "c_or2" : "c_bw16_or2",
    # "c_nand2" : "c_bw16_nand2",
    # "c_xor2" : "c_bw16_xor2",
    # "c_xnor2" : "c_bw16_xnor2",   
# }

# BITWISE_FORMAT = {
    # "c_bw16_nor2" : "c_bw16_nor2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_inv1" : "c_bw16_inv1 %s ( .A1(%s), .A2(%s), .A3(%s), .A4(%s) .A5(%s), .A6(%s), .A7(%s), .A8(%s), .A9(%s), .A10(%s), .A11(%s), .A12(%s), .A13(%s), .A14(%s), .A15(%s), .A16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_and2" : "c_bw16_and2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_or2" : "c_bw16_or2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_nand2" : "c_bw16_nand2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_xor2" : "c_bw16_xor2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",
    # "c_bw16_xnor2" : "c_bw16_xnor2 %s ( .A1(%s), .B1(%s), .A2(%s), .B2(%s), .A3(%s), .B3(%s), .A4(%s), .B4(%s), .A5(%s), .B5(%s), .A6(%s), .B6(%s), .A7(%s), .B7(%s), .A8(%s), .B8(%s), .A9(%s), .B9(%s), .A10(%s), .B10(%s), .A11(%s), .B11(%s), .A12(%s), .B12(%s), .A13(%s), .B13(%s), .A14(%s), .B14(%s), .A15(%s), .B15(%s), .A16(%s), .B16(%s), .Y1(%s), .Y2(%s), .Y3(%s), .Y4(%s), .Y5(%s), .Y6(%s), .Y7(%s), .Y8(%s), .Y9(%s), .Y10(%s), .Y11(%s), .Y12(%s), .Y13(%s), .Y14(%s), .Y15(%s), .Y16(%s) );",   
# }

class GraphEdge:

    def __init__(self,Source,Dest,Val):
        self.s = Source
        self.d = Dest
        self.v = Val

    def GetDest(self):
        return self.d

    def GetSource(self):
        return self.s

    def GetVal(self):
        return self.v

    def Print(self):
        print('(' + str(self.s) + ',' + str(self.d) + '), edge val is:' + str(self.v))

class NodeData:
    
    #Op declarations 
    No_inputs = 'NO INPUTS'
    Input = 'INPUT'
    Initialization = 'INITIALIZATION'
    
    #Class methods:        
    @classmethod
    def Get_no_inputs_op_val(cls):
        return cls.No_inputs
    
    @classmethod
    def Get_Input_op_val(cls):
        return cls.Inputs
    
    @classmethod
    def Get_Initialization_op_val(cls):
        return cls.Initialization
    
    def __init__(self,Num,Op='',Inputs_list=[],Time=0):
        self.node_num = Num 
        self.op = Op
        self.val = False
        self.FO = 0
        self.CU = 0
        self.map = []
        self.inputs_list = Inputs_list
        self.time = Time
        self.SIMPLER_lists_node = None

        self.out_edges = []
        self.in_edges = []
        self.num_of_out_edges = 0
        self.num_of_in_edges = 0
        self.intermediateCells = []
        self.output_list = []
        self.input_list = []

    def SetNodeNum(self,Num):
        self.node_num = Num
    
    def GetNodeNum(self):
        return self.node_num
        
    def SetNodeOp(self,Op):
        self.op = Op
        
    def GetNodeOp(self):
        return self.op
        
    def SetNodeCu(self,Val):
        self.CU = Val
    
    def GetNodeCu(self):
        return self.CU

    def SetNodeFO(self,Val):
        self.FO = Val
    
    def GetNodeFO(self):
        return self.FO
        
    def SetNodeMap(self,ValList):
        self.map = ValList
        
    def GetNodeMap(self):
        return self.map
    
    def GetNodeTime(self):
        return self.time

    def SetNodeInputs_list(self,Inputs):
        self.inputs_list = Inputs
        
    def GetNodeInputs_list(self):
        return self.inputs_list        

    def InsertInputNode(self):
        #Creates a node who describes a net input
        self.inputs_list = []
        self.op = self.Input        
        self.map = self.node_num
        self.time = 0

    def Insert_readoperations_parameters(self,NodeNum,InputIdxs,Op):
        self.node_num = NodeNum
        self.inputs_list = InputIdxs
        self.op = Op
        
    def Insert_AllocateCell_parameters(self,cell,time):
        self.time = time
        self.map = cell
        
    def Insert_No_Input_Node(self,NodeNum):
        #Inserts a line who describes a gate/wire who doesn't have inputs
        self.node_num = NodeNum
        self.inputs_list = []
        self.op = self.No_inputs        
        self.map = -1 
        self.time = 0   

    def Set_SIMPLER_lists_node(self,ref):
        print(ref)
        self.SIMPLER_lists_node = ref

    def Get_SIMPLER_lists_node(self):
        return self.SIMPLER_lists_node
        
    def PrintNodeData(self):
        print('node_num =',self.node_num,'inputs_list =',self.inputs_list,'op =',self.op,'cell =',self.map,'time =',self.time,'CU =',self.CU,'FO =',self.FO)

    def AddOutEdge(self,Dest,Val):
        self.out_edges.append(GraphEdge(self.node_num,Dest,Val))
        self.num_of_out_edges += 1

    def AddInEdge(self,Source,Val):
        self.in_edges.append(GraphEdge(Source,self.node_num,Val))
        self.num_of_in_edges += 1
        
    def RemoveOutEdge(self,Dest):
        for i,e in enumerate(self.out_edges):
            if e.GetDest() == Dest:
                del self.out_edges[i]
                self.num_of_out_edges -= 1
                break

    def RemoveInEdge(self,Source):
        for i,e in enumerate(self.in_edges):
            if e.GetSource() == Source:
                del self.in_edges[i]
                self.num_of_in_edges -= 1
                break

    def GetNumOfOutEdges(self):
        return self.num_of_out_edges

    def GetNumOfInEdges(self):
        return self.num_of_in_edges

    def GetOutEdgesList(self,TrueDepFlag):
        if TrueDepFlag:
            return [e.GetDest() for e in self.out_edges if e.GetVal()==1]
        else:
            return [e.GetDest() for e in self.out_edges]

    def GetInEdgesList(self,TrueDepFlag):
        if TrueDepFlag:
            L = [e.GetSource() for e in self.in_edges if e.GetVal()==1]
            L.reverse()
            return L
        else:
            return [e.GetSource() for e in self.in_edges]

class CellInfo:
    
    #States declarations 
    Available = 1 #The cell was allocated and available again
    Used = 2 #The cell is in use
    Init = 3 #The cell is not in use, but need to initialized  
    
    #Global class parameters 
    max_num_of_used_cells = 0
    cur_num_of_used_cells = 0

    #Class methods:     
    @classmethod
    def Set_max_num_of_used_cells_to_zero(cls):
        cls.max_num_of_used_cells = 0
    
    @classmethod    
    def get_max_num_of_used_cells(cls):
        return cls.max_num_of_used_cells

    @classmethod    
    def Set_cur_num_of_used_cells_to_zero(cls):
        cls.cur_num_of_used_cells = 0   

    #End of class methods
    
    def __init__(self,Idx):
        self.state = CellInfo.Available
        #self.current_gate = -1
        self.next = None
        self.prev = None
        self.cell_idx = Idx
        self.current_gate_num = None

    def GetCellIdx(self):
        return self.cell_idx

    def SetNext(self,idx):
        self.next = idx
        
    def SetPrev(self,idx):
        self.prev = idx

    def GetNext(self):
        return self.next
        
    def GetPrev(self):
        return self.prev

    def SetCurGateNum(self,gate_num):
        self.current_gate_num = gate_num

    def GetCurGateNum(self):
        return self.current_gate_num



class CellsInfo:

    def __init__(self,N):
        self.used_head = None
        self.used_tail = None
        self.init_head = None
        self.init_tail = None
        self.available_head = None
        self.available_tail = None
        self.cells = [CellInfo(idx) for idx in range(0,N)]
        self.init_list_for_json = []

    #Available list methods
    def GetFirst_Available(self):
        if self.available_head == None:
            return None
        else:
            return self.cells[self.available_head].GetCellIdx()

    def Concatenate_init_to_available_list(self):
        self.available_head = self.init_head
        self.available_tail = self.init_tail
        self.cells[self.available_tail].SetNext(None)
        self.cells[self.available_head].SetPrev(None)
        self.init_head = None
        self.init_tail = None

    def DeleteFirst_Available(self):
        if self.available_head == self.available_tail:
            self.cells[self.available_head].SetNext(None)
            self.cells[self.available_head].SetPrev(None)
            self.available_head = self.available_tail = None
        else:
            next_available_cell = self.cells[self.available_head].GetNext()
            self.cells[self.available_head].SetNext(None)
            self.available_head = next_available_cell
            self.cells[next_available_cell].SetPrev(None)

    def Insert_Available(self,cell_idx):
        if self.available_head == None:
            self.available_head = cell_idx
            self.available_tail = cell_idx
        else:
            self.cells[self.available_head].SetPrev(cell_idx)
            self.cells[cell_idx].SetNext(self.available_head)
            self.available_head = cell_idx
    #Init list methods
    def IsNotEmpty_Init(self):
        if self.init_head == None:
            return False
        else:
            return True

    def Empty_Init(self):
        self.init_tail = None
        self.init_head = None
        self.init_list_for_json = []

    def Insert_Init(self,cell_idx, add_gate=False):
        if self.init_head == None:
            self.init_head = cell_idx
            self.init_tail = cell_idx
        else:
            self.cells[self.init_head].SetPrev(cell_idx)
            self.cells[cell_idx].SetNext(self.init_head)
            self.init_head = cell_idx
        if add_gate:
            self.init_list_for_json.append([self.cells[cell_idx].GetCurGateNum(),cell_idx])
        #else:
        #    self.init_list_for_json.append([None,cell_idx])

    #Used list methods
    def Insert_Used(self,cell_idx,gate_num):
        if self.used_head == None:
            self.used_head = cell_idx
            self.used_tail = cell_idx
        else:
            self.cells[self.used_head].SetPrev(cell_idx)
            self.cells[cell_idx].SetNext(self.used_head)
            self.used_head = cell_idx
        self.cells[cell_idx].SetCurGateNum(gate_num)

    def Delete_Used(self,cell_idx):
        next_cell =  self.cells[cell_idx].GetNext()
        prev_cell =  self.cells[cell_idx].GetPrev()

        if self.used_head == self.used_tail and self.used_tail == cell_idx:
            self.cells[cell_idx].SetNext(None)
            self.cells[cell_idx].SetPrev(None)
            self.used_tail = self.used_head = None
        elif cell_idx == self.used_head:
            next_head = self.cells[cell_idx].GetNext()
            self.cells[cell_idx].SetNext(None)
            self.used_head = next_head
        elif cell_idx == self.used_tail:
            next_tail = self.cells[cell_idx].GetPrev()
            self.cells[cell_idx].SetPrev(None)
            self.used_tail = None
        else:
            next_cell = self.cells[cell_idx].GetNext()
            prev_cell = self.cells[cell_idx].GetPrev()
            self.cells[cell_idx].SetNext(None)
            self.cells[cell_idx].SetPrev(None)
            self.cells[next_cell].SetPrev(prev_cell)
            self.cells[prev_cell].SetPrev(next_cell)
        
# End of class CellState 



class GraphNode:

    def __init__(self,NodeNum):
        self.node_num = NodeNum
        self.out_edges = []
        self.in_edges = []
        self.num_of_out_edges = 0
        self.num_of_in_edges = 0

    def AddOutEdge(self,Dest,Val):
        self.out_edges.append(GraphEdge(self.node_num,Dest,Val))
        self.num_of_out_edges += 1

    def AddInEdge(self,Source,Val):
        self.in_edges.append(GraphEdge(Source,self.node_num,Val))
        self.num_of_in_edges += 1
        
    def RemoveOutEdge(self,Dest):
        for i,e in enumerate(self.out_edges):
            if e.GetDest() == Dest:
                del self.out_edges[i]
                self.num_of_out_edges -= 1
                break

    def RemoveInEdge(self,Source):
        for i,e in enumerate(self.in_edges):
            if e.GetSource() == Source:
                del self.in_edges[i]
                self.num_of_in_edges -= 1
                break

    def GetNumOfOutEdges(self):
        return self.num_of_out_edges

    def GetNumOfInEdges(self):
        return self.num_of_in_edges

    def GetOutEdgesList(self,TrueDepFlag):
        if TrueDepFlag:
            return [e.GetDest() for e in self.out_edges if e.GetVal()==1]
        else:
            return [e.GetDest() for e in self.out_edges]

    def GetInEdgesList(self,TrueDepFlag):
        if TrueDepFlag:
            L = [e.GetSource() for e in self.in_edges if e.GetVal()==1]
            L.reverse()
            return L
        else:
            return [e.GetSource() for e in self.in_edges]

class SIMPLER_Top_Data_Structure:

    def __init__(self, RowSize, bmfId, Benchmark):
        self.PRINT_WARNING = False
        self.PRINT_CODE_GEN = False
        self.JSON_CODE_GEN = False    
        self.Benchmark = Benchmark
        self.InputString = []
        self.OutputString = []
        self.WireString = []
        self.varLegendRow = []
        self.varLegendCol = []
        self.len_input_and_wire = 0
        self.lr = 0
        self.lc = 0   
        self.RowSize = RowSize
        self.NumberOfGates = 0
        self.NodesList = []
        self.i = 0
        self.N = RowSize
        self.t = 0 #TotalCycles
        self.ReuseCycles = 0
        self.LEAFS_inputs = []
        self.NodesList = []
        self.InitializationList = [] #composed of NoedData dummy instances
        self.InitializationPercentage = 0.0
        self.NoInputWireNum = 0
        self.NoInputWireList = [] 
        self.Max_Num_Of_Used_Cells = 0  
        self.UnConnected_wire = 0
        self.cells = CellsInfo(self.N)
        self.currentIntermediateCells = []
        self.numOfGates = 0
        self.writes = 0
        
        # read input/output/wire
        data = bmfId.read()
        bmfId.seek(0)
        self.InputString =  [input.strip() for input in re.findall("input\s+(.*?);", data, re.DOTALL)[0].split(",")]
        self.OutputString = [output.strip() for output in re.findall("output\s+(.*?);", data, re.DOTALL)[0].split(",")]
        self.WireString = [wire.strip() for wire in re.findall("wire\s+(.*?);", data, re.DOTALL)[0].split(",")]
        # Create a list containing all the outputs of the gates.
        self.gate_outputs = [[i] for i in self.InputString]
        gate_decs = re.findall("c_.*?;", data, re.DOTALL)
        
        # Map variables to numbers
        self.varLegendCol = self.WireString + self.OutputString
        self.varLegendRow = self.InputString + self.WireString + self.OutputString
        self.len_input_and_wire = len(self.InputString + self.WireString)
        
        self.lc = len(self.varLegendCol)   
        self.i = len(self.InputString)  # number of inputs
        #self.readoperations(bmfId)  # parses the netlist 
        
        for dec in gate_decs:
            for gate_name in GATE_TIME.keys():
                if gate_name in dec:
                    op = gate_name
                    self.numOfGates += 1
                    operands = [op.strip() for op in re.findall("\..+?\((.+?)\)", dec, re.DOTALL)]
                    outs = operands[-GATE_NUM_OF_OUTS[gate_name]:]
                    self.gate_outputs.append(outs)
                    break
        
        self.lr = len(self.InputString) + self.numOfGates
        self.NodesList = [NodeData(idx) for idx in range(len(self.InputString) + self.numOfGates)]
        for input_idx in range(len(self.InputString)):   
            self.NodesList[input_idx].InsertInputNode()
            self.NodesList[input_idx].input_list = self.InputString[input_idx]
        gate_number = 0
        for dec in gate_decs:
            for gate_name in GATE_TIME.keys():
                if gate_name in dec:
                    op = gate_name
                    operands = [op.strip() for op in re.findall("\..+?\((.+?)\)", dec, re.DOTALL)]
                    input_idxs = []
                    for k in range(0,len(operands) - GATE_NUM_OF_OUTS[op]):
                        inIdx = [self.gate_outputs.index(l) for l in self.gate_outputs if operands[k] in l][0]
                        if inIdx != gate_number + self.i:
                            self.NodesList[inIdx].AddOutEdge(gate_number + self.i,1)
                            self.NodesList[gate_number + self.i].AddInEdge(inIdx,1)
                            input_idxs.append(inIdx) #Gate inputs list
                    ins = operands[:-GATE_NUM_OF_OUTS[gate_name]]
                    outs = operands[-GATE_NUM_OF_OUTS[gate_name]:]
                    self.NodesList[gate_number + (len(self.InputString))].output_list = outs
                    self.NodesList[gate_number + (len(self.InputString))].input_list = ins
                    self.Insert_readoperations_parameters(gate_number + (len(self.InputString)),input_idxs,op) #For statistics
                    gate_number += 1                    
                    break            
        self.LEAFS_inputs = list(range(self.i)) #Inputs indexes
        
    #Seters/geters:     
    def Get_lr(self):
        return self.lr
    
    def Get_lc(self):
        return self.lc
    
    def GetTotalCycles(self):
        return self.t
    
    def Increase_ReuseCycles_by_one(self):
        self.ReuseCycles += 1 

    def Inset_To_InitializationList(self,val):
        self.InitializationList.append(val)
        
    def Get_InitializationList(self):
        return self.InitializationList
    
    def Increase_NoInputWireNum_by_one(self):
        self.NoInputWireNum += 1
        
    def Get_NoInputWireNum(self):
        return self.NoInputWireNum

    def Inset_To_NoInputWireList(self,val):
        self.NoInputWireList.append(val)
        
    def Get_NoInputWireList(self):
        return self.NoInputWireList   
    
    def Set_Max_Num_Of_Used_Cells(self,val):  
        self.Max_Num_Of_Used_Cells = val
    
    def Get_Max_Num_Of_Used_Cells(self):
        return self.Max_Num_Of_Used_Cells  

    #The next 4 methods are wrappers for the corresponding methods on Code_Generation_Table_Line class    
    def InsertInputNode(self,SN):
        self.NodesList[SN].InsertInputNode(SN)
        
    def Insert_readoperations_parameters(self,SN,input_idxs,op):
        self.NodesList[SN].Insert_readoperations_parameters(SN,input_idxs,op)
        
    def Insert_AllocateCell_parameters(self,line_num,cell):
        self.NodesList[line_num].Insert_AllocateCell_parameters(cell,self.t)
        
    def Insert_No_Input_Node(self,SN):
        self.NodesList[SN].Insert_No_Input_Node(SN) 
    #End of wrappers     

    def Add_To_Initialization_List(self,time,cells_list):
        #Adds an element to the Initialization
        self.Inset_To_InitializationList(NodeData(None,NodeData.Get_Initialization_op_val(),cells_list,time))
        self.Increase_ReuseCycles_by_one()          
            
    def Intrl_Print(self,Str):
        global PRINT_CODE_GEN
        if PRINT_CODE_GEN == True:
            print(Str)

    def PrintCodeGeneration(self):    
        #Prints the data and the statistics, can create the benchmark's execution sequence JSON file
                
        print('\\\\\\\\\\\\ MAPPING OF',self.Benchmark,'WITH ROW SIZE =',self.RowSize,' \\\\\\\\\\\\\n')
        names_to_mapping = OrderedDict()
        
        #inputs
        input_list_for_print = 'Inputs:{' 
        for input_idx in range(0, len(self.InputString)):
            if (self.NodesList[input_idx].GetNodeOp() != NodeData.Get_no_inputs_op_val()): 
                input_list_for_print += self.InputString[input_idx] + '(' + str(self.NodesList[input_idx].GetNodeMap()) + '),'  
                names_to_mapping[self.InputString[input_idx]] = str(self.NodesList[input_idx].GetNodeMap())
        input_list_for_print = input_list_for_print[:len(input_list_for_print) - 1] + '}'
        self.Intrl_Print(input_list_for_print)
        
        #outputs
        outputs = {}
        #for i in range(len(self.NodesList)):
            #if self.NodesList[i].op == "c_ha" and "n9807" in self.NodesList[i].input_list:
            #    import pdb;pdb.set_trace()
        mergerd_list = self.NodesList + self.InitializationList
        mergerd_list.sort(key = lambda k: k.GetNodeTime(), reverse=False) #Sorts by time
        for node in mergerd_list:
            if node.op in GATE_NUM_OF_OUTS.keys():
                for i in range(len(node.output_list)):
                    if node.output_list[i] in self.OutputString:

                        outputs[node.output_list[i]] = node.GetNodeMap()[i]

        output_list_for_print = "Outputs:{%s}" % ",".join(["%s(%d)" % (k, v) for k, v in outputs.items()])
        self.Intrl_Print(output_list_for_print)
        
        #Execution sequence
        #execution_dict_for_JSON=OrderedDict({}) #JSON
        # cells_to_init_list = ['INIT_CYCLE(' + str(idx) + ')' for idx in range(self.lr-self.lc,self.lr)]
        cells_to_init_list = ['INIT_CYCLE(' + str(idx) + ')' for idx in range(len(self.InputString), self.lr)]
        execution_dict_for_JSON=OrderedDict({'T0':'Initialization(Ron)'+ str(cells_to_init_list).replace('[','{').replace(']','}').replace(' ','')}) #JSON
        self.Intrl_Print('\nEXECUTION SEQUENCE + MAPPING: {')
        
        for node in mergerd_list:
            for i in range(len(node.output_list)):
                names_to_mapping[node.output_list[i]] = node.GetNodeMap()[i]
        
        # Merge pairs of gates
        prev_op_name = None
        prev_gate_paired = False
        time_pairs = self.t
        
        # Number of unique operators (n1)
        unique_operators = set([",", "()", ";"])
        
        # number of unique operands (n2)
        unique_operands = set()
        
        # Number of total occurrence of operators (N1)
        total_operators = []
        
        # Number of total occurrence of operands (N2)
        total_operands = []
        
        numOfGates_pairs = self.numOfGates
        for node in mergerd_list:
            if (node.GetNodeOp() == NodeData.Get_Initialization_op_val()):            
                init_list_to_print = '{'
                for pair in node.GetNodeInputs_list(): #in a case of Initialization, inputs_list composed of [gate_number,cell_number] elements
                    if pair[0] is not None:
                        gate_name = list(names_to_mapping.keys())[list(names_to_mapping.values()).index(pair[1])]
                        
                        names_to_mapping.pop(gate_name)                        
                    else:
                        gate_name = "Interm"
                    init_list_to_print += gate_name + '(' + str(pair[1]) + '),'
                init_list_to_print = init_list_to_print[:len(init_list_to_print) - 1] + '}' 
                self.Intrl_Print('T' + str(node.GetNodeTime()) + ':Initialization(Ron)' +  init_list_to_print)
                execution_dict_for_JSON.update({'T' + str(node.GetNodeTime()) : 'Initialization(Ron)' +  init_list_to_print})  #JSON 
            else:
                node_name = node.output_list
                if (node.GetNodeTime() != 0): #not an input
                    inputs_str = ''
                    for i in range(len(node.GetNodeInputs_list())):
                        #inputs_str = inputs_str + self.varLegendRow[Input] + '(' + str(self.NodesList[Input].GetNodeMap()) + ')' + ','
                        #inputs_str = inputs_str + node.input_list[i] + '(' + str(self.NodesList[node.GetNodeInputs_list()[i]].GetNodeMap()) + ')' + ','
                        
                        if not node.input_list[i] in names_to_mapping.keys():
                            map = None
                        else:
                            map = names_to_mapping[node.input_list[i]]
                        inputs_str = inputs_str + node.input_list[i] + '(' + str(map) + ')' + ','
                        
                    inputs_str = '{' + inputs_str[:len(inputs_str) - 1] + '}'
                    
                    self.Intrl_Print('T' + str(node.GetNodeTime()) + ':' + ",".join(["%s(%d)" % (node_name[i], node.GetNodeMap()[i]) for i in range(len(node_name))]) +'=' + node.GetNodeOp() + inputs_str + ', Int. cells: %s' % str(node.intermediateCells))
                    execution_dict_for_JSON.update({'T' + str(node.GetNodeTime()) : str(node_name) + '(' + ",".join([str(n) for n in node.GetNodeMap()]) +')=' + node.GetNodeOp() + inputs_str}) #JSON
                    
                    if node.GetNodeOp() == prev_op_name and not prev_gate_paired:
                        time_pairs -= GATE_TIME[node.GetNodeOp()]
                        prev_gate_paired = True
                        numOfGates_pairs -= 1
                        total_operators += [","] * len(node.GetNodeInputs_list())
                    else:
                        prev_gate_paired = False
                        total_operators.append(node.GetNodeOp())
                        total_operators += (["()", ";"] + [","] * len(node.GetNodeInputs_list()))
                    prev_op_name = node.GetNodeOp()
                    
                    
                    unique_operators.add(node.GetNodeOp())
                    unique_operands.update(set(node.GetNodeInputs_list()))
                    total_operands += node.GetNodeInputs_list()
                    
                elif (node.GetNodeOp() != NodeData.Get_no_inputs_op_val()): #line.time = 0 -- inputs
                    self.Intrl_Print('T' + str(node.GetNodeTime()) + ':' + str(node.input_list) + '(' + str(node.GetNodeNum()) +')=' + node.GetNodeOp())    
                    #execution_dict_for_JSON.update({'T' + str(node.GetNodeTime()) : node_name + '(' + str(node.GetNodeMap()) +')=' + node.GetNodeOp()}) #JSON                    
        self.Intrl_Print('}')         
        
        #Statistics
        print ('\nRESULTS AND STATISTICS:')
        print ('Benchmark:',self.Benchmark)
        print ('Total number of cycles:',self.t-self.ReuseCycles)
        print ('Total number of cycles with pairs:',time_pairs)
        print ('Number of reuse cycles:',self.ReuseCycles)
        self.InitializationPercentage = self.ReuseCycles/self.t
        print ('Initialization percentage:',self.InitializationPercentage)
        print ('Number of gates:', self.numOfGates)
        print ('Number of gates pairs:', numOfGates_pairs)
        #print ('Max number of used cells:',self.Max_Num_Of_Used_Cells)
        print ('Number of writes:',self.writes)
        print ('Row size (number of columns):',self.RowSize)
        print ('Number of used cells:', len(set(list(itertools.chain(*[node.GetNodeMap() for node in mergerd_list[len(self.InputString):]]))).union(set(list(itertools.chain(*[node.intermediateCells for node in mergerd_list[len(self.InputString):]]))))))
        
        
        n1 = len(unique_operators)
        n2 = len(unique_operands)
        N1 = len(total_operators)
        N2 = len(total_operands)
        V = (N1 + N2) * math.log2(n1 + n2)
        D = n1 * N2 / (2 * n2)
        E = D * V
        I = V / D
        
        # Number of unique operators (n1)
        print ('n1 = ', n1)
        
        # number of unique operands (n2)
        print ('n2 = ', n2)
        
        # Number of total occurrence of operators (N1)
        print ('N1 = ', N1)
        
        # Number of total occurrence of operands (N2)
        print ('N2 = ', N2)
        
        print ('E = ', E)
        
        print ('I = ', I)
        
        #JSON creation
        if (JSON_CODE_GEN == True):
            top_JSON_dict=OrderedDict({'Benchmark':self.Benchmark}) #JSON
            top_JSON_dict.update({'Row size':self.RowSize})
            top_JSON_dict.update({'Number of Gates':connected_gates})
            top_JSON_dict.update({'Inputs':input_list_for_print[len('Inputs:'):]})
            top_JSON_dict.update({'Outputs':output_list_for_print[len('Outputs:'):]})
            top_JSON_dict.update({'Number of Inputs':len(self.InputString)})
            top_JSON_dict.update({'Total cycles':self.t})
            top_JSON_dict.update({'Reuse cycles':self.ReuseCycles})
            top_JSON_dict.update({'Execution sequence' : execution_dict_for_JSON})
            #print('Benchmark= ',Benchmark)                             
            with open('JSON_' + str(self.RowSize) + '_' + self.Benchmark + '.json','w') as f:
                simplejson.dump(top_JSON_dict,f,indent=4)
            f.close()                


    def PrintLines(self):
        for line in self.code_generation_table:
            line.LineIntrlPrint()
        
    def PrintLines_InitializationList(self):
        for line in self.InitializationList:
            line.LineIntrlPrint()
        
    def readfield(self,tline,bmfId):
        #Parses the Inputs/Outputs/Wires declarations into a list

        FieldString = []
        while isinstance(tline,str):
            splited_tline = tline[tline.find(' '):].split(',')
            for i in list(filter(None,splited_tline)):
                FieldString.append(i.replace(' ','').replace(';','').replace('\n','').replace('\t',''))
            if (tline.find(';') != -1):
                break
            else:
                tline = bmfId.readline()
        return  list(filter(None,FieldString))


    def readoperations(self,bmfId):
        #Parses the netlist assignments into a graph (matrix) 

        global code_generation_top,PRINT_WARNING 
        
        tline = bmfId.readline()
        gate_number = -1
        while isinstance(tline,str):
            operands = []
            # Find gate number
            if tline.find('//') != -1: #Ignore comment lines at operands part
                tline = tline[0:tline.find('//')]
            if (tline.find("endmodule") != -1):
                return 
            elif ((tline.find("buf ") != -1) or (tline.find("zero ") != -1) or (tline.find("one ") != -1)):
                if (PRINT_WARNING == True):
                    print("** Warning ** unsupported operation: \'" + tline.replace('\n','') + "\'\n")
            elif any(gate in tline for gate in GATE_NUM_OF_OUTS.keys()): 
                for gate in GATE_NUM_OF_OUTS.keys():
                    if gate in tline:
                        op = gate
                        gate_number = gate_number + 1
                        break
                #idx_op = tline.find("nor")
                #if (idx_op != -1):
                #    op = tline[idx_op:idx_op + len('nor') + 1] #op = "nor(#inputs)"
                #else:
                #    op = 'inv1' 
                
                
                
                remain = tline
                num_of_op = 0
                while (remain.find('.') != -1):
                    remain = remain[remain.find('.'):]
                    remain = remain[remain.find('(') + 1:]
                    open_bracket_idx = remain.find('(')
                    close_bracket_idx = remain.find(')')
                    #Gets the operands
                    if (open_bracket_idx != -1) and (open_bracket_idx < close_bracket_idx):
                        second_close_bracket_idx = remain.find(')',close_bracket_idx + 1)
                        operand = remain[0:second_close_bracket_idx].replace(' ','').replace('\t','')
                        operands.append(operand)
                    else:
                        operand = remain[0:close_bracket_idx].replace(' ','').replace('\t','')
                        operands.append(operand)
                    # operands_dict[operand] = gate_number + self.i
                    num_of_op += 1
                    #out = operands[num_of_op - 1] #Gets the output operand
                outs = operands[num_of_op - GATE_NUM_OF_OUTS[op] : num_of_op]
                ins = operands[0 : num_of_op - GATE_NUM_OF_OUTS[op]]
                #for out in outs:
                input_idxs = []
                for k in range(0,num_of_op - GATE_NUM_OF_OUTS[op]):
                # for k in range(0,num_of_op):
                    inIdx = [self.gate_outputs.index(l) for l in self.gate_outputs if operands[k] in l][0]
                    # inIdx = self.gate_outputs.index(operands[k])
                    # inIdx = operands_dict[operands[k]]
                    self.NodesList[inIdx].AddOutEdge(gate_number + self.i,1) #TODO - remove self.i
                    self.NodesList[gate_number + self.i].AddInEdge(inIdx,1)
                    input_idxs.append(inIdx) #Gate inputs list
                # self.Insert_readoperations_parameters(outIdx + (self.lr -self.lc),input_idxs,op) #For statistics    
                self.NodesList[gate_number + (len(self.InputString))].output_list = outs
                self.NodesList[gate_number + (len(self.InputString))].input_list = ins
                self.Insert_readoperations_parameters(gate_number + (len(self.InputString)),input_idxs,op) #For statistics      
            tline = bmfId.readline()            

    def GetRoots_list(self): 
        #Returns the graph roots. Also calculates the FO array.
        
        roots = []
        for i,node in enumerate(self.NodesList):
            row_sum = node.GetNumOfOutEdges()
            if (row_sum == 0):
                if ((node.GetNumOfInEdges()) != 0):
                    roots.append(i)
                else:
                    if (PRINT_WARNING == True):
                        print('** Warning **',self.varLegendRow[i],'has no input')
                    self.Increase_NoInputWireNum_by_one()
                    self.Inset_To_NoInputWireList(i)
            else:
                self.NodesList[i].SetNodeFO(row_sum) 
        print('\n')
        return roots    

    def GetParents_list(self,V_i):
        return self.NodesList[V_i].GetOutEdgesList(True)

    def GetChildrens_list(self,V_i): 
        return self.NodesList[V_i].GetInEdgesList(True)
    
    def ChildrenWithoutInputs_list(self,V_i):
        #Returns the childrens without netlist inputs
    
        childrens = self.GetChildrens_list(V_i)
        childrens_without_inputs = [child for child in childrens if (child in self.LEAFS_inputs) == False]
        return childrens_without_inputs

    def computeCU(self,V_i):
        #Computes the cell usage (CU) of gate (node) V_i  
        if (self.NodesList[V_i].GetNodeCu() > 0):
            return # CU[V_i] was already generated and therefore doesn't change   
        childrens = self.ChildrenWithoutInputs_list(V_i)
        if(len(childrens) == 0): #V_i has no childrens -> V_i is connected to function inputs only
            #self.NodesList[V_i].SetNodeCu(1)
            self.NodesList[V_i].SetNodeCu(GATE_INTERMEDIATE_CALC_CELLS[self.NodesList[V_i].op] + GATE_NUM_OF_OUTS[self.NodesList[V_i].op])
        else:
            if (len(childrens) == 1):
                self.computeCU(childrens[0])
                tmp = self.NodesList[childrens[0]].GetNodeCu()
                self.NodesList[V_i].SetNodeCu(tmp)
            else:
                childrens_cu = []
                for child in childrens:
                    self.computeCU(child)
                    childrens_cu.append(self.NodesList[child].GetNodeCu())
                childrens_cu.sort(key=None, reverse=True)               
                num_of_childrens = range(0,len(childrens)) # equal to + (i - 1) for all i in 1 to N (N is the number of childrens)
                added_l = []
                for i in range(len(childrens_cu)):
                    added_l.append(childrens_cu[i]+num_of_childrens[i])
                #self.NodesList[V_i].SetNodeCu(max(np.add(childrens_cu,num_of_childrens)))
                self.NodesList[V_i].SetNodeCu(max(added_l))
            

    def AllocateRow(self,V_i):
        #Allocates cells to the gate V_i and his children (a sub-tree rooted by V_i). 
        #In a case the allocation for one of V_i's children or V_i itself is failed, the function returns False. On successful allocation returns True.
        childrens = self.ChildrenWithoutInputs_list(V_i) #Equal to C(V_i) - the set of V_i's childrens
        childrens_sorted_by_cu = [[child,self.NodesList[child].GetNodeCu()] for child in childrens] # the loop creates a list composed of pairs of the form [child number, CU[child number]]
        childrens_sorted_by_cu.sort(key = lambda k: k[1], reverse=True) #sorting by CU   
        childrens_sorted_by_cu = [elm[0] for elm in childrens_sorted_by_cu] #taking only the child (vertex) number       
        for V_j in childrens_sorted_by_cu:            
            if (self.NodesList[V_j].GetNodeMap() == []):
                if (self.AllocateRow(V_j) == False):
                    return False
        if (self.NodesList[V_i].GetNodeMap() == []): #V_i is not mapped
            
            intermediateCells = []
            first = True
            for i in range(GATE_INTERMEDIATE_CALC_CELLS[self.NodesList[V_i].op]): # Add intermediate calculation cells
                cell = self.AllocateCell(0, first)
                self.writes += 1
                if cell == 0:
                    return False
                intermediateCells.append(cell)
            
            nodeMap = []
            # print("op=%s, V_i=%d, self.t++, self.t=%d" % (self.NodesList[V_i].op,V_i, self.t))
            first = True
            for i in range(GATE_NUM_OF_OUTS[self.NodesList[V_i].op]):
                cell = self.AllocateCell(V_i, first)
                self.writes += 1
                first = False
                if cell == 0:
                    return False
                nodeMap.append(cell)
            self.NodesList[V_i].SetNodeMap(nodeMap)
            if len(intermediateCells) != 0:
                self.NodesList[V_i].intermediateCells = intermediateCells
                self.currentIntermediateCells += [[None, cell] for cell in intermediateCells]
            for cell in intermediateCells:
                self.cells.Insert_Init(cell)
            # print("V_i=%d, self.t+=%d, self.t=%d" % (V_i, GATE_TIME[self.NodesList[V_i].op] - 1, self.t))
            self.t += GATE_TIME[self.NodesList[V_i].op] - 1
        return True

    # def AllocateCell(self,V_i):
        # FreeCell = self.cells.GetFirst_Available()
        # if FreeCell == None:
            # if self.cells.IsNotEmpty_Init():
                # self.t += 1
                # self.Add_To_Initialization_List(self.t, self.cells.init_list_for_json)
                # self.cells.Concatenate_init_to_available_list()
                # self.cells.Empty_Init()
                # FreeCell = self.cells.GetFirst_Available()
            # else:
                # return 0
        # self.cells.DeleteFirst_Available()
        # if (V_i != 0):
            # self.cells.Insert_Used(FreeCell,V_i)
            # self.t += 1
            # self.Insert_AllocateCell_parameters(V_i,FreeCell)
            # self.t += GATE_TIME[self.NodesList[V_i].op] - 1
            # for V_k in self.ChildrenWithoutInputs_list(V_i):
                # self.NodesList[V_k].SetNodeFO(self.NodesList[V_k].GetNodeFO() - 1)
                # if (self.NodesList[V_k].GetNodeFO() == 0):
                    # cells_to_be_moved = self.NodesList[V_k].GetNodeMap()
                    # for cell_to_be_moved in cells_to_be_moved:
                        # self.cells.Delete_Used(cell_to_be_moved)
                        # self.cells.Insert_Init(cell_to_be_moved)
        # return FreeCell

    
    def AllocateCell(self,V_i,first):
        FreeCell = self.cells.GetFirst_Available()
        if FreeCell == None:
            if self.cells.IsNotEmpty_Init():
                if first:
                    self.t += 1
                self.cells.init_list_for_json += self.currentIntermediateCells
                self.currentIntermediateCells = []
                self.Add_To_Initialization_List(self.t, self.cells.init_list_for_json)
                self.cells.Concatenate_init_to_available_list()
                self.cells.Empty_Init()
                FreeCell = self.cells.GetFirst_Available()
            else:
                return 0
        self.cells.DeleteFirst_Available()
        if (V_i != 0):
            
            self.cells.Insert_Used(FreeCell,V_i)
            if first:
                self.t += 1
                for V_k in self.ChildrenWithoutInputs_list(V_i):
                    #if "n9807" in self.NodesList[V_k].output_list:
                    #   import pdb;pdb.set_trace()
                    self.NodesList[V_k].SetNodeFO(self.NodesList[V_k].GetNodeFO() - 1)
                    if (self.NodesList[V_k].GetNodeFO() == 0):
                        cells_to_be_moved = self.NodesList[V_k].GetNodeMap()
                        #if 495 in cells_to_be_moved:
                        #    import pdb;pdb.set_trace()
                        for cell_to_be_moved in cells_to_be_moved:
                            self.cells.Delete_Used(cell_to_be_moved)
                            self.cells.Insert_Init(cell_to_be_moved, True)
            self.Insert_AllocateCell_parameters(V_i,FreeCell)
            
        return FreeCell
    
    def IncreaseOutputsFo(self):
        # This function created to make sure outputs cells will not evacuated.
        #It is done by increasing their FO by 1

        for idx in range(self.len_input_and_wire,self.lr): #outputs idx range
            self.NodesList[idx].SetNodeFO(self.NodesList[idx].GetNodeFO() + 1)
            
            
    def RunAlgorithm(self):
            #================ SIMPLER algorithm Starts ================ 
            
            #FO array initialized in __init__
            #Cell Usage array initialized in __init__
            #Map is the number of the cell/column V_i is mapped to. Array initialized in __init__      
            #CELLS list initialization 
            ROOTs = self.GetRoots_list() #set of all roots of the graph. Also calculates FO values.
            self.IncreaseOutputsFo() # To ensure outputs who are also inputs, will not be evacuated
            self.t = 0 #Number of clock cycles        

            for netlist_input in range(0,self.i):
                self.cells.Insert_Used(netlist_input,netlist_input)
            for cell in range(self.i,self.N):
                self.cells.Insert_Available(cell) 
            #alg start here
            t1 = time.time()#time
            for r in ROOTs:
                self.computeCU(r)
            if SORT_ROOTS == 'NO':
                for r in ROOTs:    
                    if (self.AllocateRow(r) == False):
                        print('\\\\\\\\\\\\ MAPPING OF',self.Benchmark,'WITH ROW SIZE =',self.N,' \\\\\\\\\\\\\n')
                        print('False - no mapping\n')
                        #code_generation_success_flag = False #Printing flag 
                        #break #To enable multiple runs. To fit the code to the article, comment this line, and uncomment the two next lines. 
                        return False #Cannot find mapping
                t2 = time.time()
                print('time is:',t2-t1)#time
                return True #A mapping of the entire netlist was found 
            else:        
                sorted_ROOTs = [[r,self.NodesList[r].GetNodeCu()] for r in ROOTs]
                if SORT_ROOTS == 'DESCEND':
                    sorted_ROOTs.sort(key = lambda k: k[1], reverse=True)
                elif SORT_ROOTS == 'ASCEND':
                    sorted_ROOTs.sort(key = lambda k: k[1], reverse=False)
                for sr in sorted_ROOTs:    
                    if (self.AllocateRow(sr[0]) == False):
                        print('\\\\\\\\\\\\ MAPPING OF',self.Benchmark,'WITH ROW SIZE =',self.N,' \\\\\\\\\\\\\n')
                        print('False - no mapping\n')
                        return False #cannot find mapping
                return True          


#============ End of Globals variables and Classes ==============

# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def mergeGates_HA(syn_output_path):
    
    # Build gate dictionary
    data = open(syn_output_path, "r").read()
    gate_decs = re.findall("c_.*?;", data, re.DOTALL)
    OutputString = [output.strip() for output in re.findall("output\s+(.*?);", data, re.DOTALL)[0].split(",")]
    InputString = [output.strip() for output in re.findall("input\s+(.*?);", data, re.DOTALL)[0].split(",")]
    gate_dict = {}
    gate_dict["c_ha"] = []
    gate_dict["c_xor2"] = []
    gate_dict["c_and2"] = []
    for dec in gate_decs:
        for gate_name in GATE_TIME.keys():
            if gate_name in dec:
                op = gate_name
                if not op in gate_dict.keys():
                    gate_dict[op] = [dec]
                else:
                    gate_dict[op].append(dec)
    
    # Merge HA gates
    new_gate_dict = copy.deepcopy(gate_dict)
    for gate_dec in gate_dict["c_xor2"]:
        if gate_dec in new_gate_dict["c_xor2"]:
            operands = [op.strip() for op in re.findall("\..+?\((.+?)\)", gate_dec, re.DOTALL)] 
            found = False
            for gate_dec2 in gate_dict["c_and2"]:
                operands2 = [op.strip() for op in re.findall("\..+?\((.+?)\)", gate_dec2, re.DOTALL)]
                #if gate_dec2 in new_gate_dict["c_and2"] and operands[0] in operands[:2] and operands[1] in operands[:2] and gate_dec2 != gate_dec:
                if gate_dec2 in new_gate_dict["c_and2"] and operands[0] in operands2[:2] and operands[1] in operands2[:2]:
                    y1 = operands[2]
                    y2 = operands2[2]
                    new_gate_dict["c_xor2"].remove(gate_dec)
                    new_gate_dict["c_and2"].remove(gate_dec2)
                    unit_name = re.findall("U[0-9]+", gate_dec, re.DOTALL)[0]
                    new_gate_dict["c_ha"].append("c_ha %s ( .A(%s), .B(%s), .Y1(%s), .Y2(%s) );" % (unit_name, operands[0], operands[1], y1, y2))
                    found = True
                    break
    # Create a new netlist
    merged = []
    for l in new_gate_dict.values():
        merged += l
    
    for dec in gate_decs:
        data = data.replace(dec + "\n", "")  
    ind = data.find("endmodule")
    open("syn_output_path2.v", "w").write(data[:ind] + "\nwire zero;\n" + "\n".join(merged).replace("1'b0", "zero") + "\n" + data[ind:])

def mergeGates_HS(syn_output_path):
    
    # Build gate dictionary
    data = open(syn_output_path, "r").read()
    gate_decs = re.findall("c_.*?;", data, re.DOTALL)
    OutputString = [output.strip() for output in re.findall("output\s+(.*?);", data, re.DOTALL)[0].split(",")]
    InputString = [output.strip() for output in re.findall("input\s+(.*?);", data, re.DOTALL)[0].split(",")]
    gate_dict = {}
    gate_dict["c_hs"] = []
    gate_dict["c_xor2"] = []
    gate_dict["c_bout"] = []
    for dec in gate_decs:
        for gate_name in GATE_TIME.keys():
            if gate_name in dec:
                op = gate_name
                if not op in gate_dict.keys():
                    gate_dict[op] = [dec]
                else:
                    gate_dict[op].append(dec)
    
    # Merge HA gates
    new_gate_dict = copy.deepcopy(gate_dict)
    for gate_dec in gate_dict["c_xor2"]:
        if gate_dec in new_gate_dict["c_xor2"]:
            operands = [op.strip() for op in re.findall("\..+?\((.+?)\)", gate_dec, re.DOTALL)] 
            found = False
            for gate_dec2 in gate_dict["c_bout"]:
                operands2 = [op.strip() for op in re.findall("\..+?\((.+?)\)", gate_dec2, re.DOTALL)]
                #if gate_dec2 in new_gate_dict["c_and2"] and operands[0] in operands[:2] and operands[1] in operands[:2] and gate_dec2 != gate_dec:
                if gate_dec2 in new_gate_dict["c_bout"] and operands[0] in operands2[:2] and operands[1] in operands2[:2]:
                    y1 = operands[2]
                    y2 = operands2[2]
                    new_gate_dict["c_xor2"].remove(gate_dec)
                    new_gate_dict["c_bout"].remove(gate_dec2)
                    unit_name = re.findall("U[0-9]+", gate_dec, re.DOTALL)[0]
                    new_gate_dict["c_hs"].append("c_hs %s ( .A(%s), .B(%s), .Y1(%s), .Y2(%s) );" % (unit_name, operands[0], operands[1], y1, y2))
                    found = True
                    break
    # Create a new netlist
    merged = []
    for l in new_gate_dict.values():
        merged += l
    
    for dec in gate_decs:
        data = data.replace(dec + "\n", "")    
    ind = data.find("endmodule")
    open("syn_output_path3.v", "w").write(data[:ind] + "\n".join(merged) + "\n" + data[ind:])

    
#======================== SIMPLER MAPPING =======================
def SIMPLER_Main (BenchmarkStrings, Max_num_gates, ROW_SIZE, Benchmark_name, generate_json, print_mapping, print_warnings):
    global JSON_CODE_GEN, PRINT_CODE_GEN, PRINT_WARNING, SORT_ROOTS
    
    #print controls
    JSON_CODE_GEN = generate_json
    PRINT_CODE_GEN = print_mapping
    PRINT_WARNING = print_warnings
    SORT_ROOTS = 'NO' #Set to one of the follows: 'NO, 'ASCEND' 'DESCEND' 
    
    for Row_size in ROW_SIZE: 
        for Benchmark in BenchmarkStrings:
            
            #Parse operations 
            bmfId = open(Benchmark,"r") #open file       
            SIMPLER_TDS = SIMPLER_Top_Data_Structure(Row_size,bmfId,Benchmark_name)
                          
            if (SIMPLER_TDS.Get_lr()>Max_num_gates or SIMPLER_TDS.Get_lc()>Max_num_gates):
                print("** net too big, skip " + str(SIMPLER_TDS.Get_lr()) +" X " + str(SIMPLER_TDS.Get_lc()) + "\n")
                continue
                              
            #Statistics calculations 
            SIMPLER_TDS.Set_Max_Num_Of_Used_Cells(CellInfo.get_max_num_of_used_cells())
            code_generation_success_flag =SIMPLER_TDS.RunAlgorithm()
            if (code_generation_success_flag == True):
                SIMPLER_TDS.PrintCodeGeneration() 
            
            #Benchmark's end 
            bmfId.close() #close file
            CellInfo.Set_cur_num_of_used_cells_to_zero() #need to initiate because its a class variable
            CellInfo.Set_max_num_of_used_cells_to_zero() #need to initiate because its a class variable
            print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ \n')

#=========================== End of SIMPLER MAPPING ===========================

#============================== End of code ===================================
