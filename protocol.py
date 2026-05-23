"""
protocol.py file containing the header definitions and classes for Layers 2, 3, and 4.
"""


# Layer 2: Data Link Layer (Ethernet-like Frame)
class Frame:
    def __init__(self, dest_mac, src_mac, payload, type=0x0800):
        self.dest_mac = dest_mac  # Destination MAC address (6 bytes)
        self.src_mac = src_mac    # Source MAC address (6 bytes)
        self.type = type          # Type field (2 bytes, default to IPv4)
        self.payload = payload    # Payload contains the Layer 3 packet


# Layer 3: Header (IP-like Packet)
class Packet:
    L3_HEADER_SIZE = 12  # Source IP + destination IP + TTL + protocol + total length

    def __init__(self, src_ip, dst_ip, payload, ttl=100, protocol=17):
        self.src_ip = src_ip      # Source IP address (4 bytes)
        self.dst_ip = dst_ip      # Destination IP address (4 bytes)
        self.ttl = ttl            # Time To Live (1 byte)
        self.protocol = protocol  # Protocol field (1 byte, 17 = UDP-like payload)
        self.total_length = self.L3_HEADER_SIZE + len(payload)
        self.payload = payload    # Payload contains the Layer 4 segment


# Layer 4: Header (UDP-like Segment with ACK support)
class Segment:
    DATA = 0
    ACK = 1

    # Source port: 2 bytes
    # Destination port: 2 bytes
    # Length: 2 bytes
    # Checksum: 2 bytes
    # Type: 1 byte
    # Sequence number: 1 byte
    # Total Layer 4 header size = 10 bytes
    L4_HEADER_SIZE = 10

    def __init__(self, src_port, dst_port, seg_type, seq_num, data=b''):
        self.src_port = src_port      # Source port (2 bytes)
        self.dst_port = dst_port      # Destination port (2 bytes)
        self.length = self.L4_HEADER_SIZE + len(data)
        self.checksum = 0             # Checksum is treated as zero during calculation
        self.seg_type = seg_type      # 0 = DATA, 1 = ACK
        self.seq_num = seq_num        # Alternating bit sequence number: 0 or 1
        self.data = data              # Application data, empty for ACK segments
        self.checksum = self.compute_checksum()

    def __len__(self):
        return self.length

    def compute_checksum(self):
        """
        Compute a simple 16-bit one's-complement checksum over the segment fields.
        The checksum field itself is represented as zero during computation.
        """
        segment_bytes = self.segment_to_bytes()

        # Pad to even length so the data can be processed as 16-bit words.
        if len(segment_bytes) % 2:
            segment_bytes += b'\x00'

        total = sum(
            int.from_bytes(segment_bytes[i:i + 2], 'big')
            for i in range(0, len(segment_bytes), 2)
        )

        # Fold any carries back into 16 bits.
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)

        # Return one's complement.
        return ~total & 0xFFFF

    def verify_checksum(self):
        """
        Recompute the checksum and compare it with the stored checksum.
        """
        computed_checksum = self.compute_checksum()
        return computed_checksum == self.checksum

    def segment_to_bytes(self):
        """
        Convert segment fields to bytes for checksum computation.
        The checksum field is included as a zero placeholder.
        """
        b = b''
        b += self.src_port.to_bytes(2, 'big')       # Source port: 2 bytes
        b += self.dst_port.to_bytes(2, 'big')       # Destination port: 2 bytes
        b += self.length.to_bytes(2, 'big')         # Length: 2 bytes
        b += (0).to_bytes(2, 'big')                 # Checksum placeholder: 2 bytes
        b += self.seg_type.to_bytes(1, 'big')       # Type: 1 byte
        b += self.seq_num.to_bytes(1, 'big')        # Sequence number: 1 byte
        b += self.data                              # Data: variable length
        return b
