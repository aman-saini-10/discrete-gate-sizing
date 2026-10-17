# Description: A Python script to parse a Verilog file and perform circuit analysis.
# Author: Aman Saini (ee24s007)

import sys, os, math, re, json
import networkx as nx
from tabulate import tabulate
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# add the path for accessing utilities.py
sys.path.append(os.path.abspath(config["utilities_dir"]))
import utilities as utils

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("❌ Error: Please provide a Verilog filename.")
        print("Usage: python parser.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    base_filename = f"{os.path.splitext(os.path.basename(filename))[0]}"
    
    analysis_filenames = [
        f"analysis_{base_filename}_inout.txt",
        f"analysis_{base_filename}_fnout.txt",
        f"analysis_{base_filename}_cpath.txt",
        f"dag_{base_filename}.json"
    ]
    
    print("\nStarting Verilog File Parsing...")
    file_path = config["verilog_dir"]
    
    inputs, outputs, gates = utils.parse_verilog(file_path, filename)
    #LOGS---------------------------------------------------------------------------
    print(f"Successfully parsed '{filename}'")
    print(f"   - Found {len(inputs)} inputs")
    print(f"   - Found {len(outputs)} outputs")
    print(f"   - Identified {len(gates)} logic gates\n")
    print("Building the Circuit's Directed Acyclic Graph (DAG)...")
    #---------------------------------------------------------------------------
    
    
    dag, gate_dict, fanout_dict = utils.construct_dag(inputs, outputs, gates)
    #LOGS---------------------------------------------------------------------------
    print("DAG construction completed.\n")
    print("Performing Circuit Analysis...")
    #---------------------------------------------------------------------------
    
    
    gate_depths = utils.compute_gate_depths(dag, gate_dict)
    #LOGS---------------------------------------------------------------------------
    print("   - Determining the longest path in the circuit")
    #---------------------------------------------------------------------------
    
    
    paths, gate_sequences, gate_type_seqs = utils.longest_path(dag, gate_dict)
    #LOGS---------------------------------------------------------------------------
    print("Longest path found\n")
    #---------------------------------------------------------------------------
    
    file_path = config["reports_dir"]
    utils.write_analysis_report(file_path, analysis_filenames, inputs, outputs, fanout_dict, paths, gate_sequences, gate_type_seqs, gate_depths)
    #LOGS---------------------------------------------------------------------------
    print(f"Analysis complete!\n")
    # print(f"IO Report saved as '{analysis_filenames[0]}'.")
    print(f"Fanout Report saved as '{analysis_filenames[1]}'.")
    print(f"Critical Path Report saved as '{analysis_filenames[2]}'.")
    #---------------------------------------------------------------------------
    
    # Uncomment the following line if you wish to see the circuit as a Directed Acyclic Graph
    # utils.graph_gen(dag, inputs, outputs)
    
    # save the DAG as a JSON file to be used by the optimizer
    file_path = config["dag_output_dir"]
    utils.json_dump(file_path, dag, gate_dict, analysis_filenames)