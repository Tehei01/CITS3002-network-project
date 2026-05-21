"""
devices.py file implementing the Host and Router classes
"""
from protocol import Frame, Packet, Segment

class Host:
    def __init__(self, name, ip, mac, routing_table, ARP_table):
        self.name = name 
        self.ip = ip  # IP address (4 bytes)
        self.mac = mac  # MAC address (6 bytes)
        self.routing_table = routing_table
        self.ARP_table = ARP_table # ARP table: {IP: MAC}
        self.links = {}  # Links to other devices: {interface_name: (connected_device, connected_interface)}

    # ------------------------- layer 2 ----------------------------
    def l2_receive_packet_from_l3(self, packet, next_hop_ip):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        next_hop_mac = self.ARP_table.get(next_hop_ip)
        if not next_hop_mac:
            print(f"{self.name}: ARP lookup failed for IP {next_hop_ip}")
            return
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP {next_hop_ip} → {next_hop_mac}")
        frame = Frame(dest_mac=next_hop_mac, src_mac=self.mac, payload=packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={next_hop_mac}")
        print(f"{self.name}: Layer 2: Frame sent")
        

    
    def l2_receive_frame_from_l2(self, frame, in_interface=None):
        print(f"{self.name}: Layer 2: Frame received")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        # implement code to pass to the network layer for processing the packet

class Router:
    def __init__(self, name, interfaces, routing_table, ARP_table):
        self.name = name
        self.interfaces = interfaces  # List of (interface_name, IP, MAC) tuples for each interface
        self.routing_table = routing_table  # Routing table: {destination_ip: (next_hop_ip, interface_name)}
        self.ARP_table = ARP_table  # ARP table: {IP: MAC}
        self.links = {}  # Links to other devices: {interface_name: (connected_device, connected_interface)}

    # ------------------------- layer 2 ----------------------------
    def l2_receive_packet_from_l3(self, packet, next_hop_ip, out_interface=None):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        next_hop_mac = self.ARP_table.get(next_hop_ip)
        if not next_hop_mac:
            print(f"{self.name}: ARP lookup failed for IP {next_hop_ip}")
            return
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP {next_hop_ip} → {next_hop_mac}")
        frame = Frame(dest_mac=next_hop_mac, src_mac=self.mac, payload=packet)
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={next_hop_mac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {out_interface}")
        peer, peer_interface = self.links[out_interface]
        peer.l2_receive_frame_from_l2(frame, in_interface=peer_interface)

    
    def l2_receive_frame_from_l2(self, frame, in_interface=None):
        print(f"{self.name}: Layer 2: Frame received on {in_interface}")
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {in_interface}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
        # implement code to pass to the network layer for processing the packet

