"""
devices.py file implementing the Host and Router classes
"""
from protocol import Frame, Packet, Segment
from config import ETHERTYPE_IPV4, PROTOCOL_UDP, DEFAULT_TTL, MAX_SEGMENT_DATA

class Host:
    def __init__(self, name, ip, mac, routing_table, ARP_table):
        self.name = name 
        self.ip = ip  # IP address (4 bytes)
        self.mac = mac  # MAC address (6 bytes)
        self.routing_table = routing_table
        self.ARP_table = ARP_table # ARP table: {IP: MAC}
        self.links = {}  # Links to other devices: {interface_name: (connected_device, connected_interface)}

        # for unexpected ACK handling in rdt2.2
        self.sender_expected_seq = 1  # for rdt2.2 (for ACKs) filps to zero for first segment
        self.last_sent_segment = None  # for retransmission in rdt2.2
        self.last_sent_segment_ip = None  # destination IP of the last sent segment for retransmission

        self.receiver_expected_seq = 0  # for rdt2.2 (for DATA segments) 

    def send_message(self, dst_ip, message):
        # split message into segments if larger than MAX_SEGMENT_DATA
        segments = [message[i:i+MAX_SEGMENT_DATA] for i in range(0, len(message), MAX_SEGMENT_DATA)]
        for segment_data in segments:
            self.sender_expected_seq = (self.sender_expected_seq + 1) % 2
            self.l4_send_segment(segment_data, len(segment_data), dst_ip, src_port=5000, dst_port=80, seq_num=self.sender_expected_seq)
            # alternate sequence number for rdt2.2 (0 and 1)
            

    # ------------------------- layer 2 ----------------------------
    def l2_send_frame(self, packet, next_hop_ip, out_interface=None):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        next_hop_mac = self.ARP_table.get(next_hop_ip)
        if not next_hop_mac:
            print(f"{self.name}: ARP lookup failed for IP {next_hop_ip}")
            return
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {next_hop_mac}")
        frame = Frame(dest_mac=next_hop_mac, src_mac=self.mac, payload=packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={next_hop_mac}")
        print(f"{self.name}: Layer 2: Frame sent")
        peer, peer_interface = self.links[out_interface]
        print()
        peer.l2_receive_frame(frame, in_interface=peer_interface)
        
        

    
    def l2_receive_frame(self, frame, in_interface=None):
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        print()
        self.l3_receive_packet(frame.payload)
        

    # ------------------------- layer 3 ----------------------------
    def l3_send_packet(self, segment, dst_ip):
        """
        receives a segment from the transport layer, creates a packet, and sends it to the data link layer
        """
        TTL = DEFAULT_TTL
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={TTL}")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        next_hop_ip, out_interface = lookup_route(dst_ip, self.routing_table)
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        if not next_hop_ip:
            print(f"{self.name}: Layer 3: No route to destination {dst_ip} — packet dropped")
            return
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        packet = Packet(src_ip=self.ip, dst_ip=dst_ip, payload=segment, ttl=TTL, protocol=PROTOCOL_UDP)
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        print()
        self.l2_send_frame(packet, next_hop_ip, out_interface)
        

    def l3_receive_packet(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        if packet.dst_ip == self.ip:
            print(f"{self.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
            print()
            self.l4_receive_segment(packet.payload, src_ip=packet.src_ip)
        else:
            # should never trigger with this topology and routing tables but included it as an example
            print(f"{self.name}: Layer 3: Packet identified as not for this host — packet dropped")
        

    # ------------------------- layer 4 ----------------------------
    # figure out the port stuff
    def l4_send_segment(self, data, data_size, dst_ip, src_port, dst_port, seq_num):
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={data_size}")
        segment = Segment(src_port=src_port, dst_port=dst_port, seg_type=Segment.DATA, seq_num=seq_num, data=data)
        self.last_sent_segment = segment  # for potential retransmission in rdt2.2
        self.last_sent_segment_ip = dst_ip  # store destination IP for retransmission
        # checksum is automatically computed in Segment constructor
        print(f"{self.name}: Layer 4: Checksum computed")
        print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={seq_num}) (encapsulation)")
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")
        print()
        self.l3_send_packet(segment, dst_ip)
        


    def l4_receive_segment(self, segment, src_ip=None):
        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        checksum_verify = segment.verify_checksum()
        if not checksum_verify:
            print(f"{self.name}: Layer 4: Checksum verification failed — segment dropped")
            return

        print(f"{self.name}: Layer 4: Checksum verified")
        if segment.seg_type == segment.DATA:
            # stops duplicate segments from being delivered to the application layer 
            if segment.seq_num == self.receiver_expected_seq:
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                ack_seq = segment.seq_num
                self.receiver_expected_seq = 1 - self.receiver_expected_seq 
            else:
                ack_seq = 1 - self.receiver_expected_seq  # re-ACK previous
            ack_segment = Segment(
                src_port=segment.dst_port,
                dst_port=segment.src_port,
                seg_type=Segment.ACK,
                seq_num=ack_seq,
                data=b''
            )
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ack_seq})")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
            self.l3_send_packet(ack_segment, src_ip)
        elif segment.seg_type == Segment.ACK:
            if segment.seq_num == self.sender_expected_seq:
                print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
            elif segment.seq_num != self.sender_expected_seq:
                """
                if unexpected ACK is received retransmit segment
                """
                print(f"{self.name}: Layer 4: ACK received with unexpected sequence number: seq={segment.seq_num} (expected {self.sender_expected_seq})")
                print(f"{self.name}: Layer 4: Retransmitting segment with seq={self.sender_expected_seq}")
                self.l3_send_packet(self.last_sent_segment, self.last_sent_segment_ip)



