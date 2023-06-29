import socket
import threading
from DnsRequest import forwardDnsRequest
from redisWrapper import RedisSingleton as r

# DNS server settings
DNS_SERVERS = ['8.8.8.8']  # Example DNS servers (Google DNS)

# Cache to store DNS responses
dns_cache = {}


def handle_client_request(data, client_address, dns_proxy_socket):
    try:
        # Check if the DNS response exists in the cache
        if r.get_instance().exists(data[12:]):
            response = r.get_instance().get(data[12:])
            print(f"Using cache for {data} - {response}")
        else:
            # Send DNS request to the DNS servers
            response = forwardDnsRequest(data, DNS_SERVERS[0])
            # Save the DNS response in the cache
            r.get_instance().set(data[12:], response, ex=10)
            print(f"Got response for {data} - {response}")

        # Send the DNS response back to the client
        dns_proxy_socket.sendto((data[:2] + response[2:]), client_address)
    except Exception as e:
        print(f"Error handling request from {client_address}: {str(e)}")


def start_dns_proxy():
    dns_proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Listen for DNS requests
    PORT = 54
    dns_proxy_socket.bind(('0.0.0.0', PORT))
    print(f"DNS proxy started. Listening on port {PORT}.")

    while True:
        data, client_address = dns_proxy_socket.recvfrom(4096)
        client_thread = threading.Thread(
            target=handle_client_request, args=(
                data, client_address, dns_proxy_socket)
        )
        client_thread.start()


start_dns_proxy()

