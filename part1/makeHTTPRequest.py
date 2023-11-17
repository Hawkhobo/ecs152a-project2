import socket

# Use the time module to measure RTT
from time import time

def makeHTTPRequest(ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Measure before and after 3-way handshake. Gives us 1 RTT
    start = time()
    s.connect((ip, 80))
    end = time()
    
    requestLine = b"GET / HTTP/1.1\r\n"
    # must be an f-string. No f-byte data type available
    headerHost = f"Host: {ip}\r\n".encode('utf-8')
    # even with specified User-Agent:, tmz still blocks request
    headerUserAgent = b"User-Agent: Mozilla/5.0\r\n"
    blankLine = b"\r\n"

    httpGET = requestLine + headerHost + headerUserAgent + blankLine

    s.sendall(httpGET)

    response = b""
    # Parse incoming response, piece by piece, as buffer allows
    while True:
        data = s.recv(1024)
        response += data

        # Check if we're past headers
        if b'\r\n\r\n' in response:
            # If we're past headers, split into header section and payload section
            # Use \r\n\r\n to make the split
            headers, payload = response.split(b'\r\n\r\n', 1)

            # Determine the payload length

            # First figure out where to look for length. At Content-Length: header
            iter_start = headers.find(b'Content-Length:')

            # From iter_start, get index of first \r\n seen
            iter_end = headers.find(b'\r\n', iter_start)
            # Index at Content-Length:, plus it's length, yields the index right after the `:`
            # Then, index at start of \r\n immediately following Content-Length:
            # Return values between these two indexes. Value of header.
            header_val = headers[iter_start + len(b'Content-Length:'): iter_end]
            # Convert to integer for numerical comparison
            content_length = int(header_val)
        
            # Does actual length of payload match Content-Length:?
            # If not, still have more chunks to process. Otherwise break.
            if(len(payload) == content_length):
                break

        # Otherwise, break if no more data to return
        if not data:
            break

    s.close()

    return response, round(end - start, 4), payload