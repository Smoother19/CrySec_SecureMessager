import socket
import sys
from MessageHandler import MessageHandler

class ConnectionHandler:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('vlbelintrocrypto.hevs.ch', 6000))
        self.message_handler = MessageHandler()

    def send_message(self, text, cmd='t'):
        packet = self.message_handler.encode_message(cmd, text)
        self.client.sendall(packet)

    def receive_message(self):
        while True:
            data = self.client.recv(1024)
            if not data:
                break

            # Return to the beginning of the line and clear the current text
            sys.stdout.write('\r\033[K') 
            
            header, cmd, length, message = self.message_handler.decode_message(data)
            
            print(f"[{cmd}] Serveur : {message}")
            
            sys.stdout.write('>')
            sys.stdout.flush()