import socket

from config.config import BUFFER_SIZE
from ttypes import Node
from random import shuffle


class BootstrapServerConnection:
    def __init__(self, bs, me):
        self.bs = bs
        self.me = me
        self.users = []

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
        formatted_message = self.message_with_length(message)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_ip, target_port))
                s.send(formatted_message.encode())

                # Receive response
                response = s.recv(1024).decode()
                return response
        except Exception as e:
            return f"Error while sending JOIN request: {e}"

    def leave_network(self):
        """
        Sends a LEAVE request to the bootstrap server.

        Returns:
            str: Response from the bootstrap server.
        """
        message = f"LEAVE {self.me.ip} {self.me.port}"
        formatted_message = self.message_with_length(message)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.bs.ip, self.bs.port))
                s.send(formatted_message.encode())

                # Receive response
                response = s.recv(1024).decode()
                return response
        except Exception as e:
            return f"Error while sending LEAVE request: {e}"

    def search_file(self, file_name, hops=0):
        """
        Sends a SER request to search for a file in the network.

        Args:
            file_name (str): The name of the file to search for.
            hops (int): The hop count for the search.

        Returns:
            str: Response from the network.
        """
        message = f"SER {self.me.ip} {self.me.port} \"{file_name}\" {hops}"
        formatted_message = self.message_with_length(message)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.bs.ip, self.bs.port))
                s.send(formatted_message.encode())

                # Receive response
                response = s.recv(1024).decode()
                return response
        except Exception as e:
            return f"Error while sending SER request: {e}"
