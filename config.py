"""
config.py file defining fixed parameters such as IP addresses, MAC addresses, routing table

    Host A ----L1---- R1 ----L2---- Host B
   10.0.1.10       10.0.1.1
                   10.0.2.1       10.0.2.20
"""

NETWORK_1 = "10.0.1.0/24"
NETWORK_2 = "10.0.2.0/24"

ETHERTYPE_IPV4 = 0x0800
PROTOCOL_UDP = 17
DEFAULT_TTL = 100
MAX_SEGMENT_DATA = 500 

HOST_A = {
    "name": "Host A",
    "ip": "10.0.1.10",
    "mac": "AA:AA:AA:AA:AA:AA",
    "routing_table": {"10.0.2.0/24": ("10.0.1.1", "eth0"), "10.0.1.0/24": ("direct", "eth0")},
    "ARP_table" : {"10.0.1.1": "BB:BB:BB:BB:BB:BB"} # R1 Interface 1

}

ROUTER_R1 = {
    "name": "R1",
    'interfaces': [("interface 1", "10.0.1.1", "BB:BB:BB:BB:BB:BB"), ("interface 2", "10.0.2.1", "CC:CC:CC:CC:CC:CC")],
    "routing_table": {"10.0.1.0/24": ("direct", "interface 1"), "10.0.2.0/24": ("direct", "interface 2")},
    "ARP_table": {
        "10.0.1.10": "AA:AA:AA:AA:AA:AA",  # Host A
        "10.0.2.20": "DD:DD:DD:DD:DD:DD",  # Host B
    }
}

HOST_B = {
    "name": "Host B",
    "ip": "10.0.2.20",
    "mac": "DD:DD:DD:DD:DD:DD",
    "routing_table": {"10.0.1.0/24": ("10.0.2.1", "eth0"), "10.0.2.0/24": ("direct", "eth0")},
   "ARP_table" :{
    "10.0.2.1": "CC:CC:CC:CC:CC:CC"} # R1 interface 
}

