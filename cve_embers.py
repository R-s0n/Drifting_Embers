import requests, argparse, subprocess, sys, json
from bs4 import BeautifulSoup
from time import sleep
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

script_links = []
raw_scripts = []
links = []
extension_blacklist = [".pdf", ".jpg", ".png", ".svg"]

def get_links(fqdn, url):
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    a_tags = soup.find_all('a')
    for tag in a_tags:
        if tag.get('href') != None:
            tag_to_add = tag.get('href')
            if ".pdf" in tag_to_add or ".jpg" in tag_to_add or ".png" in tag_to_add or ".svg" in tag_to_add or "mailto:" in tag_to_add:
                continue
            if "?" in tag_to_add:
                tag_to_add = tag_to_add.split("?")[0]
            if "#" in tag_to_add:
                tag_to_add = tag_to_add.split("#")[0]
            if tag_to_add[:4] == "http":
                if tag_to_add[:len(url)] == url:
                    if tag_to_add not in links:
                        links.append(tag_to_add)
            elif tag_to_add[:1] == "/":
                tag_to_add = f"{fqdn}{tag_to_add}"
                if tag_to_add not in links:
                    links.append(tag_to_add)
            else:
                tag_to_add = f"{fqdn}/{tag_to_add}"
                if tag_to_add not in links:
                    links.append(tag_to_add)

def get_scripts(url):
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    script_tags = soup.find_all('script')
    for tag in script_tags:
        if tag.get('src') != None:
            tag_to_add = tag.get('src')
            if "?" in tag_to_add:
                tag_to_add = tag_to_add.split("?")[0]
            if tag_to_add[:4] == "http":
                if tag_to_add not in script_links:
                    script_links.append(tag_to_add)
            elif tag_to_add[:1] == "/":
                tag_to_add = f"{url}{tag_to_add}"
                if tag_to_add not in script_links:
                    script_links.append(f"{url}{tag_to_add}")
            else:
                tag_to_add = f"{url}/{tag_to_add}"
                if tag_to_add not in script_links:
                    script_links.append(f"{url}/{tag_to_add}")

def crawl_links(fqdn, depth):
    if depth == "full":
        while True:
            num_of_links = len(links)
            temp = links
            for link in temp:
                if ".pdf" in link or ".jpg" in link or ".png" in link or ".svg" in link or "mailto:" in link:
                    links.remove(link)
                    continue
                else:
                    get_links(fqdn, link)
            if len(links) == num_of_links:
                return len(links)
    else:
        counter = 1
        while True:
            num_of_links = len(links)
            temp = links
            for link in temp:
                if ".pdf" in link or ".jpg" in link or ".png" in link or ".svg" in link or "mailto:" in link:
                    links.remove(link)
                    continue
                else:
                    get_links(fqdn, link)
            if len(links) == num_of_links or counter >= int(depth):
                return len(links)
            counter += 1

def clean_urls(fqdn_list):
    clean_url_list = []
    for fqdn in fqdn_list:
        for url in fqdn:
            if "?" in url:
                url_split = url.split("?")
                if url_split[0] not in clean_url_list:
                    clean_url_list.append(url_split[0])
            else:
                if url not in clean_url_list:
                    clean_url_list.append(url)
    return clean_url_list

def get_home_dir():
    get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return get_home_dir.stdout.replace("\n", "")

def npm_package_scan(args, url_list):
    for url in url_list:
        print(f"[-] Scanning {url}...")
        get_links(url, url)
        # Uncomment to add crawling
        # link_number = crawl_links(url, "1")
        for link in links:
            get_scripts(link)
        for script in script_links:
            if args.package.lower() in script.lower():
                print(f"[+] Package {args.package} was found on {url}!")
                break


def get_fqdns(args):
    res = requests.post(f'http://{args.server}:{args.port}/api/fqdn/all')
    fqdn_json = res.json()
    fqdn_list = []
    for fqdn in fqdn_json:
        fqdn_list.append(fqdn['recon']['subdomains']['httprobe'])
    return fqdn_list

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-p','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('-P','--package', help='Name of JavaScript package', required=True)
    return parser.parse_args()

def main(args):
    fqdn_list = get_fqdns(args)
    clean_url_list = clean_urls(fqdn_list)
    npm_package_scan(args, clean_url_list)
    print("[+] Done!")

if __name__ == "__main__":
    args = arg_parse()
    main(args)