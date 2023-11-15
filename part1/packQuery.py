import socket

# Construct a DNS Query (packet request) given passed-in parameters
def packQuery(question):

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
    questionSection = question

    # QType is Type A: 0000 0000 0000 0001 
    questionSection.extend(b'\x00\x01')

    # QClass is an internet lookup: 0000 0000 0000 0001
    questionSection.extend(b'\x00\x01')

    print(f'Question section of DNS Query: {questionSection}')

    # Answer, Authority, and Additional sections are not applicable in the DNS query

    # Assembling the packet
    dnsPacket = bytearray(b'')
    dnsPacket.extend(headerSection)
    dnsPacket.extend(questionSection)

    return dnsPacket
