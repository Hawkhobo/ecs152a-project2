import socket

def makeHTTPRequest(ip):

     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s.connect(ip, 80)
    
     request = f"GET/HTTP/2\r\nHost: {ip}\r\n\r\n"

     s.sendall(request.encode())

     response = b""
     while True:
         data = s.recv(1024)
         if not data:
             break
         response += data

     s.close()

     return response