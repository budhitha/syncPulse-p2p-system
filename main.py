import logging

from config.config import BOOTSTRAP_IP, NODE_DEFAULT_PORT, BOOTSTRAP_PORT
from node import Node


def main():
    # Set up logging configuration at the entry point
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example setup
    node1 = Node("127.0.0.1", 5000, "Node1", ["File Names.txt"], [("127.0.0.1", 5001)])
    node2 = Node("127.0.0.1", 5001, "Node2", [], [("127.0.0.1", 5000)])

    node1.start()
    node2.start()

    # Generate a query from Node1
    node1.generate_query("Queries.txt")

    # Stop nodes after testing
    node1.stop()
    node2.stop()


if __name__ == "__main__":
    main()