import socket
import sys
from MessageHandler import MessageHandler

class ConnectionHandler:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('vlbelintrocrypto.hevs.ch', 6000))
        self.message_handler = MessageHandler()
        self.callback = None

    # def parse_server_task(self, message):
    #     if "encode the text" in message and "shift"

    def send_message(self, text, cmd='t'):
        packet = self.message_handler.encode_message(cmd, text)
        self.client.sendall(packet)

    def _recvall(self, n):
        '''Lit exactement n octets du flux réseau, ou retourne None si la connexion est fermée avant d'obtenir tous les octets.'''
        data = bytearray()
        while len(data) < n:
            try:
                packet = self.client.recv(n - len(data))
            except OSError:
                return None
                
            if not packet:
                return bytes(data) if len(data) > 0 else None
                
            data.extend(packet)
        return bytes(data)
    
    def _read_header_sync(self):
        """
        Lit le flux réseau octet par octet jusqu'à trouver le marqueur 'ISC'.
        Cela permet de réparer le flux si le serveur a envoyé des données corrompues.
        """
        marker = b'ISC'
        buffer = bytearray()
        
        while True:
            char = self.client.recv(1)
            if not char:
                return None
                
            buffer.extend(char)
            
            if buffer[-3:] == marker:
                rest = self._recvall(3)
                if not rest:
                    return None
                return marker + rest

    def set_callback(self, callback):
        self.callback = callback

    def receive_message(self):
        while True:
            try:
                header_data = self._read_header_sync()
                if not header_data:
                    print("\n[Système] Déconnecté du serveur.")
                    break

                length = int.from_bytes(header_data[4:6], 'big')
                payload_size = length * 4
                
                # Assurer que nous lisons un nombre d'octets multiple de 4 pour éviter les problèmes de décodage
                payload_data = b''
                if payload_size > 0:
                    payload_data = self._recvall(payload_size)
                    if payload_data is None: 
                        break
                    
                    safe_length = len(payload_data) - (len(payload_data) % 4)
                    payload_data = payload_data[:safe_length]

                full_packet = header_data + payload_data

                sys.stdout.write('\r\033[K') 
                
                header, cmd, length, message = self.message_handler.decode_message(full_packet)
                
                if self.callback:
                    self.callback(message)
                else:
                    print(f"[{cmd}] Serveur : {message}")
                
            except Exception as e:
                sys.stdout.write('\r\033[K') 
                print(f"\n[Erreur de réception] {e}")
                
            finally:
                sys.stdout.write('>')
                sys.stdout.flush()