class Router:
    def __init__(self, name, Interfaces, routing_table, ARP_table):
        self.name = name
        self.Interfaces = Interfaces  # List of (interface_name, IP, MAC) tuples for each interface
        self.routing_table = routing_table  # Routing table: {destination_ip: (next_hop_ip, interface_name)}
        self.ARP_table = ARP_table  # ARP table: {IP: MAC}
        self.links = {}  # Links to other devices: {interface_name: (connected_device, connected_interface)}

    # ------------------------- layer 2 ----------------------------
    def l2_send_frame(self, packet, next_hop_ip, out_interface=None):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        next_hop_mac = self.ARP_table.get(next_hop_ip)
        if not next_hop_mac:
            print(f"{self.name}: ARP lookup failed for IP {next_hop_ip}")
            return
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop_ip}) → {next_hop_mac}")
        interface_mac = self.Interfaces[out_interface][1]
        frame = Frame(dest_mac=next_hop_mac, src_mac=interface_mac, payload=packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={interface_mac}, DST_MAC={next_hop_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {out_interface}")
        print()
        peer, peer_interface = self.links[out_interface]
        peer.l2_receive_frame(frame, in_interface=peer_interface)


    
    def l2_receive_frame(self, frame, in_interface=None):
        print(f"{self.name}: Layer 2: Frame received on {in_interface}")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {in_interface}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        print()
        self.l3_forward_packet(frame.payload)

    
    # ------------------------- layer 3 ----------------------------

    def l3_forward_packet(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        packet.ttl -= 1
        print(f"{self.name}: Layer 3: TTL decremented: {packet.ttl + 1} → {packet.ttl}")
        if packet.ttl <= 0:
            print(f"{self.name}: Layer 3: TTL expired — packet dropped")
            return
        next_hop_ip, out_interface = lookup_route(packet.dst_ip, self.routing_table)
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        if not next_hop_ip:
            print(f"{self.name}: Layer 3: No route to destination {packet.dst_ip} — packet dropped")
            return
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected ({out_interface})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        print()
        self.l2_send_frame(packet, next_hop_ip, out_interface)




# ------------------------- Helper functions --------------------------------
def lookup_route(dst_ip, routing_table):
    for network_cidr, (next_hop, interface) in routing_table.items():
        network, prefix = network_cidr.split("/")
        prefix = int(prefix)
        
        if ip_in_network(dst_ip, network, prefix):
            # "direct" means destination is on this network,
            # so next-hop IP is the destination itself
            actual_next_hop = dst_ip if next_hop == "direct" else next_hop
            return actual_next_hop, interface
    
    return None  # no matching route

def ip_to_int(ip):
    parts = ip.split(".")
    return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])

def ip_in_network(ip, network, prefix):
    if prefix == 0:
        return True  # default route matches everything
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return (ip_to_int(ip) & mask) == (ip_to_int(network) & mask)