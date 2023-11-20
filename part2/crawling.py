# Code has been sampled from Muhammad Haroon's code, with modifications.
# Original code: https://github.com/Haroon96/ecs152a-fall-2023/blob/main/week6/proxy-code/selenium_proxy.py

from browsermobproxy import Server
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

import json
import csv

# Use OS to grab HAR file-names for analysis()
import os

# Parses HAR files
from analysis import analysis

HAR_FILE_PATH = 'C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/harFiles/'

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

# Number of sites that have been tried
site = 0
# Number of sites that have been successfull
sitesVisited = 0
# Number of sites that have failed
sitesFailed = 0
# Has the failed site been retried
secondTry = False

# Get the har of 1000 sites from the list
while sitesVisited != 0:

    # Do crawling
    proxy.new_har(f'{HAR_FILE_PATH}{site + 1}_{topSites[site][1]}.har', options = {'captureHeaders': True, 'captureCookies': True})

    try:
        driver.get("http://" + topSites[site][1])

        # Write har file to json
        with open(f'{HAR_FILE_PATH}{site + 1}_{topSites[site][1]}.har', 'w') as f:
            f.write(json.dumps(proxy.har))

        site += 1
        sitesVisited += 1
        
    except Exception as e:

        if secondTry == False:
            secondTry = True
            print("Trying site again")
        else:
            site += 1
            sitesFailed += 1
            secondTry = False
            print("Second try failed")

        print(f'Exception at {topSites[site][1]}: {e}')

# Stop server and exit
server.stop()
driver.quit()

# Sites visited
print(f'Quitting driver. {sitesVisited} sites visited, and {sitesFailed} sites failed. \n')

# Store harFile names in a list
harFiles = os.listdir('C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/harFiles')

thirdPartyPerSite = {}
thirdPartyCookies = {}

# Parse the har file for third-party cookies, and store analytics
# Run for each har file we have
for file in range(len(harFiles)):
    thirdPartyPerSite, thirdPartyCookies = analysis(harFiles[file], thirdPartyPerSite, thirdPartyCookies, HAR_FILE_PATH)

# Acquire 10 largest values from thirdPartyCookies, by domain
# First get sum of subkeys across a given key. Returns a dictionary that has key (domain), and value (sum of subkeys)
subKeySums = [(key, sum(subkey.values())) for key, subkey in thirdPartyCookies.items()]
# Grab the 10 largest from the above sum of subkeys
top10Domains = sorted(subKeySums, key = lambda x: x[1], reverse = True)[:10]

print(f'\nOur Top 10 third-party domains across the 1000 websites:')
for i in range(10):
    print(f'\t{top10Domains[i]}')

# Now, Acquire 10 largest values from thirdPartyCookies, by name (subkey)
top10Cookies = sorted(
    ((key, subkey, value) for key, sub_dict in thirdPartyCookies.items() for subkey, value in sub_dict.items()),
    key=lambda x: x[2], reverse=True)[:10]
    
print(f'\nOur Top 10 third-party cookies across the 1000 websites:')
for i in range(10):
    print(f'\t{top10Cookies[i]}')
    