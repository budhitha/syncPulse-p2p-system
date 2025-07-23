import logging

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT
from connections.bootstrap_server_connection import BootstrapServerConnection
from node import Node


def main():
    # Set up logging configuration at the entry point
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Bootstrap server details
    bs_node = Node(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT + 2, name="BootstrapServer", file_list=[],
                   peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT)], bs_ip=BOOTSTRAP_IP, bs_port=BOOTSTRAP_PORT)

    while True:
        user_input = input("Enter command (e.g., 0036 REG 129.82.123.45 5001 1234abcd or exit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        try:
            # Parse the input command
            parts = user_input.split()
            if len(parts) != 5 or parts[1] != "REG":
                print("Invalid command format. Use: <length> REG <IP_address> <port_no> <username>")
                continue

            _, _, ip, port, username = parts
            port = int(port)

            # Create a node and connect to the Bootstrap Server
            my_node = Node(ip=ip, port=port, name=username, file_list=[], peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT)],
                           bs_ip=BOOTSTRAP_IP, bs_port=BOOTSTRAP_PORT)
            with BootstrapServerConnection(bs=bs_node, me=my_node) as connection:
                nodes = connection.connect_to_bs()
                print(f"Registration successful. Nodes received: {nodes}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
