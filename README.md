# CITS3002 Mini Internet Protocol Stack Simulator

Students:
- Mohammad Saeed (24033453)
- Tehei Cabanis (24467332)

## Overview

This project implements a simplified Internet protocol stack simulator in Python. It demonstrates how Layer 2, Layer 3 and Layer 4 work together to deliver application data from Host A to Host B through Router R1.

The simulator is a logical simulation only. It does not use real sockets or networking libraries.

## Network Topology

The simulated network contains two hosts and one router:

- Host A: 10.0.1.10, MAC AA:AA:AA:AA:AA:AA
- Router R1 Interface 1: 10.0.1.1, MAC BB:BB:BB:BB:BB:BB
- Router R1 Interface 2: 10.0.2.1, MAC CC:CC:CC:CC:CC:CC
- Host B: 10.0.2.20, MAC DD:DD:DD:DD:DD:DD

The two networks are:

- Network 1: 10.0.1.0/24
- Network 2: 10.0.2.0/24

## Files

- `main.py`: Entry point. Accepts the application message size as a command-line argument.
- `config.py`: Defines IP addresses, MAC addresses, routing tables, ARP tables and constants.
- `protocol.py`: Defines Layer 2 `Frame`, Layer 3 `Packet`, and Layer 4 `Segment` classes.
- `devices.py`: Implements the `Host` and `Router` classes.
- `test/test_main.py`: Runs an exact-match test for the 10-byte example output.
- `test/expected_10_bytes.txt`: Expected output for the 10-byte test case.

## How to Run

Run the simulator using:

    python main.py <message_size>

Examples:

    python main.py 10
    python main.py 500
    python main.py 501
    python main.py 1000

## Testing

Run the provided test with:

    python test/test_main.py

Recommended manual tests:

    python main.py 10
    python main.py 500
    python main.py 501
    python main.py 1000

The 501-byte test confirms that the message is split into a 500-byte segment and a 1-byte segment. Sequence numbers alternate between 0 and 1, and each DATA segment receives an ACK.

## Implemented Features

### Layer 2

- Creates Ethernet-like frames.
- Uses source and destination MAC addresses.
- Performs next-hop IP to MAC lookup using ARP tables.
- Delivers Layer 3 packets to the Network Layer.
- Logs frame creation, sending, receiving and MAC learning.

### Layer 3

- Creates IP-like packets.
- Uses source and destination IP addresses.
- Performs routing table lookups.
- Forwards packets through Router R1.
- Decrements TTL at the router.
- Drops packets if TTL expires.
- Delivers Layer 4 segments to the Transport Layer at the destination host.

### Layer 4

- Creates UDP-like DATA and ACK segments.
- Uses source and destination ports.
- Computes segment length using the full 10-byte Layer 4 header.
- Computes and verifies checksums.
- Splits messages larger than 500 bytes into multiple segments.
- Uses alternating sequence numbers 0 and 1.
- Sends ACKs with the same sequence number as the received DATA segment.

## Limitations

This is a deterministic logical simulation. It does not use real packet transmission, sockets, or external networking libraries. Packet loss and frame corruption are not randomly simulated because the assignment assumes deterministic transmission with no packet loss or frame corruption.
