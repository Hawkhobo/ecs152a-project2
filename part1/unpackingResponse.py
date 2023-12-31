import socket
import struct 

def unpackingResponse(packet):

    print(f'\tResponse packet: {packet}')
    
    # Extract a Resource Record of Type A, nominating a valid DNS server
    # DNS servers return a list of the next server-type in the hierarchy
    
    # Print out the header section and its contents
    # numOf contains the number of [0] Questions, [1] Answer RRs, [2] Authority RRs, [3] Additional RRs
    print('\n\t--Contents of Header Section--')
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

    # Do we have any Answer resource records that are authoritative?
    if aa == '1':
        offset, listOfAAIPs = extractRRData(numOf[1], packet, offset, 'Answer')
         # Iterate over the Authority section, returning any Type A RR IP's
        offset, listOfIPs = extractRRData(numOf[2], packet, offset, 'Authority')
        # Iterate over the Additional section, returning any Type A RR IP's
        offset, listOfIPs = extractRRData(numOf[3], packet, offset, 'Additional')
        return listOfAAIPs
    # If not, iterate over the other RR's
    else:
        # Iterate over the Authority section, returning any Type A RR IP's
        offset, listOfIPs = extractRRData(numOf[2], packet, offset, 'Authority')
        # Iterate over the Additional section, returning any Type A RR IP's
        offset, listOfIPs = extractRRData(numOf[3], packet, offset, 'Additional')
        # Combine Type A RR's of Authority and Additional

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

# If it is an Answer, Authority, or Additional section, run a RR look-through method
def extractRRData(numOf, packet, offset, section):
    # Extracting new IPs from RRs
    listOfIPs = []
    # In the range of the number of resource records (could be Answer, Authoritative, or Additional)
    print(f'\t\n--Resource Records stored in the {section} section--\n')
    print(f'\tFormat: (TYPE, IP (or Name Server if TYPE is NS))\n')
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
            ipv4 = socket.inet_ntoa(packet[r_data_start: r_data_end])
            print(f'(A, {ipv4})')
            listOfIPs.append(ipv4)
        # Print out IPv6, but don't store. Only using IPV4's
        elif r_type == 28 and r_class == 1:
            print(f'(AAAA, {socket.inet_ntop(socket.AF_INET6, packet[r_data_start: r_data_end])})')
        # Print out NS RRs, don't store 
        elif r_type == 2 and r_class == 1:
            # Some Name Servers are 4 bytes due to a compression algorithm
            # decode() doesn't work well on these. Let decode() handle with an error exception
            print('(NS, ', packet[r_data_start: r_data_end].decode(errors='replace'), ')')
    
                


        # Move to the next RR
        offset += 12 + r_data_length

    return offset, listOfIPs