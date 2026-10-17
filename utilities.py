# Description: A Python script to parse a Verilog file and perform circuit analysis.
# Author: Aman Saini (ee24s007)

import math, re, json, os
import networkx as nx
from tabulate import tabulate
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
# =============================================================================

def parse_verilog(file_path, filename): # PARSER FUNCTION
    
    with open(os.path.join(file_path, filename), 'r') as f:
        lines = f.readlines()
    
    inputs = []; outputs = []; gates = []
    
    capturing_inputs = False; capturing_outputs = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("input"):
            capturing_inputs = True; capturing_outputs = False
        elif line.startswith("output"):
            capturing_inputs = False; capturing_outputs = True
        elif line.startswith("wire"):
            capturing_inputs = False; capturing_outputs = False
        
        # I/O HANDLING UTILITY
        if capturing_inputs or capturing_outputs:
            tokens = line.replace("input", "").replace("output", "").replace(";", "").split(',')
            tokens = [token.strip() for token in tokens if token.strip()]
            
            if capturing_inputs:
                inputs.extend(tokens)
            else:
                outputs.extend(tokens)
        # GATE HANDLING UTILITY        
        elif line.startswith("nand") or line.startswith("nor") or line.startswith("not"):
            
            # HANDLING I/Os as TOKENS
            tokens = line.split('(')[-1].split(')')[0].split(',')
            tokens = [token.strip() for token in tokens if token.strip()]
            
            # GETTING THE GATE TYPE
            gate_type = "NAND" if "nand" in line else "NOR" if "nor" in line else "NOT"
            gate_type = gate_type if gate_type == "NOT" else f"{gate_type}_{len(tokens) - 1}"
            
            # GATE NAME
            gate_name = line.split('(')[0].strip().split()[1]
            
            gates.append((gate_name, gate_type, tokens[0], tokens[1:]))
            
    return inputs, outputs, gates

# =============================================================================

def construct_dag(inputs, outputs, gates):
    G = nx.DiGraph()
    
    # adding the input and output nodes to the DiGraph
    for node in inputs:
        G.add_node(node, type="input")
    # for node in outputs:
    #     G.add_node(node, type="output")
    
    # associate each output node to a gate_name and gate_type
    gate_dict = {}
    
    # # First, construct gate_dict
    # for gate_name, gate_type, output, inputs in gates:
    #     # In the DiGraph, only the gate_type is associated with the output
    #     G.add_node(output, type=gate_type)
    #     gate_dict[output] = (gate_name, gate_type)

    # First, construct gate_dict
    for gate_name, gate_type, output, inputs in gates:
        # If output is also a primary output, keep that info
        node_attrs = {"type": gate_type}
        if output in outputs:
            node_attrs["is_output"] = True
        G.add_node(output, **node_attrs)
        gate_dict[output] = (gate_name, gate_type)
    
        
    # Now, construct fanout_dict after gate_dict is complete
    fanout_dict = {gate_name: set() for gate_name, _, _, _ in gates}
    
    for gate_name, gate_type, output, inputs in gates:
        for inp in inputs:
            G.add_edge(inp, output)
            if inp in gate_dict:
                prev_gate = gate_dict[inp][0]  # Find previous gate
                if prev_gate in fanout_dict:
                    fanout_dict[prev_gate].add(gate_name)

    # Convert sets to lists
    for key in fanout_dict:
        fanout_dict[key] = list(fanout_dict[key])
    
    return G, gate_dict, fanout_dict

# =============================================================================

def longest_path(G, gate_dict):
    try:
        path = nx.dag_longest_path(G)
        gate_sequence = [gate_dict[node][0] for node in path if node in gate_dict]
        gate_type_seq = [gate_dict[node][1] for node in path if node in gate_dict]
        return path, gate_sequence, gate_type_seq
    except nx.NetworkXUnfeasible:
        return [], [], []

# =============================================================================

def compute_gate_depths(dag, gate_dict):
    depths = {node: 0 for node in dag.nodes if dag.in_degree(node) == 0}  # Inputs at depth 0
    for node in nx.topological_sort(dag):
        if dag.in_degree(node) > 0:  # Skip inputs
            depths[node] = 1 + max(depths[parent] for parent in dag.predecessors(node))
    
    gate_depths = {gate_dict[node][0]: depths[node] for node in depths if node in gate_dict}
    return gate_depths

# =============================================================================

