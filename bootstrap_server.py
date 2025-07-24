import logging
import socket
import threading

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT


class Node:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name


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
                    self.nodes.append(Node(ip, int(port), name))

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
            elif toks[1] == "JOIN":
                # Handle JOIN request
                source_ip, source_port = toks[2], toks[3]
                print(f"Node joining network: IP: {source_ip}, Port: {source_port}")

                # Acknowledge the JOIN request
                response = f"{len('JOINOK 0') + 5:04d} JOINOK 0"
            elif toks[1] == "LEAVE":
                ip, port = toks[2], toks[3]
                print(f"Node leaving network: IP: {ip}, Port: {port}")

                # Remove the node from the list
                self.nodes = [n for n in self.nodes if not (n.ip == ip and n.port == int(port))]

                # Send success acknowledgment
                response = f"{len('LEAVEOK 0') + 5:04d} LEAVEOK 0"
            elif toks[1] == "SER":
                ip, port, file_name, hops = toks[2], toks[3], toks[4].strip('"'), int(toks[5])
                print(f"Search request: IP: {ip}, Port: {port}, File: {file_name}, Hops: {hops}")

                # Simulate file search (replace with actual logic)
                matching_files = [f for f in self.get_files() if file_name.lower() in f.lower()]
                no_files = len(matching_files)

                if no_files > 0:
                    response = f"SEROK {no_files} {self.ip} {self.port} {hops + 1} " + " ".join(matching_files)
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


if __name__ == "__main__":
    server = BootstrapServer(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT)
    server.start()
