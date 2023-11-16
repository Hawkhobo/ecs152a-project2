# Code has been sampled from Muhammad Haroon's code, with modifications.
# Original code: https://github.com/Haroon96/ecs152a-fall-2023/blob/main/week6/proxy-code/selenium_proxy.py

from browsermobproxy import Server
from selenium import webdriver
import json
import csv

# create a browsermob server instance
server = Server("browsermob-proxy/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy(params=dict(trustAllServers=True))

# create a new chromedriver instance
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=chrome_options)

# do crawling
proxy.new_har("harCollection")

file = open('top-1m.csv', newline = '')
topSites = csv.reader(file, delimiter = ',')

# Only need to get the har of top 1000
for site in range(1000):
    driver.get(topSites[site])

    # Not sure if we need to dump into json files (cuz there would be 1000)
    # # write har file to json
    # with open('harCollection.har', 'w') as f:
    #     f.write(json.dumps(proxy.har))

# stop server and exit
server.stop()
driver.quit()
