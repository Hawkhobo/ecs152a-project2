# Import our various Python methods, using the socket and struct library. 
from packQuery import packQuery
from sendingToServer import sendingToServer
from unpackingResponse import unpackingResponse
from makeHTTPRequest import makeHTTPRequest

# Use the time module to measure RTT
from time import time

if __name__ == "__main__":

    # Encoded tmz.com to 3 tmz 3 com 0
    # To binary 0000 0011 0111 0100 0110 1101 0111 1010 0000 0011 0110 0011 0110 1111 0110 1101 0000 0000
    # To hex \x03\x74\x6D\x7A\x03\x63\x6F\x6D\x00
    question = bytearray(b'\x03\x74\x6D\x7A\x03\x63\x6F\x6D\x00')

    # Build our DNS query for the root DNS server, for tmz.com question
    dnsQuery = packQuery(question)

    # Root servers on https://www.iana.org/domains/root/servers
    rootServers = ['198.41.0.4', '199.9.14.201', 
                   '192.33.4.12', '199.7.91.13', 
                   '192.203.230.10', '192.5.5.241', 
                   '192.112.36.4', '198.97.190.53', 
                   '192.36.148.17', '192.58.128.30', 
                   '193.0.14.129', '199.7.83.42', 
                   '202.12.27.33']

    print("\n--Root DNS Server Request/Response--\n")
    # Send query to a root DNS server
    # Begin measuring time for RTT of DNS hierarchy traversal
    start = time()
    dnsResponse = sendingToServer(dnsQuery, rootServers)

    # Unpack response of root DNS
    ipTLD = unpackingResponse(dnsResponse)

    print("\n--TLD DNS Server Request/Response--\n")
    # Send query to a TLD DNS server
    dnsResponse = sendingToServer(dnsQuery, ipTLD)

    # Unpack response of TLD DNS
    ipAuth = unpackingResponse(dnsResponse)

    print("\n--Authoritative DNS Server Request/Response--\n")
    # Send query to an Authoritative DNS server
    dnsResponse = sendingToServer(dnsQuery, ipAuth)

    # Moment final response is received, stop time, get RTT
    end = time()

    # Unpack response of Authoritative DNS 
    tmzIPs = unpackingResponse(dnsResponse)

    # Arbitrarily grab one of these IPs. Can choose any; all duplicate servers of TMZ.com
    tmzIP = tmzIPs[0]
    print('TMZ IP: ', tmzIP)

    print(f'RTT for DNS traversal was {round(end - start, 4)} seconds')

    # Start time for HTTP
    start = time()

    # Build an HTTP GET packet for tmz.com, and make the request
    httpResponse = makeHTTPRequest(tmzIP)

    # End time for HTTP
    end = time()

    # Our response from TMZ.com 
    print(httpResponse)

    print(f'RTT for HTTP Request/Response to tmz.com was {round(end - start, 4)} seconds')

    # Acquire the entity body (HTML object) from response and return as an HTML page

    
