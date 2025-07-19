import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Performance metrics
metrics = {
    'hops': [],
    'latency': [],
    'messages_per_node': defaultdict(int),
    'routing_table_sizes': [],
}


def plot_cdf(data, title, xlabel):
    """Plot CDF for the given data."""
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf, marker='.', linestyle='none')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('CDF')
    plt.grid()
    plt.show()


def log_query_performance(start_time, hops, messages, routing_table_size):
    """Log performance metrics for a single query."""
    latency = time.time() - start_time
    metrics['hops'].append(hops)
    metrics['latency'].append(latency)
    metrics['messages_per_node'][messages['node_id']] += messages['count']
    metrics['routing_table_sizes'].append(routing_table_size)


def analyze_metrics():
    """Analyze and print performance metrics."""
    print("Performance Analysis:")
    print(
        f"Min Hops: {min(metrics['hops'])}, Max Hops: {max(metrics['hops'])}, Avg Hops: {statistics.mean(metrics['hops'])}")
    print(
        f"Min Latency: {min(metrics['latency'])}, Max Latency: {max(metrics['latency'])}, Avg Latency: {statistics.mean(metrics['latency'])}")
    print(f"Messages per Node: {dict(metrics['messages_per_node'])}")
    print(f"Routing Table Sizes: {metrics['routing_table_sizes']}")

    # Example usage
    plot_cdf(metrics['hops'], "CDF of Hops", "Hops")
    plot_cdf(metrics['latency'], "CDF of Latency", "Latency (s)")
