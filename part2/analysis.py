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
    # Parse for third party requests (using url)
    requestURLsList = []
    entries = json_data.get('log', {}).get('entries', [])

    for i in range(len(entries)):

        # Request cookies are interesting. Denoted by URL on request-level, not domain on cookie-level
        # So logic differs a bit from responses
        requestCookie = entries[i].get('request', {}).get('cookies', [])
        requestURLs = entries[i].get('request', {})

        for req in range(len(requestCookie)):
            if requestURLs.get('url'):
                requestCookieList.append([requestURLs.get('url'), requestCookie[req].get('name')])
                requestURLsList.append(requestURLs.get('url'))
            
        # Response cookiesa are simple. Check for anything in cookies[], and return domain and name.
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
    # If we have very small domains, add a `.` For instance, keeps `mi.com` from being just `mi`
    # Lowers false third-party classification. For instance `mi` could pair with `microsoft`, but `mi.` will not 
    if len(siteName) < 6:
        siteName += '.'
    
    # Counting number of requests to third party domains. Use full web page domain provided
    end = har.rfind('.')
    har = har[start + 1: end]
    sites[har] = 0
    for url in requestURLsList:
       if siteName not in url:
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