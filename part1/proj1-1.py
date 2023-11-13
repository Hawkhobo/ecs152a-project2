
import socket
import struct

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

def sendingToServer(packet, listOfIPs):

    # Port 53 is reserved for the DNS Protocol 
    SERVER_PORT = 53
    
    # Test each server
    # Start the timer. Allow for a 10 second elapse
    for IP in range(len(listOfIPs)):

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

def unpackingResponse(packet):
    
    print(f'Response packet: {packet}')

    # We want to extract the Resource Record of Type A, nominating a valid TLD DNS server
    # We know that Root DNS Servers return a list of TLD servers, given a query. So we can grab the first one
    # Need to iterate to the Answer section in the response packet, and inspect the resource records there

    # Header Section
    print('\n--Contents of Header Section--')

    # Ensure the Identification matches the DNS query we built 
    id_values = struct.unpack('BB', packet[:2])
    identification = ''.join(chr(value) for value in id_values)
    print(f'\tIdentification: {identification}')
    
    # Inspect our flags
    flags = struct.unpack('BB', packet[2:4])
    binary_values = ''.join(f'{byte:08b}' for byte in flags)
    
    print(f'\t--Flags field--')
    # 1-bit QR, 4-bit OPCODE, 1-bit AA, 1-bit TC, 1-bit RD, 1-bit RA, 3-bit Z, and a 4-bit RCODE 
    print(f'\t\tQR flag: {binary_values[0]}')
    print(f'\t\tOPCODE: {binary_values[1:5]}')

    aa = binary_values[5]
    print(f'\t\tAA flag: {aa}')
    print(f'\t\tTC flag: {binary_values[6]}')
    print(f'\t\tRD flag: {binary_values[7]}')
    print(f'\t\tRA flag: {binary_values[8]}')
    print(f'\t\tZ flag: {binary_values[9:12]}')
    print(f'\t\tRCODE: {binary_values[12:16]}')

    numOfQuestions = struct.unpack('BB', packet[4:6])
    print(f'\tNumber of Queries: {numOfQuestions[1]}')
    numOfAnswerRRs = struct.unpack('BB', packet[6:8])
    print(f'\tNumber of Answers: {numOfAnswerRRs[1]}')
    numOfAuthorityRRs = struct.unpack('BB', packet[8:10])
    print(f'\tNumber of Authority RR\'s: {numOfAuthorityRRs[1]}')
    numOfAdditionalRRs = struct.unpack('BB', packet[10:12])
    print(f'\tNumber of Additional RR\'s: {numOfAdditionalRRs[1]}')


    # # Skipping over Question Section
    # offset = 12
    # for _ in range (numOfQuestions):
    #     while int.from_bytes(packet[offset], "big") != 0:
    #         offset += 1
    #     offset += 5

    # # Extracting new IPs from Answer Section
    # listOfIPs = []
    # for _ in range (numOfAnswers):
    #     r_type, r_class, ttl, r_data_length = struct.unpack('!HHIH', packet[offset:offset + 10])

    #     # Check if the answer is an A record (IPv4)
    #     if r_type == 1 and r_class == 1:
    #         listOfIPs.append(socket.inet_ntoa(packet[offset + 10:offset + 14]))

    #     # Move to the next answer
    #     offset += 10 + r_data_length

    # return listOfIPs

if __name__ == "__main__":

    # Build our DNS query for the root DNS server
    dnsQuery = packQuery()

    rootServers = ['198.41.0.4', '199.9.14.201', 
                   '192.33.4.12', '199.7.91.13', 
                   '192.203.230.10', '192.5.5.241', 
                   '192.112.36.4', '198.97.190.53', 
                   '192.36.148.17', '192.58.128.30', 
                   '193.0.14.129', '199.7.83.42', 
                   '202.12.27.33']

    # Send to the root DNS server
    dnsResponse = sendingToServer(dnsQuery, rootServers)

    # Unpacking Response
    ipTLD = unpackingResponse(dnsResponse)

    # # Send query to TLD DNS server
    # dnsResponse = sendingToServer(dnsQuery, ipTLD)
    
