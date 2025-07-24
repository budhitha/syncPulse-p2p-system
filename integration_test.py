import random
import requests
import time
import statistics

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT, FLASK_API_URL
from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node
from performance_analysis import log_query_performance

# Nodes
nodes = []

# Performance Metrics
class PerformanceMetrics:
    def __init__(self):
        self.hops = []
        self.latencies = []
        self.messages_per_node = []
        self.node_degrees = []

    def record_hop(self, hop_count):
        self.hops.append(hop_count)

    def record_latency(self, latency):
        self.latencies.append(latency)

    def record_messages_per_node(self, message_count):
        self.messages_per_node.append(message_count)

    def record_node_degree(self, degree):
        self.node_degrees.append(degree)

    def calculate_metrics(self, data):
        if not data:
            return {"min": None, "max": None, "average": None, "std_dev": None}
        return {
            "min": min(data),
            "max": max(data),
            "average": sum(data) / len(data),
            "std_dev": statistics.stdev(data) if len(data) > 1 else 0
        }

    def get_performance_summary(self):
        return {
            "hops": self.calculate_metrics(self.hops),
            "latencies": self.calculate_metrics(self.latencies),
            "messages_per_node": self.calculate_metrics(self.messages_per_node),
            "node_degrees": self.calculate_metrics(self.node_degrees)
        }

performance_metrics = PerformanceMetrics()

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

def simulate_hops(node):
    """Simulate the number of hops for a query from the given node."""
    return random.randint(1, 5)

def simulate_messages(node):
    """Simulate the number of messages for a query from the given node."""
    return {
        'node_id': node.name,  # Use the node's name as its ID
        'count': random.randint(10, 50)  # Simulate the message count dynamically
    }

def get_routing_table_size(node):
    """Return the size of the node's routing table."""
    return len(node.routing_table)

def query_file(node, file_name):
    """Simulate a file query from a node."""
    start_time = time.time()
    hops = simulate_hops(node)
    messages = simulate_messages(node)
    routing_table_size = get_routing_table_size(node)
    latency = time.time() - start_time

    # Log performance metrics
    performance_metrics.record_hop(hops)
    performance_metrics.record_latency(latency)
    performance_metrics.record_messages_per_node(messages['count'])
    performance_metrics.record_node_degree(routing_table_size)

    log_query_performance(start_time, hops, messages, routing_table_size)

def simulate_node_failure():
    """Simulate node failures with graceful departure."""
    for neighbor in node.routing_table:
        try:
            connection.send_leave_message(neighbor)
            neighbor_connection = BootstrapServerConnection(self.me, neighbor)
            neighbor_connection.update_routing_table_on_leave(node)
        except Exception as e:
            print(f"Failed to update routing table for {neighbor}: {e}")

        # Unregister the node from the bootstrap server
        connection.unreg_from_bs()
        nodes.remove((node, connection))

def analyze_metrics():
    """Analyze and print performance metrics."""
    summary = performance_metrics.get_performance_summary()
    print("Performance Metrics Summary:")
    print(summary)

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