import socket
import threading
import logging
import random

from config.config import BUFFER_SIZE
from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node as SimpleNode  # Import the simple Node class for the bootstrap server


class Node:
    def __init__(self, ip, port, name, file_list, peers):
        self.ip = ip
        self.port = port
        self.name = name
        # Ensure sampling does not exceed the size of the file_list
        if not file_list:
            self.file_list = set()  # Assign an empty set if file_list is empty
        else:
            sample_size = min(len(file_list), random.randint(3, 5))
            self.file_list = set(random.sample(file_list, sample_size))
        self.peers = peers  # List of peer addresses (IP, Port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.running = False  # Flag to control the thread
        self.thread = None  # Store the thread object

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        logging.info(f"Thread started: {self.thread.is_alive()}")

    def register(self):
        # Use the simplified Node from ttypes.py for the bootstrap server
        bs_node = SimpleNode(self.bs_ip, self.bs_port, "BootstrapServer")
        with BootstrapServerConnection(bs_node, self) as conn:
            self.peers = conn.users

    def search_file(self, file_name):
        # Flood search to peers
        for peer in self.peers:
            self._send_search_message(peer, file_name)

    def _send_search_message(self, peer, file_name):
        # Send FILE_SEARCH message to a given peer
        pass  # Placeholder for networking code

    def listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                message = data.decode()
                self.handle_message(message, addr)
            except Exception as e:
                logging.error(f"Error receiving message: {e}")

    def generate_query(self, file_name):
        """
        Sends a query message to all peers to search for the specified file.
        """
        query = f"QUERY:{file_name}:{self.name}"
        for peer in self.peers:
            try:
                self.sock.sendto(query.encode(), peer)
                logging.info(f"Query sent to {peer}: {query}")
            except Exception as e:
                logging.error(f"Failed to send query to {peer}: {e}")

    def handle_message(self, message, addr):
        """
        Handles incoming messages from peers.
        """
        logging.info(f"Received message from {addr}: {message}")
        if message.startswith("QUERY:"):
            _, file_name, sender_name = message.split(":")
            if file_name in self.file_list:
                response = f"FOUND:{file_name}:{self.name}"
                try:
                    self.sock.sendto(response.encode(), addr)
                    logging.info(f"Response sent to {addr}: {response}")
                except Exception as e:
                    logging.error(f"Failed to send response to {addr}: {e}")
        else:
            logging.warning(f"Unknown message format: {message}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()  # Wait for the thread to finish
            logging.info(f"Thread stopped: {not self.thread.is_alive()}")
        self.sock.close()
