EE6332-Modelling and Optimization Project (Verilog Netlist Parser)
Author: Aman Saini (ee24s007)
------------------------------------------------------------------------------

Main File: EE6332_endsem.ipynb

* Continuous sizing results are stored in the directory `sizing_results` (separate files for Twall, and area minimum solutions of given relaxation factors (Tspec/Twall)).
* Discrete sizing results are stored in directory `discrete_solutions`.
	
	-> <ckt_name>_log.txt contains the execution logs, summarizing the results.
	-> <ckt_name>_size.txt contains the table detailing the size of every gate in the circuit.

------------------------------------------------------------------------------
It is recommended to run this notebook in google colab. Follow the given steps to setup the notebook for execution:

	* Create a directory "EE6332" in your google drive and upload the following items in it:
		1. The notebook file "EE6332_endsem.ipynb"
		2. The folder DAG_json, created using "parser.py"
		3. "mosek.lic" license file
	
	* Make sure sizes_dict.json is also present, however, if not available, it can also be created using the code provided in the notebook.
	* If you choose to use a different directory structure, modify the file paths in the notebook accordingly.