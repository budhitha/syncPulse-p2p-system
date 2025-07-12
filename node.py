from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node as SimpleNode  # Import the simple Node class for the bootstrap server

class Node:
    def __init__(self, bs_ip, bs_port, my_ip, my_port, name):
        self.bs_ip = bs_ip
        self.bs_port = bs_port
        self.ip = my_ip
        self.port = my_port
        self.name = name
        self.files = set()  # Files to share
        self.peers = []  # Connected peers

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