import requests, sys, subprocess, getopt, json, time, math
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "f:F:"
long_options = ["file=", "file-path"]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

hasFile = False
hasFile_Path = False

for current_argument, current_value in arguments:
    if current_argument in ("-f", "--file"):
        file_name = current_value
        hasFile = True
    if current_argument in ("-F", "--file-path"):
        file_path = current_value
        hasFile_Path = True

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

if hasFile_Path == True:
    f = open(f'{file_path}', 'r')
if hasFile == True:
    f = open(f'{home_dir}/Reports/{file_name}', 'r')
results_arr = f.read().split("\n")
results_arr.pop()

print("**********INFORMATIONAL VULNS************")
for result in results_arr:
    parsed = json.loads(result)
    if parsed['info']['severity'] == 'info':
        print(json.dumps(parsed, indent=4, sort_keys=True))

print("**********IMPACTFUL VULNS************")
for result in results_arr:
    parsed = json.loads(result)
    if parsed['info']['severity'] != 'info':
        print(json.dumps(parsed, indent=4, sort_keys=True))