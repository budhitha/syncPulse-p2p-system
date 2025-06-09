from bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node


def main():
    # Configuration (you could use argparse to make these command-line options)
    my_ip = "127.0.0.1"
    my_port = 5002
    my_name = "peer2"

    bootstrap_ip = "127.0.0.1"
    bootstrap_port = 5000
    bootstrap_name = "bootstrap"

    # Create Node objects
    me = Node(my_ip, my_port, my_name)
    bootstrap = Node(bootstrap_ip, bootstrap_port, bootstrap_name)

    # Connect to bootstrap server
    bsc = BootstrapServerConnection(bootstrap, me)
    try:
        neighbors = bsc.connect_to_bs()
        print("Successfully registered. Neighbor nodes:")
        for n in neighbors:
            print(f"- {n.ip}:{n.port} ({n.name})")
    except Exception as e:
        print("Failed to register with bootstrap server:", e)


if __name__ == "__main__":
    main()