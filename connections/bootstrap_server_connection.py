import socket

from config.config import BUFFER_SIZE
from ttypes import Node


class BootstrapServerConnection:
    def __init__(self, bs, me):
        self.bs = bs
        self.me = me
        self.users = []
        self.maintenance_interval = 30  # Run every 30 seconds
        self.start_routing_table_maintenance()

    def __enter__(self):
        self.users = self.connect_to_bs()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unreg_from_bs()

    def message_with_length(self, message):
        """
        Helper function to prepend the length of the message to the message itself.
        """
        return f"{len(message) + 5:04d} {message}"

    def send_message(self, target_ip, target_port, message):
        """
        Sends a message to a target node.

        Args:
            target_ip (str): IP address of the target node.
            target_port (int): Port number of the target node.
            message (str): The message to send.

        Returns:
            str: Response from the target node, if any.
        """
        formatted_message = self.message_with_length(message)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_ip, target_port))
                s.send(formatted_message.encode())

                # Receive response
                response = s.recv(BUFFER_SIZE).decode()
                return response
        except Exception as e:
            return f"Error while sending message: {e}"

    def maintain_routing_table(self):
        """Remove stale nodes from the routing table."""
        while True:
            time.sleep(self.maintenance_interval)
            self.me.routing_table = [
                node for node in self.me.routing_table if self.ping_node(node)
            ]

    def ping_node(self, node):
        """Check if a node is reachable."""
        try:
            response = self.send_message(node.ip, node.port, "PING")
            return response == "PONG"
        except:
            return False

    def start_routing_table_maintenance(self):
        """Start the routing table maintenance thread."""
        maintenance_thread = threading.Thread(target=self.maintain_routing_table, daemon=True)
        maintenance_thread.start()

    def connect_to_bs(self):
        '''
        Register node at bootstrap server.
        Args:
            bs (Node): Bootstrap server node
            me (Node): This node
        Returns:
            list(Node): List of other nodes in the distributed system
        Raises:
            RuntimeError: If server sends an invalid response or if registration is unsuccessful
        '''
        message = "REG " + self.me.ip + " " + str(self.me.port) + " " + self.me.name

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.bs.ip, self.bs.port))
        s.send(self.message_with_length(message).encode())

        # Receive data from the bootstrap server
        data = s.recv(BUFFER_SIZE)
        s.close()

        # Decode the raw data
        decoded_data = data.decode()

        # Debugging received data
        print(f"DEBUG: Received raw data: {decoded_data}")

        # Extract the length prefix (first 4 digits) for validation
        length_prefix = decoded_data[:4]
        if not length_prefix.isdigit():
            raise RuntimeError("Invalid message length prefix")

        # Log length prefix for debugging purposes
        print(f"DEBUG: Length Prefix: {length_prefix}")

        # Strip the length prefix (4 digits + 1 space)
        decoded_data = decoded_data[5:].strip()

        # Tokenize the response
        toks = decoded_data.split()
        print(f"DEBUG: Tokenized response: {toks}")

        # Validate the response
        if len(toks) < 2 or toks[0] != "REGOK":  # Ensure response starts with REGOK
            raise RuntimeError("Registration failed")

        num = int(toks[1])  # Number of neighbors
        if num < 0:
            raise RuntimeError("Invalid neighbor count")

        if num == 0:
            return []
        elif num == 1:
            return [Node(toks[2], int(toks[3]), toks[4])]
        else:
            nodes = []
            for i in range(num):
                ip = toks[2 + i * 3]
                port = int(toks[3 + i * 3])
                name = toks[4 + i * 3]
                nodes.append(Node(ip, port, name))
            return nodes

    def unreg_from_bs(self):
        '''
        Unregister node at bootstrap server.
        Args:
            bs (tuple(str, int)): Bootstrap server IP address and port as a tuple.
            me (tuple(str, int)): This node's IP address and port as a tuple.
            myname (str)        : This node's name.
        Returns:
            None
        Raises:
            RuntimeError: If unregistration is unsuccessful.
        '''
        buffer_size = BUFFER_SIZE
        message = "UNREG " + self.me.ip + " " + str(self.me.port) + " " + self.me.name

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.bs.ip, self.bs.port))

        # Encode the message before sending to the server
        s.send(self.message_with_length(message).encode())

        # Receive the response from the server
        data = s.recv(buffer_size).decode()  # Decode the bytes object to string
        s.close()

        print(f"DEBUG: Received data: {data}")

        # Strip the length prefix (first 5 characters) from the response
        data_without_length = data[5:].strip()
        toks = data_without_length.split()

        print(f"DEBUG: Tokenized response: {toks}")

        if toks[0] != "UNROK":  # Check the first token after removing the length prefix
            raise RuntimeError("Unreg failed")

    def join_network(self, target_ip, target_port):
        """
        Sends a JOIN request to another node in the distributed system.

        Args:
            target_ip (str): IP address of the target node.
            target_port (int): Port number of the target node.

        Returns:
            str: Response from the target node.
        """
        message = f"JOIN {self.me.ip} {self.me.port}"
        return self.send_message(target_ip, target_port, message)

    def send_join_request(self, target_node):
        """Send a JOIN request to a target node."""
        message = f"JOIN {self.me.ip} {self.me.port}"
        return self.send_message(target_node.ip, target_node.port, message)

    def handle_join_request(self, message):
        """Handle an incoming JOIN request."""
        # Parse the JOIN message
        _, ip, port = message.split()
        # Add the new node to the routing table
        self.me.routing_table.append((ip, int(port)))
        # Send JOINOK response
        response = "JOINOK 0"
        return self.send_message(ip, int(port), response)

    def leave_network(self):
        """
        Sends a LEAVE request to the bootstrap server.

        Returns:
            str: Response from the bootstrap server.
        """
        message = f"LEAVE {self.me.ip} {self.me.port}"
        return self.send_message(self.bs.ip, self.bs.port, message)

    def send_leave_request(self, target_node):
        """Send a LEAVE request to a target node."""
        message = f"LEAVE {self.me.ip} {self.me.port}"
        return self.send_message(target_node.ip, target_node.port, message)

    def send_leave_message(self, target_node):
        """Send a LEAVE message to a target node."""
        try:
            message = f"LEAVE {self.me.ip} {self.me.port}"
            response = self.send_message(target_node.ip, target_node.port, message)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to send LEAVE message to {target_node.name}: {e}")

    def handle_leave_request(self, message):
        """Handle an incoming LEAVE request."""
        # Parse the LEAVE message
        _, ip, port = message.split()
        departing_node = (ip, int(port))

        # Update the routing table
        self.update_routing_table_on_leave(departing_node)

        # Send LEAVEOK response
        response = "LEAVEOK 0"
        return self.send_message(ip, int(port), response)

    def update_routing_table_on_leave(self, departing_node):
        """
        Update the routing table when a node leaves.

        Args:
            departing_node (tuple): A tuple (ip, port) representing the departing node.
        """
        self.me.routing_table = [
            node for node in self.me.routing_table if node != departing_node
        ]

    def search_file(self, file_name, hops=0):
        """
        Handles the SER (file search) request and performs the actual file search logic.

        Args:
            file_name (str): The name of the file to search for.
            hops (int): The current hop count for the search.

        Returns:
            str: SEROK message if the file is found, or forwards the request to neighbors.
        """
        # Check if the file exists in the local file list (partial match)
        matching_files = [f for f in self.me.file_list if file_name.lower() in f.lower()]
        if matching_files:
            # File found locally, respond with SEROK
            response = f"SEROK {len(matching_files)} {self.me.ip} {self.me.port} {hops + 1} " + " ".join(matching_files)
            return self.message_with_length(response)

        # If file not found locally, forward the SER request to neighbors
        if hops < self.me.max_hops:
            for neighbor in self.me.routing_table:
                neighbor_ip, neighbor_port = neighbor
                message = f"SER {self.me.ip} {self.me.port} \"{file_name}\" {hops + 1}"
                response = self.send_message(neighbor_ip, neighbor_port, message)
                if response and response.startswith("SEROK"):
                    # If a neighbor finds the file, return the response
                    return response

        # If no file is found and max hops are reached, return SEROK with 0 results
        response = f"SEROK 0 {self.me.ip} {self.me.port} {hops + 1}"
        return self.message_with_length(response)
