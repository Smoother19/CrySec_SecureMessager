from Frame import Frame
from sympy import randprime
import math


class MessageHandler():
    def __init__(self, header='ISC'):
        self.frame = Frame(header)
    
    def parse_server_task(self, message):
        """ Analyse le message pour voir si c'est une tâche (insensible à la casse) """
        msg_lower = message.lower()
        
        # On vérifie si c'est la phrase typique d'une tâche d'encodage
        if "encode the text" in msg_lower:
            mots = message.split() # On split le message original pour garder la casse de la clé
            
            if "shift-key" in msg_lower:
                try:
                    return ("shift", int(mots[-1]))
                except ValueError:
                    pass
            elif "vigenere key" in msg_lower:
                # Retourne 'vigenere' et le dernier mot (la clé)
                return ("vigenere", mots[-1])
                
        return None

    def encode_message(self, cmd, message):

        cmd_bytes = cmd.encode('ascii')
        length_bytes = len(message).to_bytes(2, 'big')
        message_bytes = message.encode('utf-32-be')
        
        packed = self.frame.pack(cmd_bytes, length_bytes, message_bytes)

        return packed
    
    def decode_message(self, packet):
        unpacked = self.frame.unpack(packet)

        header = unpacked[0]
        cmd = unpacked[1]
        length = unpacked[2]
        message_bytes = unpacked[3]

        message = message_bytes.decode('utf-32-be', errors='replace')

        return (header, cmd, length, message)
    
    def encrypt(self, message):
        return message
    
    def decrypt(self, message):
        return message
    
    def encode_shift(self, message, shift):
        result = ''

        for letter in message:
            new_code = (ord(letter) + shift) #% 1114112
            result += chr(new_code)

        return result
    
    def decode_shift(self, message, shift):
        result = ''

        for letter in message:
            new_code = (ord(letter) - shift) #% 1114112
            result += chr(new_code)

        return result

    def xor(self, message, key):
        result=[]

        for idx in range(len(message)):
            key_byte = key[idx%len(key)]
            result.append(message[idx]^key_byte)

        return bytes(result)

    def encode_vigenere(self, message, key):
        result = ''

        for i, char in enumerate(message):
            key_char = key[i % len(key)]
            new_code = (ord(char) + ord(key_char))
            result += chr(new_code)
        
        return result
    
    def decode_vigenere(self, message, key):
        result = ''

        for i, char in enumerate(message):
            key_char = key[i % len(key)]
            new_code = (ord(char) - ord(key_char))
            result += chr(new_code)
        
        return result
    
    def rsa_keygen(self, key_size):
        min_val = 2**(key_size // 2 - 1)
        max_val = 2**(key_size // 2)

        p = randprime()(min_val, max_val)
        q = randprime()(min_val, max_val)

        while p == q:
            q = randprime()(min_val, max_val)

        shared_key = p * q
        phi = (p - 1) * (q - 1)
        e = 65537 # Convention

        while math.gcd(e, phi) != 1:
            return self.rsa_keygen(key_size)

        private_key = pow(e, -1, phi)
        
        return (shared_key, e, private_key)

    def rsa_encrypt(self, message, n, e):
        '''Encode the message using RSA encryption with the given public key (n, e)'''

        message_int = int.from_bytes(message.encode('utf-32-be'), 'big')
        cipher_int = pow(message_int, e, n)
        byte_length = (n.bit_length() + 7) // 8
        
        return cipher_int.to_bytes(byte_length, 'big')
    
    def rsa_decrypt(self, cipher_bytes, n, d):
        '''Decode the message using RSA decryption with the given private key (n, d)'''

        cipher_int = int.from_bytes(cipher_bytes, 'big')
        message_int = pow(cipher_int, d, n)
        byte_length = (message_int.bit_length() + 7) // 8
        message_bytes = message_int.to_bytes(byte_length, 'big')

        return message_bytes.decode('utf-32-be', errors='replace')

    def parse_server_task(self, message):
        """
        Parses a message from the server to identify if it's a task.
        Returns a tuple (algorithm, key) or None.
        """
        if "encode the text" in message:
            words = message.split()
            if "shift-key" in message:
                try:
                    # The key is the last word
                    key = int(words[-1])
                    return ("shift", key)
                except (ValueError, IndexError):
                    return None
            elif "vigenere-key" in message:
                try:
                    # The key is the last word
                    key = words[-1]
                    return ("vigenere", key)
                except IndexError:
                    return None
        return None
