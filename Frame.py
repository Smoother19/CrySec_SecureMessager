class Frame():
    def __init__(self, header, cmd='t', payload=''):
        self.header = header
        self.cmd = cmd
        self.payload = payload
        self.length = len(payload)

    def pack(self, cmd, length, message):
        header_bytes = self.header.encode('ascii')
        return header_bytes + cmd + length + message

    def unpack(self, packet):
        header = packet[0:3].decode('ascii')
        cmd = packet[3:4].decode('ascii')
        size_bytes = packet[4:6]
        length = int.from_bytes(size_bytes, 'big')
        payload = packet[6:6+length*4]
        
        return (header, cmd, length, payload)

    def __str__(self):
        return f"Frame(header={self.header}, cmd={self.cmd}, length={self.length},payload={self.payload})"