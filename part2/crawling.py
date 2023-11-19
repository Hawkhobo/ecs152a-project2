# Code has been sampled from Muhammad Haroon's code, with modifications.
# Original code: https://github.com/Haroon96/ecs152a-fall-2023/blob/main/week6/proxy-code/selenium_proxy.py

from browsermobproxy import Server
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

import json
import csv

# Parses our HAR files
from analysis import analysis

# Create a browsermob server instance
server = Server("C:/Users/chaus/AppData/Local/Programs/Python/Python312/Lib/site-packages/browsermobproxy/browsermob-proxy-2.1.4/bin/browsermob-proxy")
server.start()

proxy = server.create_proxy(params = dict(trustAllServers = True))

# Create a new chromedriver instance. Add arguments to allow for third-party requests
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-third-party-cookies=false')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
driver = webdriver.Chrome(options = chrome_options)

driver.delete_all_cookies()

# Setting the timeout for each request to 120 seconds
driver.set_page_load_timeout(120)

# Read top sites
with open("C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/top-1m.csv", newline = '') as file: 
    topSites = list(csv.reader(file, delimiter = ','))

# get the har of 1000 sites from the list
site = 135
sitesVisited = 130
while sitesVisited != 1000:

    # Do crawling
    proxy.new_har(f'C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/harFiles/{site + 1}_{topSites[site][1]}.har', options = {'captureHeaders': True, 'captureCookies': True})

    try:
        driver.get("http://" + topSites[site][1])

        # write har file to json
        with open(f'C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/harFiles/{site + 1}_{topSites[site][1]}.har', 'w') as f:
            f.write(json.dumps(proxy.har))

        site += 1
        sitesVisited += 1
        
    except Exception as e:
        site += 1
        print(f'Exception at {topSites[site][1]}: {e}')

# stop server and exit
server.stop()
driver.quit()

# parse the har file for third-party cookies, and store analytics
# analysis()