def write_analysis_report(file_path, filename, inputs, outputs, fanout_dict, path, gate_sequence, gate_type_seq, gate_depths):
    def create_table(items, title, max_columns=7):
        """Formats a table for inputs, outputs, and other lists."""
        if not items:
            return f"{title}: None\n"
        num_columns = min(max_columns, len(items))
        num_rows = math.ceil(len(items) / num_columns)
        table_data = [items[i * num_columns:(i + 1) * num_columns] for i in range(num_rows)]
        return f"{title} (Total: {len(items)})\n" + tabulate(table_data, tablefmt="grid") + "\n"
    
    def create_fanout_table(fanout_dict, gate_depths, sort_by="fanout", max_columns=5):
        """Formats the fanout table with sorting by fanout count or topological order."""
        if not fanout_dict:
            return "Fanout List: None\n"
        
        if sort_by == "fanout":
            sorted_fanouts = sorted(fanout_dict.items(), key=lambda x: len(x[1]), reverse=True)
            title = "Fanout List (Sorted by N(Fanout) - Descending)"
        else:
            sorted_fanouts = sorted(fanout_dict.items(), key=lambda x: gate_depths.get(x[0], float('inf')))
            title = "Fanout List (Sorted by Topological Order - Increasing Depth)"

        table_data = []
        for idx, (gate, fanouts) in enumerate(sorted_fanouts, start=1):
            if not fanouts:
                table_data.append([idx, gate, 0, gate_depths.get(gate, "N/A")])
                continue
            
            num_columns = min(max_columns, len(fanouts))
            num_rows = math.ceil(len(fanouts) / num_columns)
            split_fanouts = [fanouts[i * num_columns:(i + 1) * num_columns] for i in range(num_rows)]
            
            table_data.append([idx, gate, len(fanouts), gate_depths.get(gate, "N/A")] + split_fanouts[0])
            for row in split_fanouts[1:]:
                table_data.append(["", "", "", ""] + row)
        
        headers = ["Sr.No.", "Gate", "N(Fanout)", "Depth"] + [""] * max_columns
        return title + "\n" + tabulate(table_data, headers=headers, tablefmt="grid") + "\n"
    
    os.makedirs(file_path, exist_ok=True)  # Ensure the directory exists
    
    #   WRITING INPUTS AND OUTPUTS TO THE INOUT FILE
    with open(os.path.join(file_path, filename[1]), "w") as f:
        f.write("Circuit Analysis Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(create_table(inputs, "Inputs"))
        f.write(create_table(outputs, "Outputs"))
    
    # # WRITING FANOUT TABLES TO FNOUT FILE
    # with open(filename[1], "w") as f:
    
        f.write("\n" + create_fanout_table(fanout_dict, gate_depths, sort_by="depth"))
        f.write("\n\n")
        f.write("\n" + create_fanout_table(fanout_dict, gate_depths, sort_by="fanout"))
        
        
    max_len = max(len(path), len(gate_sequence), len(gate_type_seq))
    path += [""] * (max_len - len(path))
    gate_sequence += [""] * (max_len - len(gate_sequence))
    gate_type_seq += [""] * (max_len - len(gate_type_seq))
    serial_numbers = list(range(1, max_len + 1))
    
    # WRITING THE LONGEST PATH ANALYSIS TO CPATH FILE
    with open(os.path.join(file_path, filename[2]), "w") as f:
        f.write(f"\nLongest Path Analysis (Total Gates: {max_len - 1})\n")
        table = zip(serial_numbers, path, gate_sequence, gate_type_seq)
        headers = ["S.No.", "Longest Path", "Gate Sequence", "Gate Types"]
        f.write(tabulate(table, headers=headers, tablefmt="grid") + "\n")
        
    return

# =============================================================================

def graph_gen(dag, inputs, outputs):
    # Define node colors: Green for inputs, Red for outputs, Blue for internal gates
    node_colors = []
    for node in dag.nodes():
        if node in inputs:
            node_colors.append("green")  # Primary inputs
        elif node in outputs:
            node_colors.append("red")  # Primary outputs
        else:
            node_colors.append("lightblue")  # Internal nodes (gates)

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(dag)  # Layout for better visualization

    # Draw nodes
    nx.draw(dag, pos, with_labels=True, node_size=2000, node_color=node_colors, edge_color="gray", font_size=10, font_weight="bold")

    # Add legend
    import matplotlib.patches as mpatches
    legend_labels = [
        mpatches.Patch(color="green", label="Primary Inputs"),
        mpatches.Patch(color="red", label="Primary Outputs"),
        mpatches.Patch(color="lightblue", label="Intermidiate nodes")
    ]
    plt.legend(handles=legend_labels, loc="upper left")

    plt.title("Circuit DAG Visualization")
    plt.show()    
    
# =============================================================================
# saves the directed acyclic graph as a json file, to be used by the optimization program
def json_dump(file_path, G, gate_dict, analysis_filenames):
    for node in G.nodes():
        if node in gate_dict:
            name, gate_type = gate_dict[node]
            G.nodes[node]['name'] = name
            G.nodes[node]['type'] = gate_type
        else:
            # For primary inputs, keep 'type' as 'input'
            G.nodes[node]['type'] = 'input'
            G.nodes[node]['name'] = node  # or name them "IN1", "IN2", etc.

    os.makedirs(file_path, exist_ok=True)  # Ensure the directory exists
    
    # Save DAG to file in node-link JSON format
    data = json_graph.node_link_data(G)
    with open(os.path.join(file_path, analysis_filenames[3]), "w") as f:
        json.dump(data, f, indent=2)