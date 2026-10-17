EE6332-Modelling and Optimization Project (Verilog Netlist Parser)
Author: Aman Saini (ee24s007)
------------------------------------------------------------------------------
File Description:

parser.py: Main Executable (parses structural Verilog netlists into DAGs)
utilities.py: Defines necessary functions
config.json: Config file -> Sets appropriate paths

------------------------------------------------------------------------------
Libraries Required for successful execution:

1. networkx
2. tabulate
3. matplotlib.pyplot

------------------------------------------------------------------------------
Usage: "python parser.py <file_path>"
Example: python parser.py .\c17.txt
------------------------------------------------------------------------------

Use the config.json to set the paths appropriately.
Specifically, the following paths are required:

1. verilog_dir: the path where the input netlist is stored
2. utilities_dir: the path where utilities.py is stored
3. dag_output_dir: the path where DAG (Directed-Acyclic-Graph) will be saved
4. reports_dir: the path where output reports of the circuit will be saved 

------------------------------------------------------------------------------
Results:
    The submission contains the following directories, that are produced upon code execution.
    * analyses: files detailing the critical path, and fan-out of the gates in the circuits.
    * DAG_json: contains the json files of all the circuits stored as DAG.