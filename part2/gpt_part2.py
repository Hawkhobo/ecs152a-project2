
from browsermobproxy import Server
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import json
import csv
import os

# Parses HAR files
from analysis import analysis

HAR_FILES_PATH = 'C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/harFilesGPT/'
TOP_SITES_FILE_PATH = 'C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/top-1m.csv'

def start_server():
    server = Server("C:/Users/chaus/AppData/Local/Programs/Python/Python312/Lib/site-packages/browsermobproxy/browsermob-proxy-2.1.4/bin/browsermob-proxy")
    server.start()
    return server

def initialize_driver(proxy):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--proxy-server={proxy.proxy}")
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-third-party-cookies=false')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    return webdriver.Chrome(options=chrome_options)

def read_top_sites(file_path):
    with open(file_path, newline='') as file:
        return list(csv.reader(file, delimiter=','))

def crawl_websites(driver, proxy, top_sites):
    sites_visited = 0
    sites_failed = 0
    
    # Setting the timeout for each request to 120 seconds
    driver.set_page_load_timeout(120)

    while sites_visited != 1000:
        proxy.new_har(f'{HAR_FILES_PATH}{sites_visited + 1}_{top_sites[sites_visited][1]}.har', options={'captureHeaders': True, 'captureCookies': True})

        try:
            driver.get("http://" + top_sites[sites_visited][1])
            
            with open(f'{HAR_FILES_PATH}{sites_visited + 1}_{top_sites[sites_visited][1]}.har', 'w') as f:
                f.write(json.dumps(proxy.har))

            sites_visited += 1

        except TimeoutException as te:
            print(f'TimeoutException at {top_sites[sites_visited][1]}: {te}')
            sites_failed += 1

        except Exception as e:
            print(f'Exception at {top_sites[sites_visited][1]}: {e}')
            sites_failed += 1

        if sites_failed > 1:
            sites_visited += 1
            sites_failed = 0

    print(f'{sites_visited} sites visited, and {sites_failed} sites failed.')

def analyze_har_files(har_files):
    third_party_per_site = {}
    third_party_cookies = {}

    for file in har_files:
        third_party_per_site, third_party_cookies = analysis(file, third_party_per_site, third_party_cookies, HAR_FILES_PATH)

    return third_party_per_site, third_party_cookies

def main():
    server = start_server()
    proxy = server.create_proxy(params=dict(trustAllServers=True))
    driver = initialize_driver(proxy)
    driver.delete_all_cookies()

    # top_sites = read_top_sites(TOP_SITES_FILE_PATH)
    with open(TOP_SITES_FILE_PATH, newline = '') as file: 
        topSites = list(csv.reader(file, delimiter = ','))

    crawl_websites(driver, proxy, topSites)

    server.stop()
    driver.quit()

    har_files = os.listdir(HAR_FILES_PATH)
    third_party_per_site, third_party_cookies = analyze_har_files(har_files)

    subKeySums = [(key, sum(subkey.values())) for key, subkey in third_party_cookies.items()]
    top10Domains = sorted(subKeySums, key = lambda x: x[1], reverse = True)[:10]

    print(f'\nOur Top 10 third-party domains across the 1000 websites:')
    for i in range(10):
        print(f'\t{top10Domains[i]}')

    top10Cookies = sorted(
        ((key, subkey, value) for key, sub_dict in third_party_cookies.items() for subkey, value in sub_dict.items()),
        key=lambda x: x[2], reverse=True)[:10]
        
    print(f'\nOur Top 10 third-party cookies across the 1000 websites:')
    for i in range(10):
        print(f'\t{top10Cookies[i]}')

if __name__ == "__main__":
    main()
