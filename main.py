import logging
import time

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT
from node import Node


def main():
    # Set up logging configuration at the entry point
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example setup
    with open("File Names.txt", "r") as file:
        file_content = file.read()
    node1 = Node(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT, name="Node1", file_list=[file_content],
                 peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT + 1)])
    node2 = Node(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT + 1, name="Node2", file_list=[],
                 peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT)])

    node1.start()
    node2.start()

    # Generate a query from Node1
    test_query_file = "test_queries.txt"  # Use a test-specific filename
    node1.generate_query(file_name=test_query_file)

    # Allow time for the query to be processed
    time.sleep(2)

    # Stop nodes after testing
    node1.stop()
    node2.stop()


if __name__ == "__main__":
    main()
