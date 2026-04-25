import hashlib

from Frame import Frame
from sympy import randprime
import math
    


class MessageHandler():
    def __init__(self, header='ISC'):
        self.frame = Frame(header)

    def encode_message(self, cmd, message):
        cmd_bytes = cmd.encode('ascii')
        
        if isinstance(message, list):
            length_bytes = len(message).to_bytes(2, 'big')
            
            byte_array = bytearray()
            for c in message:
                byte_array.extend(c.to_bytes(4, byteorder="big"))
                
            message_bytes = bytes(byte_array)
            
        elif isinstance(message, bytes):
            length_bytes = len(message).to_bytes(2, 'big')
            message_bytes = message

        else:
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

        self._last_raw_bytes = message_bytes

        message = message_bytes.decode('utf-32-be', errors='replace')

        return (header, cmd, length, message)

    
    def encode_shift(self, message, shift):
        result = ''

        for letter in message:
            new_code = (ord(letter) + shift)
            result += chr(new_code)

        return result
    
    def decode_shift(self, message, shift):
        result = ''

        for letter in message:
            new_code = (ord(letter) - shift)
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
        if key_size <= 4:
            raise ValueError("Key size must be greater than 4 bits.")

        half_key_size = key_size // 2
        min_val = 2 ** (half_key_size - 2)
        max_val = 2 ** half_key_size

        p = randprime(min_val, max_val)
        q = randprime(min_val, max_val)

        while p == q:
            q = randprime(min_val, max_val)

        n = p * q
        phi = (p - 1) * (q - 1)
        e = randprime(3, phi)

        while e <= 1 or e >= phi or math.gcd(e, phi) != 1:
            e = randprime(3, phi)

        d = pow(e, -1, phi)

        return (n, e, d)

    def rsa_encrypt(self, message, n, e):
        '''Encode the message using RSA encryption with the given public key (n, e)'''
        result = []
        
        use_raw = hasattr(self, '_last_raw_bytes') and len(self._last_raw_bytes) == len(message) * 4

        for i in range(len(message)):
            if use_raw:
                chunk = self._last_raw_bytes[i*4 : i*4+4]
                val = int.from_bytes(chunk, byteorder='big')
            else:
                val = ord(message[i])
                
            c = pow(val, e, n)
            result.append(c)
            
        return result
    
    def rsa_decrypt(self, cipher_data, n, d):
        '''Décode le message RSA depuis une liste de nombres ou des bytes'''
        result = ""
        
        # CAS 1 : Chaîne de nombres décimaux (ex: "141 15 205...")
        if isinstance(cipher_data, str):
            # On sépare par les espaces et on ignore les morceaux vides
            numbers = [n for n in cipher_data.split() if n.strip()]
            for num_str in numbers:
                try:
                    c = int(num_str)
                    # Calcul RSA : m = c^d mod n
                    m = pow(c, d, n)
                    result += chr(m)
                except ValueError:
                    continue
                    
        # CAS 2 : Bytes bruts (pour la compatibilité)
        elif isinstance(cipher_data, bytes):
            bytes_per_char = (n.bit_length() + 7) // 8
            for i in range(0, len(cipher_data), bytes_per_char):
                c = int.from_bytes(cipher_data[i : i + bytes_per_char], byteorder="big")
                result += chr(pow(c, d, n))

        return result
    
    def diffie_hellman_keygen(self):
        import secrets
        from sympy import primitive_root
        
        p = randprime(1000, 5000)
        g = primitive_root(p)
        a = secrets.randbelow(p - 2) + 2

        A = pow(g, a, p)

        return p, g, a, A
    
    def diffie_hellman_shared_key(self, B, a, p):
        secret = pow(B, a, p)
        return secret

    def parse_server_task(self, message):
        """
        Parses a message from the server to identify if it's a task.
        Returns a tuple (algorithm, key) or None.
        """
        if "encode the text" in message:
            words = message.split()
            if "shift-key" in message:
                try:
                    key = int(words[-1])
                    return ("shift", key)
                except (ValueError, IndexError):
                    return None
            elif "vigenere-key" in message:
                try:
                    key = words[-1]
                    return ("vigenere", key)
                except IndexError:
                    return None
        return None
    
    def sha256_hash(self, message):
        cleaned_message = ""
        for char in message:
            val = ord(char)
            if val > 255:
                try:
                    byte_len = (val.bit_length() + 7) // 8
                    raw_utf8 = val.to_bytes(byte_len, byteorder='little')
                    cleaned_message += raw_utf8.decode('utf-8')
                except Exception:
                    cleaned_message += char
            else:
                cleaned_message += char

        return hashlib.sha256(cleaned_message.encode('utf-8')).hexdigest()