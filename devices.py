"""
devices.py file implementing the Host and Router classes
"""

class Host:
    def __init__(self, name, ip, mac, routing_table, ARP_table):
        self.name = name 
        self.ip = ip  # IP address (4 bytes)
        self.mac = mac  # MAC address (6 bytes)
        self.routing_table = routing_table
        self.arp_table = ARP_table # ARP table: {IP: MAC}

class Router:
    def __init__(self, name, interfaces, routing_table, ARP_table):
        self.name = name
        self.interfaces = interfaces  # List of (interface_name, IP, MAC) tuples for each interface
        self.routing_table = routing_table  # Routing table: {destination_ip: (next_hop_ip, interface_name)}
        self.arp_table = ARP_table  # ARP table: {IP: MAC}