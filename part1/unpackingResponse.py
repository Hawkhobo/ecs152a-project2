import socket
import struct 

def unpackingResponse(packet):

    print(f'Response packet: {packet}')
    
    # We want to extract the Resource Record of Type A, nominating a valid TLD DNS server
    # We know that Root DNS Servers return a list of TLD servers, given a query. So we can grab the first one
    # From Wireshark, can observe that the TLD IP's are cached in the root DNS server. In the Additional section! 
    
    # Print out the header section and its contents
    # aa is the Authoritative Answer flag. Tells us if we've found tmz.com's IP 
    # numOf contains the number of [0] Questions, [1] Answer RRs, [2] Authority RRs
    print('\n--Contents of Header Section--')
    aa, numOf = unpackingHeader(packet)
 
    # Skipping Header Section. Fixed 12 bytes 
    offset = 12

    # Skipping over Question Section. Each for iter is a separate Query
    for _ in range (numOf[0]):
        # Iterate past Queries until we hit our null byte
        while packet[offset] != 0:
            offset += 1
        # Skipping Null Byte, Qtype (2 Bytes), and Qclass (2 Bytes)
        offset += 5

    # Do we have an Answer section?
    if aa == 1:
        offset, listOfIPs = extractRRData(numOf[1], packet, offset)
    # If not, iterate over the other RR's
    else:
        # Iterate over the Authority section, returning any Type A RR IP's
        offset, listOfIPs = extractRRData(numOf[2], packet, offset)
        # Iterate over the Additional section, returning any Type A RR IP's
        offset, listOfIPs2 = extractRRData(numOf[3], packet, offset)
        # Combine Type A RR's of Authority and Additional
        listOfIPs.append(listOfIPs2)

    return listOfIPs

# Method for unpacking Header section of a DNS message
def unpackingHeader(packet):
    
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

    numOf = []

    numOfQuestions = struct.unpack('BB', packet[4:6])
    numOf.append(numOfQuestions[1])
    print(f'\tNumber of Queries: {numOfQuestions[1]}')

    numOfAnswerRRs = struct.unpack('BB', packet[6:8])
    numOf.append(numOfAnswerRRs[1])
    print(f'\tNumber of Answers: {numOfAnswerRRs[1]}')

    numOfAuthorityRRs = struct.unpack('BB', packet[8:10])
    numOf.append(numOfAuthorityRRs[1])
    print(f'\tNumber of Authority RR\'s: {numOfAuthorityRRs[1]}')
    
    numOfAdditionalRRs = struct.unpack('BB', packet[10:12])
    numOf.append(numOfAdditionalRRs[1])
    print(f'\tNumber of Additional RR\'s: {numOfAdditionalRRs[1]}')

    return aa, numOf

def extractRRData(numOf, packet, offset):
    # Extracting new IPs from RRs
    listOfIPs = []
    # In the range of the number of resource records (could be Answer, Authoritative, or Additional)
    for _ in range (numOf):

        # Unpack the first 12 bytes of a given RR. The 4-tuple, and the data length of the last value (our Name Server)
        r_name, r_type, r_class, ttl, r_data_length = struct.unpack('!HHHIH', packet[offset:offset + 12])

        # Beginning of RDATA in current RR
        r_data_start = offset + 12
        # end of RDATA in current RR
        r_data_end = r_data_start + r_data_length

        # Check if the answer is a Type A RR (IPv4). Only returning IPv4
        # Any other type is passed over, and we continue to unpack the response
        if r_type == 1 and r_class == 1:
            # Unpack RDATA, use socket method to store as IPv4 string
            listOfIPs.append(socket.inet_ntoa(packet[r_data_start: r_data_end]))

        # Move to the next RR
        offset += 12 + r_data_length

    return offset, listOfIPs