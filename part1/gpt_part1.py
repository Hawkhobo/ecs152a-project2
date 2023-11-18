import socket
import struct
from time import time

# Constants
UDP_TIMEOUT = 10
MAX_PACKET_SIZE = 1024
DNS_HEADER_SIZE = 12
DNS_TYPE_A = 1
DNS_CLASS_IN = 1

def unpacking_response(packet):
    print(f'\tResponse packet: {packet}')
    
    aa, num_of = unpacking_header(packet)
    
    offset = DNS_HEADER_SIZE

    for _ in range(num_of[0]):
        while packet[offset] != 0:
            offset += 1
        offset += 5

    if aa == '1':
        offset, list_of_aa_ips = extract_rr_data(num_of[1], packet, offset, 'Answer')
        offset, list_of_ips = extract_rr_data(num_of[2], packet, offset, 'Authority')
        offset, list_of_ips = extract_rr_data(num_of[3], packet, offset, 'Additional')
        return list_of_aa_ips
    else:
        offset, list_of_ips = extract_rr_data(num_of[2], packet, offset, 'Authority')
        offset, list_of_ips = extract_rr_data(num_of[3], packet, offset, 'Additional')

    return list_of_ips

def unpacking_header(packet):
    id_values = struct.unpack('BB', packet[:2])
    identification = ''.join(chr(value) for value in id_values)
    
    flags = struct.unpack('BB', packet[2:4])
    binary_values = ''.join(f'{byte:08b}' for byte in flags)
    
    aa = binary_values[5]

    num_of = []

    for i in range(4):
        num_of_rrs = struct.unpack('BB', packet[i * 2 + 4:i * 2 + 6])
        num_of.append(num_of_rrs[1])

    return aa, num_of

def extract_rr_data(num_of, packet, offset, section):
    list_of_ips = []
    
    for _ in range(num_of):
        r_name, r_type, r_class, ttl, r_data_length = struct.unpack('!HHHIH', packet[offset:offset + 12])

        r_data_start = offset + 12
        r_data_end = r_data_start + r_data_length

        if r_type == DNS_TYPE_A and r_class == DNS_CLASS_IN:
            ipv4 = socket.inet_ntoa(packet[r_data_start: r_data_end])
            list_of_ips.append(ipv4)
        elif r_type == 28 and r_class == DNS_CLASS_IN:
            pass
        elif r_type == 2 and r_class == DNS_CLASS_IN:
            pass
    
        offset += 12 + r_data_length

    return offset, list_of_ips

def sending_to_server(packet, list_of_ips, serv_name):
    SERVER_PORT = 53
    
    for ip in list_of_ips:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(UDP_TIMEOUT)
            start = time()
            client_socket.sendto(packet, (ip, SERVER_PORT))
            response_packet = client_socket.recv(MAX_PACKET_SIZE)
            end = time()
        except Exception as e:
            print(f'\tFailed with error: {e}')
        finally:
            client_socket.close()

    print(f'\tRTT for {serv_name} DNS server was {round(end - start, 4)} seconds')
    return response_packet

def pack_query(question):
    header_section = bytearray(DNS_HEADER_SIZE)
    
    header_section[0:2] = b'\x4A\x4B'
    header_section[2:4] = b'\x00\x00'
    header_section[4:6] = b'\x00\x01'
    header_section[6:8] = b'\x00\x00'
    header_section[8:10] = b'\x00\x00'
    header_section[10:12] = b'\x00\x00'

    question_section = question
    question_section.extend(struct.pack('!HH', DNS_TYPE_A, DNS_CLASS_IN))

    dns_packet = bytearray(b'')
    dns_packet.extend(header_section)
    dns_packet.extend(question_section)

    return dns_packet

def make_http_request(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((ip, 80))
    
    request_line = b"GET / HTTP/1.1\r\n"
    header_host = f"Host: {ip}\r\n".encode('utf-8')
    header_user_agent = b"User-Agent: Mozilla/5.0\r\n"
    blank_line = b"\r\n"

    http_get = request_line + header_host + header_user_agent + blank_line

    start = time()
    s.sendall(http_get)

    response = b""

    while True:
        data = s.recv(MAX_PACKET_SIZE)
        response += data

        if b'\r\n\r\n' in response:
            headers, payload = response.split(b'\r\n\r\n', 1)

            iter_start = headers.find(b'Content-Length:')
            iter_end = headers.find(b'\r\n', iter_start)
            header_val = headers[iter_start + len(b'Content-Length:'): iter_end]
            content_length = int(header_val)
        
            if len(payload) == content_length:
                end = time()
                break

        if not data:
            break

    s.close()

    return response, round(end - start, 4), payload

if __name__ == "__main__":
    question = bytearray(b'\x03\x74\x6D\x7A\x03\x63\x6F\x6D\x00')
    dns_query = pack_query(question)

    root_servers = ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241',
                    '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
                    '202.12.27.33']

    print("\n--Root DNS Server Request/Response--\n")
    dns_response = sending_to_server(dns_query, root_servers, 'root')
    ip_tld = unpacking_response(dns_response)

    print("\n--TLD DNS Server Request/Response--\n")
    dns_response = sending_to_server(dns_query, ip_tld, 'TLD')
    ip_auth = unpacking_response(dns_response)

    print("\n--Authoritative DNS Server Request/Response--\n")
    dns_response = sending_to_server(dns_query, ip_auth, 'authoritative')
    tmz_ips = unpacking_response(dns_response)

    tmz_ip = tmz_ips[0]
    print('\nTMZ IP: ', tmz_ip)

    http_response, http_rtt, payload = make_http_request(tmz_ip)

    print('\nReturned HTTP response: ', http_response)
    print(f'\nRTT for HTTP Request/Response to tmz.com was {http_rtt} seconds')

    html_file = open('tmz_payload.html', 'w', encoding='utf-8')
    html_file.write(payload.decode('utf-8'))
