class Node:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.max_hops = 3
        self.file_list = []
        self.routing_table = []  # Initialize the routing table as an empty list