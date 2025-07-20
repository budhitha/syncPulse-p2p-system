import requests
import time

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT, FLASK_API_URL
from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node
from performance_analysis import log_query_performance, analyze_metrics

# Nodes
nodes = []


def setup_nodes():
    """Start and register nodes with the bootstrap server."""
    for i in range(5):  # Start 5 nodes
        node = Node(BOOTSTRAP_IP, BOOTSTRAP_PORT + i + 1, f"peer{i + 1}")
        connection = BootstrapServerConnection(Node(BOOTSTRAP_IP, BOOTSTRAP_PORT, "bootstrap"), node)
        connection.connect_to_bs()
        nodes.append((node, connection))


def generate_file():
    """Generate a file using the Flask API."""
    response = requests.get(f"{FLASK_API_URL}/generate")
    if response.status_code == 200:
        return response.json()
    raise RuntimeError(f"Failed to generate file. Status: {response.status_code}, Response: {response.text}")


def query_file(node, file_name):
    """Simulate a file query from a node."""
    start_time = time.time()
    # Simulate query logic here (e.g., send query to neighbors)
    hops = 3  # Example hop count
    messages = {'node_id': node.name, 'count': 5}  # Example message count
    routing_table_size = 4  # Example routing table size
    log_query_performance(start_time, hops, messages, routing_table_size)


def simulate_node_failure():
    """Simulate node failures."""
    to_remove = []  # Temporary list to store nodes to be removed
    for node, connection in nodes[:2]:  # Identify first 2 nodes to remove
        connection.unreg_from_bs()
        to_remove.append((node, connection))
    for item in to_remove:  # Remove identified nodes after iteration
        nodes.remove(item)


def main():
    """Run the integration test."""
    setup_nodes()
    print("Nodes registered with the bootstrap server.")

    file_details = generate_file()
    print(f"Generated file: {file_details}")

    for node, _ in nodes:
        query_file(node, file_details['file_name'])

    simulate_node_failure()
    print("Simulated node failures.")

    for node, _ in nodes:
        query_file(node, file_details['file_name'])

    analyze_metrics()


if __name__ == "__main__":
    main()
