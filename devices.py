"""
devices.py file implementing the Host and Router classes
"""

class Host:
    def __init__(self, name, ip, mac):
        self.name = name 
        self.ip = ip  # IP address (4 bytes)
        self.mac = mac  # MAC address (6 bytes)
    
class Router:
    def __init__(self, name, interfaces):
        self.name = name
        self.interfaces = interfaces  # List of (IP, MAC) tuples for each interface
        self.routing_table = {}  # Routing table: {destination_ip: (next_hop_ip, interface_index)}