import socket

# Use the time module to measure RTT
from time import time

def sendingToServer(packet, listOfIPs, serv_name):

    # Port 53 is reserved for the DNS Protocol 
    SERVER_PORT = 53
    
    # Test each server
    # Start the timer. Allow for a 10 second elapse
    for IP in range(len(listOfIPs)):

        print(f'\tRequesting server {listOfIPs[IP]}:')
        
        try:
            # Open a new socket for given server, send a packet, if it does connect within 10 seconds, move on to next 
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("\tUDP listening for 10 seconds")
            clientSocket.settimeout(10)
            # Start measuring RTT moment request is sent
            start = time()
            clientSocket.sendto(packet, (listOfIPs[IP], SERVER_PORT))
            responsePacket = clientSocket.recv(1024)
            end = time()
            # Stop measuring RTT moment response is received 
        except:
            print('\tFailed')
        finally:
            clientSocket.close()
            print(f'\tRTT for {serv_name} DNS server was {round(end - start, 4)} seconds')
            break

    return responsePacket