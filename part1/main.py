
import socket
import struct

# Import our various Python methods, using the socket and struct library. 
from packQuery import packQuery
from sendingToServer import sendingToServer
from unpackingResponse import unpackingResponse


# def makingHTTPRequest(ip):

#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect(ip, 80)
    
#     request = f"GET/HTTP/2\r\nHost: {ip}\r\n\r\n"

#     s.sendall(request.encode())

#     response = b""
#     while True:
#         data = s.recv(1024)
#         if not data:
#             break
#         response += data

#     s.close()

#     return response

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

    # Send query to a root DNS server
    dnsResponse = sendingToServer(dnsQuery, rootServers)

    # Unpack response of root DNS
    ipTLD = unpackingResponse(dnsResponse)

    # Send query to a TLD DNS server

    # Send query to an Authoritative DNS server

    
    # dnsResponse = sendingToServer(dnsQuery, ipTLD)
    
