import socket
import threading
import json
from DnsRequest import forwardDnsRequest
from redisWrapper import RedisSingleton as r
from DnsParser import parse_dns_packet

# DNS server settings

# Cache to store DNS responses
dns_cache = {}
redis_service = r.get_instance()

# Load the JSON data into a dictionary
with open('config.json') as f:
    config = json.load(f)

DNS_SERVERS = config['external-dns-servers']
CACHE_TTL = config['cache-expiration-time']


def request_to_dns_servers(data):
    for dns_server in DNS_SERVERS:
        try:
            response = forwardDnsRequest(data, dns_server)
            answer_count = int.from_bytes(response[6:8], 'big')
            if answer_count == 0:
                print(f"Domain not found in {dns_server}")
                raise Exception
            print(f"Got response for {data} - {response} in {dns_server}")
            return response
        except Exception:
            continue
    print("\nDomain is NOT available in dns servers !\n")
    return response


def handle_client_request(data, client_address, dns_proxy_socket):
    try:
        # Check if the DNS response exists in the cache
        if redis_service.exists(data[12:]):
            response = redis_service.get(data[12:])
            print(f"Using cache for {data} - {response}")
        else:
            # Send DNS request to the DNS servers
            response = request_to_dns_servers(data)
            if (response is None):
                print('Domain not found in DNS servers')
            redis_service.set(data[12:], response, ex=CACHE_TTL)
            # Save the DNS response in the cache

        # Send the DNS response back to the client
        parse_dns_packet((data[:2] + response[2:]))
        dns_proxy_socket.sendto((data[:2] + response[2:]), client_address)
    except Exception as e:
        print(f"Error handling request from {client_address}: {str(e)}")


def start_dns_proxy():
    dns_proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Listen for DNS requests
    PORT = 5005
    dns_proxy_socket.bind(('0.0.0.0', PORT))
    print(f"DNS proxy started. Listening on port {PORT}.")

    while True:
        print('--------------------------------------')
        data, client_address = dns_proxy_socket.recvfrom(4096)
        client_thread = threading.Thread(
            target=handle_client_request, args=(
                data, client_address, dns_proxy_socket)
        )
        client_thread.start()
        print('--------------------------------------')


start_dns_proxy()
