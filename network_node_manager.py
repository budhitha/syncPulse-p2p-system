import logging
import random
import socket


# Define the Node class
class Node:
    def __init__(self, name, ip, port, file_list=None):
        self.name = name
        self.ip = ip
        self.port = port
        self.file_list = file_list or []
        self.neighbors = []

    def add_neighbors(self, neighbors):
        self.neighbors.extend(neighbors)

    def __str__(self):
        return (f"Node(name={self.name}, ip={self.ip}, port={self.port}, files={self.file_list}, "
                f"neighbors={[n.name for n in self.neighbors]})")

    def format_message(self, command):
        """
        Prepends length to the command (4-digit format).
        """
        return f"{len(command) + 4:04d} {command}"

    def register(self):
        """
        Register this node with the Bootstrap Server.
        """
        message = f"REG {self.ip} {self.port} {self.username}"
        full_message = self.format_message(message)

        # Send registration message to BS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(full_message.encode(), self.bs_address)

            # Wait for the response
            data, _ = s.recvfrom(1024)
            response = data.decode()

            print(f"Received from BS: {response}")
            self.handle_register_response(response)

    def handle_register_response(self, response):
        """
        Handle the response from the Bootstrap Server.
        """
        toks = response.split()

        if len(toks) < 2:  # Ensure at least 2 tokens are present
            logging.info(f"Registration failed with response: {response}")
            return

        if toks[0] == "REGFAILED":
            logging.info(f"Registration failed with response: {response}")
            return

        if toks[0] == "REGOK":  # Correct registration response
            num_nodes = int(toks[1])  # Number of neighbors
            if num_nodes > 0:
                # Parse and add neighbors
                for i in range(num_nodes):
                    try:
                        neighbor_ip = toks[2 + i * 2]
                        neighbor_port = int(toks[3 + i * 2])
                        self.neighbors.append((neighbor_ip, neighbor_port))
                    except IndexError:
                        logging.error(f"Malformed neighbor data in response: {response}")
                logging.info(f"New neighbors: {self.neighbors}")
            else:
                logging.info("No other nodes in the network.")
        else:
            logging.error(f"Unexpected registration response: {response}")



    def unregister(self):
        """
        Unregister this node from the Bootstrap Server.
        """
        message = f"UNREG {self.ip} {self.port} {self.username}"
        full_message = self.format_message(message)

        # Send unregistration message to BS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(full_message.encode(), self.bs_address)

            # Wait for the response
            data, _ = s.recvfrom(1024)
            response = data.decode()

            print(f"Received from BS: {response}")
            self.handle_unregister_response(response)

    def handle_unregister_response(self, response):
        """
        Handle the unregister response from the Bootstrap Server.
        """
        toks = response.split()
        if toks[1] == "UNROK":
            if toks[2] == "0":
                print("Successfully unregistered from the Bootstrap Server.")
            else:
                print("Unregistration failed with response:", response)

    def join_network(self):
        """
        Send JOIN requests to neighbors.
        """
        message = f"JOIN {self.ip} {self.port}"
        full_message = self.format_message(message)

        for neighbor in self.neighbors:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(full_message.encode(), neighbor)

                # Wait for the response
                data, _ = s.recvfrom(1024)
                response = data.decode()
                self.handle_join_response(response)

    def handle_join_response(self, response):
        """
        Handle the join response from neighbors.
        """
        toks = response.split()
        if toks[1] == "JOINOK":
            if toks[2] == "0":
                print("Successfully joined neighbor.")
            else:
                print(f"Join failed with response: {response}")

    def leave_network(self):
        """
        Send LEAVE requests to all neighbors.
        """
        message = f"LEAVE {self.ip} {self.port}"
        full_message = self.format_message(message)

        for neighbor in self.neighbors:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(full_message.encode(), neighbor)

                # Wait for the response
                data, _ = s.recvfrom(1024)
                response = data.decode()
                self.handle_leave_response(response)

    def handle_leave_response(self, response):
        """
        Handle leave response from neighbors.
        """
        toks = response.split()
        if toks[1] == "LEAVEOK":
            if toks[2] == "0":
                print("Successfully notified neighbor about leaving.")
            else:
                print(f"Leave notification failed with response: {response}")


# File pool
file_pool = [f"file{i}" for i in range(1, 21)]


# Assign random files to a node
def assign_files():
    return random.sample(file_pool, random.randint(3, 5))


# Define the Network
class Network:
    def __init__(self, bs_ip, bs_port):
        self.bootstrap_server = (bs_ip, bs_port)
        self.nodes = []  # Stores all the nodes in the system

    def register_node(self, new_node):
        """
        Register a node and establish 2 connections.
        """
        self.nodes.append(new_node)
        if len(self.nodes) == 1:
            # First node, no neighbors
            print(f"Bootstrap Server acknowledged registration of {new_node.name}")
        else:
            # Choose 2 random neighbors
            neighbors = random.sample(self.nodes[:-1], min(2, len(self.nodes) - 1))
            new_node.add_neighbors(neighbors)

        # Log the network topology
        print(f"Node {new_node.name} connected to {[n.name for n in new_node.neighbors]}")

    def display_nodes(self):
        """
        Display network topology and node contents.
        """
        for node in self.nodes:
            print(node)


# Main program
if __name__ == "__main__":
    # Initialize the bootstrap server and network
    bs_ip = "127.0.0.1"
    bs_port = 5000
    network = Network(bs_ip, bs_port)

    # Create 10+ nodes
    for i in range(1, 11):  # Example: 10 nodes
        # Create a new node
        node_name = f"Node{i}"
        node_ip = f"192.168.0.{i}"
        node_port = 1000 + i
        node_files = assign_files()
        new_node = Node(name=node_name, ip=node_ip, port=node_port, file_list=node_files)

        # Register node in the network
        network.register_node(new_node)

    # Display entire network
    print("\nFinal Network Topology:")
    network.display_nodes()
