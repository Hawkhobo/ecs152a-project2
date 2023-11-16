import socket

def makeHTTPRequest(ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, 80))
    
    requestLine = b"GET / HTTP/1.1\r\n"
    # must be an f-string. No f-byte data type available
    headerHost = f"Host: {ip}\r\n".encode('utf-8')
    # even with specified User-Agent:, tmz still blocks request
    headerUserAgent = b"User-Agent: Mozilla/5.0\r\n"
    blankLine = b"\r\n"

    httpGET = requestLine + headerHost + headerUserAgent + blankLine

    s.sendall(httpGET)

    response = b""
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data

    s.close()

    return response