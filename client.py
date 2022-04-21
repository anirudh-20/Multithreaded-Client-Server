import socket
import struct
from os.path import exists as file_exists

IP = socket.gethostbyname( socket.gethostname() )
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "DISCONNECT"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)        # connect client to the server
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    connected = True

    while connected:
        msg = input("Enter the URL you want to search or \
                type DISCONNECT to stop the connection\n")
        client.send(msg.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
            # End sending/receving of bytes to/from client socket
            client.shutdown(socket.SHUT_RDWR)
            client.close()                          # close socket
        else:
            filename = getFileName()
            html_response = b''
            # receive webpage data length as first 4 bytes
            data_size = struct.unpack('>I', client.recv(4))[0]
            print("[SERVER] sending webpage...")
            # repeatedly get buffer sized data until no remaining webpage data
            rem_size = data_size
            while rem_size:
                html_response += client.recv(SIZE)      # SIZE -> size of buffer
                rem_size = data_size - len(html_response)

            print("[SERVER] Webpage sent completely")
            decoded_html = html_response.decode(FORMAT)
            with open(filename, 'w') as f:  # opening and write the webpage
                f.write(decoded_html)

            print(f"Saved WebPage contents to {filename}.html\n")

def getFileName():
    name = input("Enter the name of file of webpage you want to save\n")
    filename = name + '.html'

    while file_exists(filename):
        print("There already exists a file with the same name.")
        answer = input("Do you want to rewrite it? [Y/n] \n")
        if answer.lower() == 'n':
            filename = name + '_copy'
        filename = filename + '.html'

    return filename


if __name__ == "__main__":
    main()
