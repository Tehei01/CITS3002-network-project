"""
protocol.py file containing the header definitions and classes for Layers 2, 3, and 4, 3)
"""


# Layer 2:Data Link Layer (Ethernet-like Frame)
class Frame:
    def __init__(self, dest_mac, src_mac, payload, type=0x0800):
        if len(dest_mac) != 6 or len(src_mac) != 6:
            raise ValueError("MAC must be 6 bytes")
        self.dest_mac = dest_mac  # Destination MAC address (6 bytes)
        self.src_mac = src_mac    # Source MAC address (6 bytes)
        self.type = type          # Type field (2 bytes, default to IPv4)
        self.payload = payload    # Payload (variable length)

    def receive_packet(self, packet):
        """Simulate receiving a packet and encapsulating it in a frame"""
        self.payload = packet
        


#Layer 3: Header (IP-like Packet)
class Packet:
    L3_HEADER_SIZE = 12  # Fixed header size for our simplified IP-like packet
    def __init__(self, src_ip, dst_ip, payload, ttl=100, protocol=17):
        if len(src_ip) != 4 or len(dst_ip) != 4:
            raise ValueError("IP must be 4 bytes")
        self.src_ip = src_ip      # Source IP address (4 bytes)
        self.dst_ip = dst_ip      # Destination IP address (4 bytes)
        self.ttl = ttl            # Time to Live (1 byte)
        self.protocol = protocol  # Protocol (1 byte, default to UDP)
        self.total_length = self.L3_HEADER_SIZE + len(payload)  # Total length (2 bytes, header + payload)
        self.payload = payload    # Payload (variable length)


#Layer 4: Header (UDP-like Segment with ACK support)
class Segment:
    DATA = 0
    ACK = 1
    def __init__(self, src_port, dst_port, seg_type, seq_num, data=b''):
        self.src_port = src_port  # Source port (2 bytes)
        self.dst_port = dst_port  # Destination port (2 bytes)
        self.length = 8 + len(data)   # header size + data size  (max 500) (2 bytes))
        self.checksum = 0 # 2 bytes checksum field, computed later
        self.seg_type = seg_type  # Segment type (1 byte: DATA or ACK)
        self.seq_num = seq_num    # Sequence number (1 byte) 0 or 1
        self.data = data          # Data contains the application message (empty for ACK)
        


    
    def segment_to_bytes(self):
        """convert segment fields to bytes for checksum computation"""
        b = b''
        b += self.src_port.to_bytes(2, 'big')      # 2 bytes
        b += self.dst_port.to_bytes(2, 'big')      # 2 bytes
        b += self.length.to_bytes(2, 'big')        # 2 bytes
        b += self.checksum.to_bytes(2, 'big')      # 2 bytes (zero during computation)
        b += self.seg_type.to_bytes(1, 'big')      # 1 byte
        b += self.seq_num.to_bytes(1, 'big')       # 1 byte
        # make sure data is bytes
        b += self.data                          
        return b

   
    # implemented checksum from the lecture slides 
    def compute_checksum(segment_bytes):
        # pad to even length
        if len(segment_bytes) % 2:
            segment_bytes += b'\x00'

        # sum all 16-bit words
        total = sum(int.from_bytes(segment_bytes[i:i+2], 'big')
                    for i in range(0, len(segment_bytes), 2))

        # fold carries back in (loop handles the rare case where folding produces another carry)
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)

        # 1's complement
        return ~total & 0xFFFF
    
    def verify_checksum(segment_bytes):
        if len(segment_bytes) % 2:
            segment_bytes += b'\x00'
        total = sum(int.from_bytes(segment_bytes[i:i+2], 'big')
                    for i in range(0, len(segment_bytes), 2))
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)
        return total == 0xFFFF

    
    