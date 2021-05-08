import requests, sys, subprocess, getopt, json, time, math
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "d:t:"
long_options = ["domain=", "template="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value
    if current_argument in ("-t", "--template"):
        template = current_value

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Nuclei - Template: {template} - Start Time: {now_start}\n")
f.close()

start = time.time()

r = requests.post('http://10.0.0.211:8000/api/auto', data={'fqdn':fqdn})
thisFqdn = r.json()

httprobe_arr = thisFqdn['recon']['subdomains']['httprobe']
masscan_arr = thisFqdn['recon']['subdomains']['masscanLive']

urls = httprobe_arr + masscan_arr

url_str = ""

for url in urls:
    url_str += f"{url}\n"

f = open("/tmp/urls.txt", "w")
f.write(url_str)
f.close()

now = datetime.now().strftime("%d-%m-%y_%I%p")

subprocess.run([f"{home_dir}/go/bin/nuclei -t {template}/ -l /tmp/urls.txt -o {home_dir}/Reports/{template}-{now}.json -json"], shell=True)

try:
    f = open(f"{home_dir}/Reports/{template}-{now}.json")
    results = f.read().split("\n")
    data = []
    for result in results:
        if len(result) < 5:
            i = results.index(result)
            del results[i]
            continue
        json_result = json.loads(result)
        data.append(json_result)
    info_counter = 0
    non_info_counter = 0
    for result in data:
        if result['info']['severity'] == 'info':
            info_counter += 1
        else :
            non_info_counter += 1
    end = time.time()
    runtime_seconds = math.floor(end - start)
    runtime_minutes = math.floor(runtime_seconds / 60)
    target_count = len(urls)
    message_json = {'text':f'Nuclei Scan Completed!\n\nResults:\nWeb Servers Scanned: {target_count}\nRood/Seed Targeted: {fqdn}\nTemplate Category: {template}\nImpactful Results: {non_info_counter}\nInformational Results: {info_counter}\nScan Time: {runtime_minutes} minutes\nReport Location: {home_dir}/Reports/{template}-{now}.json\n\nNothing wrong with a little Spray and Pray!!  :pray:','username':'Vuln Disco Box','icon_emoji':':dart:'}
    f = open(f'{home_dir}/.keys/slack_web_hook')
    token = f.read()
    slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)     
except Exception as e:
    f = open(f"{home_dir}/Logs/automation.log", "a")
    f.write(f"Nuclei - Template: {template} - No Results Found\n")
    f.close()

now_end = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Nuclei - Template: {template} - End Time: {now_end}\n")
f.close()