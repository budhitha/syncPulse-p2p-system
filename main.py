import logging

from config.config import BOOTSTRAP_IP, NODE_DEFAULT_PORT, BOOTSTRAP_PORT
from node import Node


def main():
    # Application configuration
    my_ip = BOOTSTRAP_IP
    my_port = NODE_DEFAULT_PORT
    my_name = "peer2"
    bootstrap_ip = BOOTSTRAP_IP
    bootstrap_port = BOOTSTRAP_PORT

    # Create Node and connect to the bootstrap server
    node_instance = Node(bootstrap_ip, bootstrap_port, my_ip, my_port, my_name)
    node_instance.register()  # Register with the bootstrap server

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == "__main__":
    main()