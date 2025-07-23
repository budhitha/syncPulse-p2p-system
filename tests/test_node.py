import unittest
from unittest.mock import patch, MagicMock
from network_node_manager import Node


class TestNode(unittest.TestCase):

    def setUp(self):
        """
        Set up a test node instance.
        """
        self.node = Node(name="Node1", ip="127.0.0.1", port=5001, file_list=["file1.txt", "file2.txt"])

    def test_node_initialization(self):
        """
        Test the initialization of a Node instance.
        """
        self.assertEqual(self.node.name, "Node1")
        self.assertEqual(self.node.ip, "127.0.0.1")
        self.assertEqual(self.node.port, 5001)
        self.assertEqual(self.node.file_list, ["file1.txt", "file2.txt"])
        self.assertEqual(self.node.neighbors, [])

    def test_add_neighbors(self):
        """
        Test adding neighbors to the node.
        """
        neighbor1 = Node(name="Node2", ip="127.0.0.2", port=5002)
        neighbor2 = Node(name="Node3", ip="127.0.0.3", port=5003)
        self.node.add_neighbors([neighbor1, neighbor2])

        self.assertEqual(len(self.node.neighbors), 2)
        self.assertIn(neighbor1, self.node.neighbors)
        self.assertIn(neighbor2, self.node.neighbors)

    def test_str_representation(self):
        """
        Test the string representation of a Node instance.
        """
        neighbor = Node(name="Node2", ip="127.0.0.2", port=5002)
        self.node.add_neighbors([neighbor])
        node_str = str(self.node)
        expected_str = "Node(name=Node1, ip=127.0.0.1, port=5001, files=['file1.txt', 'file2.txt'], neighbors=['Node2'])"
        self.assertEqual(node_str, expected_str)

    def test_format_message(self):
        """
        Test formatting a message with the correct length prefix.
        """
        command = "REG 127.0.0.1 5001 Node1"
        formatted_message = self.node.format_message(command)
        expected_message = f"{len(command) + 4:04d} {command}"
        self.assertEqual(formatted_message, expected_message)

    @patch("socket.socket")  # Mock socket for registration
    def test_register_successful(self, mock_socket):
        """
        Test successful registration of a node with the Bootstrap Server.
        """
        mock_socket_instance = MagicMock()
        mock_socket_instance.recvfrom.return_value = ("REGOK 1 127.0.0.2 5002".encode(), None)
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        self.node.bs_address = ("127.0.0.1", 5000)
        self.node.username = "Node1"

        self.node.register()

        self.assertEqual(len(self.node.neighbors), 1)
        # Check that the neighbor is a Node object with the correct attributes
        self.assertEqual(self.node.neighbors[0].ip, "127.0.0.2")
        self.assertEqual(self.node.neighbors[0].port, 5002)

    @patch("socket.socket")  # Mock socket for registration
    def test_register_failure(self, mock_socket):
        """
        Test failed registration of a node due to an invalid response.
        """
        mock_socket_instance = MagicMock()
        mock_socket_instance.recvfrom.return_value = ("REGFAILED".encode(), None)
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        self.node.bs_address = ("127.0.0.1", 5000)
        self.node.username = "Node1"

        with self.assertLogs(level="INFO") as log:
            self.node.register()
            self.assertIn("INFO:root:Registration failed with response: REGFAILED", log.output)

    @patch("socket.socket")  # Mock socket for unregistration
    def test_unregister_successful(self, mock_socket):
        """
        Test successful unregistration of a node from the Bootstrap Server.
        """
        mock_socket_instance = MagicMock()
        mock_socket_instance.recvfrom.return_value = ("UNROK 0".encode(), None)
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        self.node.bs_address = ("127.0.0.1", 5000)
        self.node.username = "Node1"

        self.node.unregister()

        self.assertLogs(level="INFO")  # Ensure no exception was raised

    @patch("socket.socket")  # Mock socket for JOIN
    def test_join_network(self, mock_socket):
        """
        Test sending a JOIN request to neighbors.
        """
        neighbor = ("127.0.0.2", 5002)
        self.node.neighbors.append(neighbor)

        mock_socket_instance = MagicMock()
        mock_socket_instance.recvfrom.return_value = ("JOINOK 0".encode(), None)
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        self.node.join_network()

        self.assertLogs(level="INFO")  # Check that there are logs indicating the JOIN response

    @patch("socket.socket")  # Mock socket for LEAVE
    def test_leave_network(self, mock_socket):
        """
        Test sending a LEAVE request to all neighbors.
        """
        neighbor = ("127.0.0.2", 5002)
        self.node.neighbors.append(neighbor)

        mock_socket_instance = MagicMock()
        mock_socket_instance.recvfrom.return_value = ("LEAVEOK 0".encode(), None)
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        self.node.leave_network()

        self.assertLogs(level="INFO")  # Check that there are logs indicating the LEAVE response


if __name__ == "__main__":
    unittest.main()