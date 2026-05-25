# python main.py 100 for a 100-byte message
import sys
from config import HOST_A, ROUTER_R1, HOST_B
from devices import Host, Router
from protocol import Frame, Packet, Segment

sys.stdout.reconfigure(encoding="utf-8")


def create_message(size):
    """Create a message of the specified size in bytes"""
    all_ones_bytes = b'\xff' * size
    return all_ones_bytes

def setup_network():
    # Create devices
    host_A = Host(HOST_A['name'], HOST_A['ip'], HOST_A['mac'], HOST_A['routing_table'], HOST_A['ARP_table'])
    router_R1 = Router(ROUTER_R1['name'], ROUTER_R1['Interfaces'], ROUTER_R1['routing_table'], ROUTER_R1['ARP_table'])
    host_B = Host(HOST_B['name'], HOST_B['ip'], HOST_B['mac'], HOST_B['routing_table'], HOST_B['ARP_table'])

    host_A.links = {"eth0": (router_R1, "Interface 1")}
    router_R1.links = {
        "Interface 1": (host_A, "eth0"),
        "Interface 2": (host_B, "eth0"),
    }
    host_B.links = {"eth0": (router_R1, "Interface 2")}
    return host_A, router_R1, host_B



def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        return 1
    try:
        message_size = int(sys.argv[1])
        if message_size < 0:
            print("Error: Message size must be a non-negative integer.")
            return 1
    except ValueError:
        print("Error: Message size must be an integer.")
        return 1
    message = create_message(message_size)
    host_A, router_R1, host_B = setup_network()
    host_A.l4_send_message(HOST_B['ip'], message)
    return 0

if __name__ == "__main__":
    main()