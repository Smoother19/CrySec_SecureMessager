from Frame import Frame

class MessageHandler():
    def __init__(self, header='ISC'):
        self.frame = Frame(header)
    
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

        message = message_bytes.decode('utf-32-be')

        return (header, cmd, length, message)
    
    def encrypt(self, message):
        return message
    
    def decrypt(self, message):
        return message