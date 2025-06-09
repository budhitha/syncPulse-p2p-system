import socket
import threading

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
        data = conn.recv(1024).decode()
        print("Received:", data)
        toks = data.split()
        if len(toks) < 5 or toks[1] != "REG":
            response = "0013 REGOK 9999"  # error format
        else:
            ip, port, name = toks[2], toks[3], toks[4]
            # Check if already registered
            exists = any(n.ip == ip and n.port == int(port) for n in self.nodes)
            if not exists:
                self.nodes.append(Node(ip, int(port), name))
            # Prepare response
            num_nodes = min(len(self.nodes) - 1, 2)  # Exclude the registering node
            other_nodes = [n for n in self.nodes if not (n.ip == ip and n.port == int(port))]
            response = f"REGOK {num_nodes}"
            for n in other_nodes[:2]:
                response += f" {n.ip} {n.port} {n.name}"
            response = f"{len(response)+5:04d} {response}"

        conn.send(response.encode())
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

if __name__ == "__main__":
    server = BootstrapServer(ip="0.0.0.0", port=5000)
    server.start()