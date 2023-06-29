import socket


def forwardDnsRequest(data, dest):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (dest, 53))
        response, _ = client_socket.recvfrom(4096)
        return response
    except Exception as e:
        print(f"Error forwarding {data} to {dest} : {str(e)}")
    finally:
        client_socket.close()
