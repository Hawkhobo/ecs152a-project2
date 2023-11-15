import socket

def sendingToServer(packet, listOfIPs):

    # Port 53 is reserved for the DNS Protocol 
    SERVER_PORT = 53
    
    # Test each server
    # Start the timer. Allow for a 10 second elapse
    for IP in listOfIPs:

        print(f'Testing server {listOfIPs[IP]}:')
        
        try:
            # Open a new socket for given server, send a packet, if it does connect within 10 seconds, move on to next 
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("UDP listening for 10 seconds")
            clientSocket.settimeout(10)
            clientSocket.sendto(packet, (listOfIPs[IP], SERVER_PORT))
            responsePacket = clientSocket.recv(1024)
        except:
            print('Failed')
        finally:
            clientSocket.close()
            break

    return responsePacket