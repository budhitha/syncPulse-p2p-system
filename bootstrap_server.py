import logging
import random
import socket
import threading
import time

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT
from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node as SimpleNode


class Node:
    def __init__(self, ip, port, name, file_list):
        self.ip = ip
        self.port = port
        self.name = name
        self.files = self.assign_files(file_list)

    def assign_files(self, file_list):
        """Assign 3-5 random files to the node."""
        return random.sample(file_list, k=random.randint(3, 5))


class BootstrapServer:
    def __init__(self, ip='0.0.0.0', port=5000):
        self.ip = ip
        self.port = port
        self.nodes = []  # Registered nodes

    def handle_client(self, conn, addr):
        try:
            # Receive the data from the client
            data = conn.recv(1024).decode()
            logging.info(f"Received: {data}")

            # Tokenize the message
            toks = data.split()
            response = ""

            if len(toks) < 2:
                # Invalid message format
                response = f"{len('REGOK 9999') + 5:04d} REGOK 9999"  # Default error format
            elif toks[1] == "REG":
                # Handle registration
                ip, port, name = toks[2], toks[3], toks[4]
                print(f"Registering node: {name}, IP: {ip}, Port: {port}")

                # Check if node is already registered
                exists = any(n.ip == ip and n.port == int(port) for n in self.nodes)
                if not exists:
                    file_list = self.get_files()  # Retrieve the list of files
                    self.nodes.append(Node(ip, int(port), name, file_list))

                # Create response with up to 2 neighbors
                num_nodes = min(len(self.nodes) - 1, 2)  # Exclude the new node itself
                other_nodes = [n for n in self.nodes if not (n.ip == ip and n.port == int(port))]
                response = f"REGOK {num_nodes}"
                for n in other_nodes[:2]:
                    response += f" {n.ip} {n.port} {n.name}"
                response = f"{len(response) + 5:04d} {response}"
            elif toks[1] == "UNREG":
                # Handle unregistration
                ip, port, name = toks[2], toks[3], toks[4]
                print(f"Unregistering node: {name}, IP: {ip}, Port: {port}")

                # Remove the node if it exists
                self.nodes = [n for n in self.nodes if not (n.ip == ip and n.port == int(port) and n.name == name)]

                # Send success acknowledgment
                response = f"{len('UNROK 0') + 5:04d} UNROK 0"
            elif toks[1] == "LEAVE":
                # Handle LEAVE request
                ip, port = toks[2], toks[3]
                response = self.handle_leave_request(ip, int(port))
            elif toks[1] == "JOIN":
                # Handle JOIN request using BootstrapServerConnection
                join_message = " ".join(toks)
                connection = BootstrapServerConnection(
                    bs=self,
                    me=SimpleNode(ip=self.ip, port=self.port, name="BootstrapServer")
                )
                response = connection.handle_join_request(join_message)
            elif toks[1] == "SER":
                ip, port = toks[2], toks[3]
                hops = int(toks[-1])  # Parse the last token as hops
                file_name = " ".join(toks[4:-1]).strip('"')  # Join tokens for the file name
                print(f"Search request: IP: {ip}, Port: {port}, File: {file_name}, Hops: {hops}")

                # Forward the request to neighbors
                response = self.forward_request(f"SER {ip} {port} \"{file_name}\" {hops - 1}", hops)
            elif toks[1] == "ERROR":
                # Handle ERROR message
                self.handle_error_message(" ".join(toks[2:]))
            else:
                # Invalid command
                response = f"{len('REGOK 9999') + 5:04d} REGOK 9999"

            # Send the response back to the client
            print(f"Handled command: {toks[1]}")
            conn.send(response.encode())
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            conn.close()

    def forward_request(self, message, hops):
        """Forward requests to active neighbors."""
        for neighbor in self.nodes:
            try:
                if hops > 0:
                    with socket.create_connection((neighbor.ip, neighbor.port), timeout=5) as s:
                        s.sendall(message.encode())
                        response = s.recv(1024).decode()
                        if response.startswith("SEROK"):
                            return response
            except (socket.timeout, ConnectionRefusedError):
                print(f"Neighbor {neighbor.name} at {neighbor.ip}:{neighbor.port} is unreachable.")
        return f"{len('SEROK 0') + 5:04d} SEROK 0"  # Default response if no results

    def start_heartbeat(self, interval=10):
        """Periodically check the availability of nodes."""

        def heartbeat():
            while True:
                for node in self.nodes:
                    if not self.check_node_availability(node):
                        print(f"Node {node.name} at {node.ip}:{node.port} is unreachable. Marking as failed.")
                        self.nodes.remove(node)
                time.sleep(interval)

        threading.Thread(target=heartbeat, daemon=True).start()

    def check_node_availability(self, node):
        """Check if a node is reachable."""
        try:
            with socket.create_connection((node.ip, node.port), timeout=5):
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen()
            print(f"Bootstrap server listening on {self.ip}:{self.port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def register_node(self, ip, port, name):
        new_node = {"ip": ip, "port": port, "name": name}
        self.nodes.append(new_node)
        return self.nodes[-2:]  # Send last two registered nodes

    def unregister_node(self, name):
        self.nodes = [node for node in self.nodes if node['name'] != name]

    def handle_leave_request(self, ip, port):
        """Handle LEAVE requests from nodes."""
        for node in self.nodes:
            if node.ip == ip and node.port == int(port):
                self.nodes.remove(node)
                return f"{len('LEAVEOK 0') + 5:04d} LEAVEOK 0"
        return f"{len('LEAVEOK 9999') + 5:04d} LEAVEOK 9999"

    def get_files(self):
        """
        Reads file names from the 'File Names.txt' file and returns them as a list.
        """
        try:
            with open('File Names.txt', 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("Error: 'File Names.txt' not found.")
            return []

    def handle_error_message(self, message):
        """
        Handle an incoming ERROR message.

        Args:
            message (str): The ERROR message received.

        Returns:
            None
        """
        # Log the error message
        print(f"ERROR received: {message}")


if __name__ == "__main__":
    server = BootstrapServer(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT)
    server.start_heartbeat(interval=10)  # Check every 10 seconds
    server.start()
