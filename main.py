# python main.py 100 for a 100-byte message
import sys


if __name__ == "__main__":



    # Get the message size from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        sys.exit(1)

    message_size = int(sys.argv[1])
    print(message_size)