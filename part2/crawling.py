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

# Create a new chromedriver instance
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options = chrome_options)

# Setting the timeout for each request to 10 seconds
driver.set_page_load_timeout(10)

# # do crawling
# proxy.new_har("myhar")
# driver.get("http://www.cnn.com")

# # write har file
# with open('myhar.har', 'w') as f:
#     f.write(json.dumps(proxy.har))

# Read top sites
with open("C:/Users/chaus/visualstudio/ECS-152A/Project2/ecs152a-project2/part2/top-1m.csv", newline = '') as file: 
    topSites = csv.reader(file, delimiter = ',')

# Do crawling
proxy.new_har()

# Only need to get the har of top 1000
site = 0
sitesVisited = 0
while sitesVisited != 5:

    try:
        driver.get(topSites[site])

        # write har file to json
        with open('currentHar.har', 'w') as f:
            f.write(json.dumps(proxy.har))

        # parse the har file for third-party cookies, and store analytics
        # analysis()

        site += 1
        sitesVisited += 1
        
    except TimeoutException:
        site += 1

# stop server and exit
server.stop()
driver.quit()
