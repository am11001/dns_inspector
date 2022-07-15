import argparse
import socket
import time
import random
import struct

class DnsClient:
    def __init__(self, params):
        self.timeout = params.timeout
        self.retries = params.max_retries
        self.port = params.port
        if(params.mx):
            self.requesttype = 'MX'
        elif(params.ns):
            self.requesttype = 'NS'   
        else:
            self.requesttype = 'A'
        self.server = params.server[1:]
        self.name = params.name
        print("DNS Client sending request for", self.name)
        print("Server:", self.server)
        print("Request type:",self.requesttype)
  
def sendquery(self, packet, num):
     if num > self.retries:
        print(f"ERROR: Maximum number of retries {self.retries} exceeded")
        return
     try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #initialize socket
        sock.settimeout(self.timeout) #set timeout
        startt = time.time()   #starttime
        sock.sendto(packet, (self.server, self.port)) #send query
        socketresponse, _ = sock.recvfrom(512) #recieve response
        endt = time.time() #record end time
        print(f'Response received after {(endt-startt)} seconds ({num} retries)')
        sock.close() #close socket
        #do shit with socketresponse
        response = setoutput(socketresponse)

        print(f"***Answer Section ({num} records)***")
    
        


     except socket.timeout as e:
        print(f"ERROR: Timeout number {num} ...")
        sendquery(self,  packet, num + 1)
     except socket.error as e:
        print(f'ERROR creating socket: {e}')
     except (socket.gaierror, socket.herror) as e:
        print(f"ERROR Host/Address related error: {e}")
     except Exception as e:
        print(e)


def setinput(args):
    #id, flags, question, answer, authority, additional
    packet = struct.pack('>HHHHHH', random.getrandbits(16), 0x0100, 0x0001, 0x0000, 0x0000, 0x0000)
    for i in args.name.split('.'):
        packet += struct.pack('B', len(i))
        for j in i:
            packet += struct.pack('c', j.encode('utf-8'))
    packet += struct.pack('B', 0)
    #type of query
    if args.mx:
        packet += struct.pack('>H', 0x000F)
    elif args.ns:
        packet += struct.pack('>H', 0x0002)
    else:
        packet += struct.pack('>H', 0x0001)
    packet += struct.pack(">H", 1) #queryclass
    return packet

def setoutput(args):
    response = {}
    #header
    header = {}
    id, flags, qdcount, ancount, nscount, arcount = struct.Struct('!6H').unpack_from(args)
    header['id'] = id
    header['qdcount'] = qdcount
    header['ancount'] = ancount
    header['nscount'] = nscount
    header['arcount'] = arcount
    #headers QR
    #headers opcode
    #headers AA
    #headers TC
    #headers RD
    #headers RA
    #headers Z
    #headers Rcode
    






    
    response['header'] = header
    return response

#maybe change some descriptions
def parse():
    parser = argparse.ArgumentParser(description='Use this command line tool to query a DNS server')
    parser.add_argument("-t", "--timeout", nargs='?', type=int, default=5,
                        help="timeout(optional) gives how long to wait, in seconds, \
                            before retransmitting an unanswered query")
    parser.add_argument("-r", "--max-retries", nargs='?', type=int, default=3,
                        help="max-retries(optional) is the maximum number of times \
                             to retransmit an unanswered query before giving up.")
    parser.add_argument("-p", "--port", type=int, nargs='?', default=53,
                        help="port(optional) is the UDP port number of the DNS server")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-mx", action='store_true',
                       help='mx/ns flags (optional) indicate whether to send a MX (mail server) or \
                            NS (name server) query. At most one of these can be given, and if neither \
                            is given then the client should send a type A (IP address) query')
    group.add_argument("-ns", action='store_true')
    parser.add_argument(help='IPv4 address',
                        action='store', dest='server')
    parser.add_argument(help='domain name',
                        action='store', dest='name')
    return parser.parse_args()

# how to input: -t 10 -r 2 -p 10 -mx @8.8.8.8 mcgill.ca
#minimum: s @8.8.8.8 -n mcgill.ca
params = parse()
# do shit with params
client = DnsClient(params)
packet = setinput(params)
sendquery(client, packet, 1)