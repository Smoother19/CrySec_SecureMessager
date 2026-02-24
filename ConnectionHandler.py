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

    def _recvall(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.client.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def receive_message(self):
        while True:
            header_data = self._recvall(6)
            if not header_data:
                break
            
            length = int.from_bytes(header_data[4:6], 'big')
            
            payload_size = length * 4
            
            payload_data = b''
            if payload_size > 0:
                payload_data = self._recvall(payload_size)
                if not payload_data:
                    break
            
            full_packet = header_data + payload_data

            # Affichage classique
            sys.stdout.write('\r\033[K') 
            
            header, cmd, length, message = self.message_handler.decode_message(full_packet)
            
            print(f"[{cmd}] Serveur : {message}")
            
            sys.stdout.write('>')
            sys.stdout.flush()