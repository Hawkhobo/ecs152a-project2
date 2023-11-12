
import socket

# Construct a DNS Query (packet request) given passed-in parameters
def packQuery():

    # Declare header section, fill in values field-to-field (12 bytes total)
    headerSection = bytearray(12)
    
    # First two bytes is `Identification` field
    # JK to hex \x4A\x4B
    headerSection[0:2] = b'\x4A\x4B'

    # Next two bytes is a list of flags: 
    # 1-bit QR, 4-bit OPCODE, 1-bit AA, 1-bit TC, 1-bit RD, 1-bit RA, 3-bit Z, and a 4-bit RCODE 
    # Each flag is read left-to-right in headerSection[2:4]    
    # Set everything to 0. Most flags are response-oriented (not query-oriented), and we prefer iterative traversal over recursive traversal for this exercise.
    headerSection[2:4] = b'\x00\x00'

    # Next two bytes is the number of questions
    headerSection[4:6] = b'\x00\x01'

    # Next two bytes is the number of answer RRs
    headerSection[6:8] = b'\x00\x00'

    # Next two bytes is the number of authority RRs
    headerSection[8:10] = b'\x00\x00'

    # Next two bytes is the number of additional RRs
    headerSection[10:12] = b'\x00\x00'

    print(f'Header section of DNS Query: {headerSection}')

    # Declare Question Section 
    # Encoded tmz.com to 3 tmz 3 com 0
    # To binary 0000 0011 0111 0100 0110 1101 0111 1010 0000 0011 0110 0011 0110 1111 0110 1101 0000 0000
    # To hex \x03\x74\x6D\x7A\x03\x63\x6F\x6D\x00
    questionSection = bytearray(b'\x03\x74\x6D\x7A\x03\x63\x6F\x6D\x00')

    # QType is Type A: 0000 0000 0000 0001 
    questionSection.extend(b'\x00\x01')

    # QClass is an internet lookup: 0000 0000 0000 0001
    questionSection.extend(b'\x00\x01')

    print(f'Question section of DNS Query: {questionSection}')
    
    # Declare Answer Section 
    answerSection = bytearray(b'')

    # Declare Authority Section 
    authoritySection = bytearray(b'')

    # Declare Additional Information Section 
    additionalInfoSection = bytearray(b'')

    # Assembling the packet
    dnsPacket = bytearray(b'')
    dnsPacket.extend(headerSection)
    dnsPacket.extend(questionSection)

    return dnsPacket

def sendingToRoot(packet):

    rootServers = {
        'a.root-servers.net': '198.41.0.4', 
        'b.root-servers.net': '199.9.14.201',
        'c.root-servers.net': '192.33.4.12', 
        'd.root-servers.net': '199.7.91.13', 
        'e.root-servers.net': '192.203.230.10', 
        'f.root-servers.net': '192.5.5.241', 
        'g.root-servers.net': '192.112.36.4', 
        'h.root-servers.net': '198.97.190.53', 
        'i.root-servers.net': '192.36.148.17', 
        'j.root-servers.net': '192.58.128.30', 
        'k.root-servers.net': '193.0.14.129', 
        'l.root-servers.net': '199.7.83.42', 
        'm.root-servers.net': '202.12.27.33'}

    # Port 53 is reserved for the DNS Protocol 
    SERVER_PORT = 53
    
    # Test each root server
    # Start the timer. Allow for a 10 second elapse
    for root, IP in rootServers.items():

        print(f'Testing root server {root}:')
        
        try:
            # Open a new socket for given root server, send a packet, if it does connect within 10 seconds, move on to next root 
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("UDP listening for 10 seconds")
            clientSocket.settimeout(10)
            clientSocket.sendto(packet, (IP, SERVER_PORT))
            responsePacket = clientSocket.recv(1024)
        except:
            print('Failed')
        finally:
            clientSocket.close()
            break

    return responsePacket

def unpackingResponse(packet):
    print(f'Response packet: {packet}')

    # We want to extract the Resource Record of Type A, nominating a valid TLD DNS server
    # We know that Root DNS Servers return a list of TLD servers, given a query. So we can grab the first one
    # Need to iterate to the Answer section in the response packet, and inspect the resource records there

    numOfAnswer = packet[6:8].decode()
    print(numOfAnswer)
    
    

if __name__ == "__main__":

    # Build our DNS query for the root DNS server
    dnsQuery = packQuery()

    # Send to the root DNS server
    dnsResponse = sendingToRoot(dnsQuery)

    # Unpacking Response
    ipTLD = unpackingResponse(dnsResponse)

    # Send query to TLD DNS server
    
