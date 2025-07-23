import unittest
from unittest.mock import patch, MagicMock

from connections.bootstrap_server_connection import BootstrapServerConnection
from ttypes import Node

class TestBootstrapServerConnection(unittest.TestCase):

    def setUp(self):
        """
        Set up test data and dependencies.
        """
        self.bootstrap = Node("127.0.0.1", 5000, "bootstrap")  # Mock bootstrap server node
        self.me = Node("127.0.0.1", 5001, "peer1")            # Mock current node
        self.connection = BootstrapServerConnection(self.bootstrap, self.me)

    @patch('socket.socket')  # Mock the socket class
    def test_message_with_length(self, mock_socket):
        """
        Test if the `message_with_length` prepends the correct length.
        """
        message = "REG 127.0.0.1 5001 peer1"
        formatted_message = self.connection.message_with_length(message)
        # Expected length = len("REG 127.0.0.1 5001 peer1") + 5 (length prefix plus space)
        expected_length = len(message) + 5
        self.assertEqual(formatted_message[:4], f"{expected_length:04d}")

    @patch('socket.socket')  # Mock the socket class
    def test_connect_to_bs_success(self, mock_socket):
        """
        Test successful registration of a node with the bootstrap server.
        """
        # Mock the behavior of socket to simulate a successful registration
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate BS returning a REGOK response
        mock_socket_instance.recv.return_value = b"0025 REGOK 1 127.0.0.1 5002 peer2"

        with patch.object(self.connection, 'unreg_from_bs') as mock_unreg:
            mock_unreg.return_value = None  # Ensures unreg_from_bs doesn't do anything

            users = self.connection.connect_to_bs()  # This line calls the mocked socket.recv

        # Ensure that the returned neighbors list is parsed correctly
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].ip, "127.0.0.1")
        self.assertEqual(users[0].port, 5002)
        self.assertEqual(users[0].name, "peer2")

    @patch('socket.socket')  # Mock the socket class
    def test_connect_to_bs_failure_invalid_response(self, mock_socket):
        """
        Test registration failure with an invalid bootstrap server response.
        """
        # Mock the behavior of socket with an invalid response
        mock_socket.return_value.recv.return_value = "INVALID_RESPONSE".encode()

        with patch.object(self.connection, 'unreg_from_bs') as mock_unreg:
            mock_unreg.return_value = None  # Mock unreg_from_bs

            # Assert that RuntimeError is raised
            with self.assertRaises(RuntimeError):
                self.connection.connect_to_bs()

    @patch('socket.socket')  # Mock the socket class
    def test_unreg_from_bs_success(self, mock_socket):
        """
        Test successful unregistration of a node with the bootstrap server.
        """
        # Mock the behavior of socket to simulate a successful unregistration
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate BS returning a length-prefixed UNROK response
        mock_socket_instance.recv.return_value = "0009 UNROK 0".encode()

        try:
            self.connection.unreg_from_bs()  # Should not raise an exception
        except RuntimeError:
            self.fail("unreg_from_bs raised RuntimeError unexpectedly!")


    @patch('socket.socket')  # Mock the socket class
    def test_unreg_from_bs_failure(self, mock_socket):
        """
        Test unregistration failure due to an invalid server response.
        """
        # Mock the behavior of socket with an invalid response
        mock_socket.return_value.recv.return_value = "UNROK 1".encode()

        # Assert that RuntimeError is raised
        with self.assertRaises(RuntimeError):
            self.connection.unreg_from_bs()

    @patch('socket.socket')  # Mock the socket class
    def test_context_manager_enter_exit(self, mock_socket):
        """
        Test the context manager functionality of BootstrapServerConnection.
        """
        # Mock both `connect_to_bs` and `unreg_from_bs` methods
        with patch.object(self.connection, 'connect_to_bs', return_value=[]) as mock_connect:
            with patch.object(self.connection, 'unreg_from_bs') as mock_unreg:
                # Use the connection inside the context manager
                with self.connection as conn:
                    self.assertEqual(conn.users, [])

                # Ensure the methods were called correctly
                mock_connect.assert_called_once()
                mock_unreg.assert_called_once()

if __name__ == '__main__':
    unittest.main()