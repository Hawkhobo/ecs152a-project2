
import socket
import struct
from sys import getsizeof

# Construct a DNS Query (packet request) given passed-in parameters
def packQuery():

    # Declare header section, fill in values byte-to-byte
    headerSection = bytearray(12)
    
    # Construct header bytes, then append together
    #headerSection[0:2] =
    
    # headerSection[2:4]

    flags = bytearray(b'0000000000000000')

    numOfQuestions = bytearray(b'xx')
    numOfAnswerRR = bytearray(b'xx')
    numOfAuthoritativeRR = bytearray(b'xx')
    numOfAdditionalRR = bytearray(b'xx')

    header = bytearray(b'')
    # header.append(identification[0])
    # header.append(flags[0])
    # header.append(numOfQuestions[0])
    # header.append(numOfAnswerRR[0])
    # header.append(numOfAuthoritativeRR[0])
    # header.append(numOfAdditionalRR[0])
    # print(header)



if __name__ == "__main__":

    # Build our DNS query for the root DNS server
    packQuery()

    # Send to the root DNS server
