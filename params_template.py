'''
Author: Brendan Pratt
Organization: Pacific Northwest Seismic Network

SeisScripter - Params Template

This template file contains modifiable parameters for the SeisScripter program. To use in the main
program, this file MUST be copied or renamed to "params.py"

Last modified: 1/14/2025
'''
###################################################################################################

'''
Testing params:
'''
# Change to False for production run
TESTING: bool = True
# File containing the IP and site info of devices to use for testing
TESTING_CSV: str = "input/testing_ips.csv"


'''
Bash script params:
'''
# Bash script filename
SH_SCRIPT: str = "test-script.sh"
# Bash script file path
SH_SCRIPT_PATH: str = "input/"


'''
Results params:
'''
# Results filename
RESULTS_CSV: str = "results.csv"
# Results file path
RESULTS_PATH: str = "output/"
# Optional CSV header for results file
RESULTS_HEADER: str = "Output"


'''
Other params:
'''
# delay in seconds before moving on to next site
DELAY: float = 1.0
# delay in seconds for an attempted ssh connection to time out
TIMEOUT: float = 5.0
