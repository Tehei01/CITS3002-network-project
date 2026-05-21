# python main.py 100 for a 100-byte message
import sys
from config import HOST_A, ROUTER_R1, HOST_B
from devices import Host, Router
from protocol import Frame, Packet, Segment


def create_message(size):
    """Create a message of the specified size in bytes"""
    all_ones_bytes = b'\xff' * size
    return all_ones_bytes

def setup_network():
    # Create devices
    host_a = Host(HOST_A['name'], HOST_A['ip'], HOST_A['mac'])
    router_r1 = Router(ROUTER_R1['name'], ROUTER_R1['interfaces'])
    host_b = Host(HOST_B['name'], HOST_B['ip'], HOST_B['mac'])
    


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        return 1
    message_size = int(sys.argv[1])
    print(create_message(message_size))
    return 0

if __name__ == "__main__":
    main()