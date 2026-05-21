"""
config.py file defining fixed parameters such as IP addresses, MAC addresses, routing table

    Host A ----L1---- R1 ----L2---- Host B
   10.0.1.10       10.0.1.1
                   10.0.2.1       10.0.2.20
"""

NETWORK_1 = "10.0.1.0/24"
NETWORK_2 = "10.0.2.0/24"

HOST_A = {
    'ip': "10.0.1.10",
    "mac": " AA:AA:AA:AA:AA:AA"
}

ROUTER_R1 = {
    'interfaces': [("10.0.1.1", "BB:BB:BB:BB:BB:BB"), ("10.0.2.1", "CC:CC:CC:CC:CC:CC")]
}

HOST_B = {
    "ip": "10.0.2.20",
    "mac": "DD:DD:DD:DD:DD:DD"
}

