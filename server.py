import socket       # one end point to a two way communication link
import struct
import threading    # to handle multiple clients simentaneously

from sys import exit
from urllib.request import urlopen   # to open url and read source code from url


IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)  # binding ip and port as a tuple
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "DISCONNECT"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")  # whenever a new client is connected

    connected = True
    # when worker thread recieves DISCONNECT_MSG, it will terminate client connection
    while connected:
        url = conn.recv(SIZE).decode(FORMAT)    # decoding byte-stream from client

        if url == DISCONNECT_MSG:
            connected = False
            print(f"client{addr} was disconnected ")
            continue
        print(f"client{addr} sent url {url} ")

        # prepend https if not specified in url
        if url[:8] != 'https://':
            url = 'https://' + url

        with urlopen(url) as response:   #opening the url
             html_response = response.read()  # reading the source code

             # get encoding format of webpage, if none fallback to `utf-8`
             encoding = response.headers.get_content_charset('utf-8')
             # converting the httpResponse as ASCII
             decoded_html = html_response.decode(encoding)
             # encode it as utf-8 to send to client socket
             data = decoded_html.encode(FORMAT)

             # send output page size as first 4 bytes
             conn.sendall(struct.pack('>I', len(data)))
             conn.sendall(data)                    # send output page to client

             print(f"Webpage sent to client{addr}")

    conn.close()        # closing the connection


def main():
    print("[STARTING] Server is starting...")
    # SOCK_STREAM -> TCP (stream oriented protocol) ; AF_INET -> IPv4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          # create server socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # set it as re-usable
    server.bind(ADDR)                              # bind function take ip and port in a tuple
    server.listen()                                                     # listen to client
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:  #infinte loop till we stop program
        conn, addr = server.accept()   #loop wait for client to connect
        # creating a thread to handle client
        # conn acts as end-point to receive and send request
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")    # exclude main thread


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)                     #sys.exit()
