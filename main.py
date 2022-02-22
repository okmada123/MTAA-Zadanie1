import sipfullproxy
import my_logging
import socket
import socketserver

def main():
    ip_addr = socket.gethostbyname(socket.gethostname())
    port = 5060

    sipfullproxy.recordroute = f"Record-Route: <sip:{ip_addr}:{port};lr>"
    sipfullproxy.topvia = f"Via: SIP/2.0/UDP {ip_addr}:{port}"

    my_logging.initial_log()
    print(f"Listening on {ip_addr}:{port}...")
    socketserver.UDPServer((ip_addr, port), sipfullproxy.UDPHandler).serve_forever()

if __name__ == "__main__":
    main()