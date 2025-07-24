import logging
import shlex
import socket

from config.config import BOOTSTRAP_IP, BOOTSTRAP_PORT
from connections.bootstrap_server_connection import BootstrapServerConnection
from node import Node
from ttypes import Node as SimpleNode


def parse_command_parts(parts):
    try:
        _, _, ip, port, username = parts
        port = int(port)
        return ip, port, username
    except ValueError:
        raise ValueError("Invalid command format. Ensure the command includes <IP_address>, <port_no>, and <username>.")


def main():
    # Set up logging configuration at the entry point
    logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(levelname)s - %(message)s\n')

    # Bootstrap server details
    bs_node = SimpleNode(ip=BOOTSTRAP_IP, port=BOOTSTRAP_PORT, name="BootstrapServer")

    while True:
        user_input = input("Enter command (e.g., 0036 REG 129.82.123.45 5001 1234abcd or exit): ").strip()
        if user_input.lower() == "exit":
            logging.info("Exiting...")
            break

        try:
            # Parse the input command
            parts = shlex.split(user_input)
            if len(parts) == 5 and parts[1] == "REG":
                ip, port, username = parse_command_parts(parts)
                my_node = Node(ip=ip, port=port, name=username, file_list=[], peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT)],
                               bs_ip=BOOTSTRAP_IP, bs_port=BOOTSTRAP_PORT)

                nodes = BootstrapServerConnection(bs=bs_node, me=my_node).connect_to_bs()
                logging.info(f"Registration successful. Nodes received: {nodes}")
                print('\n')

            elif len(parts) == 5 and parts[1] == "UNREG":
                ip, port, username = parse_command_parts(parts)
                my_node = Node(ip=ip, port=port, name=username, file_list=[], peers=[(BOOTSTRAP_IP, BOOTSTRAP_PORT)],
                               bs_ip=BOOTSTRAP_IP, bs_port=BOOTSTRAP_PORT)

                response = BootstrapServerConnection(bs=bs_node, me=my_node).unreg_from_bs()
                result = handle_unreg_response(response)
                logging.info(result)
                print('\n')


            elif len(parts) == 4 and parts[1] == "JOIN":
                _, _, target_ip, target_port = parts
                target_port = int(target_port)

                # Dynamically get the local IP
                local_ip = socket.gethostbyname(socket.gethostname())  # Replace with the actual port

                my_node = SimpleNode(ip=local_ip, port=BOOTSTRAP_PORT, name="MyNode")  # Example node details
                response = BootstrapServerConnection(bs=bs_node, me=my_node).join_network(target_ip=target_ip,
                                                                                          target_port=target_port)
                result = handle_join_response(response)
                logging.info(result)
                print('\n')
            elif len(parts) == 4 and parts[1] == "LEAVE":
                _, _, ip, port = parts
                port = int(port)

                my_node = SimpleNode(ip=ip, port=port, name="MyNode")
                response = BootstrapServerConnection(bs=bs_node, me=my_node).leave_network()
                logging.info(response)
                print('\n')
            elif len(parts) == 6 and parts[1] == "SER":
                _, _, ip, port, file_name, hops = parts
                port = int(port)
                hops = int(hops)

                my_node = SimpleNode(ip=ip, port=port, name="MyNode")
                response = BootstrapServerConnection(bs=bs_node, me=my_node).search_file(file_name=file_name.strip('"'),
                                                                                         hops=hops)
                logging.info(response)
                print('\n')

            else:
                logging.warning("Invalid command format. Use: <length> REG/UNREG <IP_address> <port_no> <username>\n")
                print('\n')

        except Exception as e:
            logging.error(e)
            print('\n')


def handle_unreg_response(response):
    try:
        # Split the response into parts
        parts = response.split()
        if len(parts) != 3 or parts[1] != "UNROK":
            raise ValueError("Invalid UNROK response format")

        # Extract the value
        value = int(parts[2])
        if value == 0:
            return "Unregistration successful."
        elif value == 9999:
            return "Error: Unregistration failed. IP and port may not be in the registry or command is incorrect."
        else:
            return f"Error: Unknown response value {value}"
    except Exception as e:
        return f"Error while processing UNROK response: {e}"


def handle_join_response(response):
    try:
        parts = response.split()
        if len(parts) != 3 or parts[1] != "JOINOK":
            raise ValueError("Invalid JOINOK response format")

        value = int(parts[2])
        if value == 0:
            return "Join successful."
        elif value == 9999:
            return "Error: Join failed. Could not add the new node to the routing table."
        else:
            return f"Error: Unknown response value {value}"
    except Exception as e:
        return f"Error while processing JOINOK response: {e}"


if __name__ == "__main__":
    main()
