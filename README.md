# Mini Internet Protocol Stack Simulator

A Python simulator of a simplified network stack (Layer 2 / Layer 3 / Layer 4) that transmits a message from Host A to Host B through Router R1.

## Topology

```
Host A ----L1---- R1 ----L2---- Host B
10.0.1.10            10.0.2.1
            10.0.1.1             10.0.2.20
```

## Requirements

- Python 3 (standard library only — no external packages)

## Usage

```
python main.py <message_size>
```

`<message_size>` is a non-negative integer specifying the number of bytes to send from Host A to Host B. Messages longer than 500 bytes are split into multiple segments under the rdt2.2 alternating-bit protocol.

**Examples**

```bash
python main.py 10      
python main.py 500      
python main.py 501    
python main.py 1010    
```
- 10 byte message -> 1 segment
- 500 byte message -> 1 segment
- 501 byte message -> 2 segments
- 1010 byte message -> 3 segments 

## File Structure

- `main.py` — entry point; parses the message size, builds the topology, and starts the transfer.
- `config.py` — IP/MAC addresses, routing tables, ARP tables, and constants.
- `protocol.py` — header classes for Layer 2 (`Frame`), Layer 3 (`Packet`), and Layer 4 (`Segment`).
- `devices.py` — `Host` and `Router` classes implementing each layer's send/receive logic.
- `README.md` — this file.

## Output

Each layer prints log messages describing its actions (frame creation, MAC learning, routing decisions, TTL handling, checksum verification, ACK exchange). Logs are written to standard output and can be redirected to a file:
