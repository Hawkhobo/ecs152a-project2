import json

def analysis(har, sites, cookies, path): 

    # Load the present har file into a JSON instance
    with open(f'{path}{har}', 'r', encoding='utf-8') as file:
        try: 
            json_data = json.load(file)
        except:
            print('death')

    # Parse for cookie domains
    requestCookieList = []
    responseCookieList = []
    entries = json_data.get('log', {}).get('entries', [])

    for i in range(len(entries)):

        requestCookie = entries[i].get('request', {}).get('cookies', [])

        for req in range(len(requestCookie)):
            if requestCookie[req].get('domain'):
                requestCookieList.append([requestCookie[req].get('domain'), requestCookie[req].get('name')])
            
        responseCookie = entries[i].get('response', {}).get('cookies', [])
        
        for res in range(len(responseCookie)):
            if responseCookie[res].get('domain'):
                responseCookieList.append([responseCookie[res].get('domain'), responseCookie[res].get('name')])

    cookieList = requestCookieList + responseCookieList

    commonDomains = ['.com', '.net', '.org', '.edu', '.co', '.ru', '.uk', '.jp', '.io', '.it', '.br', '.cn']

    start = har.find("_")
    # Check if the word has a common domain from web crawling
    # If it does, we'll remove it. Otherwise, just remove .har
    end = 0
    for i in range(0, len(commonDomains)):
        if har.find(commonDomains[i]) != -1:
            end = har.find(commonDomains[i])
            break
        else:
            end = har.rfind('.')
    # second-level domain of current HAR
    siteName = har[start + 1: end]
    # If we have very small domains, keep a `.` For instance, keeps `mi.com` from being just `mi`
    if len(siteName) < 4:
        siteName = siteName + '.'
    
    # Counting number of requests to third party domains. Use full web page domain provided
    end = har.rfind('.')
    har = har[start + 1: end]
    sites[har] = 0
    for domain in cookieList:
       if siteName not in domain[0]:
           sites[har] += 1
    
    print(f'Number of requests to third-party domains for {har}: {sites[har]}')

    # Adding to current list
    for domain in cookieList:
        if siteName not in domain[0]:
            if domain[0] in cookies:
                if domain[1] in cookies[domain[0]]:
                    cookies[domain[0]][domain[1]] += 1
                else:
                    cookies[domain[0]][domain[1]] = 1
            else:
                # Adds new key to dictionary
                cookies[domain[0]] = {}
                cookies[domain[0]][domain[1]] = 1

    return sites, cookies  