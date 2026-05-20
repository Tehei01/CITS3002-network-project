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
        self.seg_type = seg_type  # Segment type (1 byte: DATA or ACK)
        self.seq_num = seq_num    # Sequence number (4 bytes)
        self.data = data          # Data (variable length)