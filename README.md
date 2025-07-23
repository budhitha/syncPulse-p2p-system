# syncPulse - Decentralized Node Network

A Python-based implementation of a decentralized network using nodes that connect, register, and communicate with each other over a distributed system. The project allows nodes to connect via a bootstrap server, exchange information, and manage a scalable peer-to-peer network.

---

## Features

- **Node Management**:
    - Each node is uniquely identified by its name, IP, and port.
    - Maintains a list of neighbors (connected nodes).
    - Can exchange commands to join or leave the network.

- **Bootstrap Server Integration**:
    - A central server for initial registration and discovery of other nodes.
    - Manages the registration, unregistration, and neighbor information.

- **Communication Protocol**:
    - Supports messages with a length-prefixed format for clarity and consistency.
    - Commands include:
        - `REG / UNREG`: Register/unregister with the bootstrap server.
        - `JOIN / LEAVE`: Add or remove nodes from the network.

- **Resilient Design**:
    - Modular components for managing connections, handling messages, and performing node communication.

---

## Project Structure

The project is organized as follows:
- **`app.py`**: Entry point for the Flask API.
- **`bootstrap_server.py`**: Manages the bootstrap server for node registration.
- **`integration_test.py`**: Script to test the entire flow of the P2P system.
- **`performance_analysis.py`**: Contains functions for logging and analyzing performance metrics.
- **`config/config.py`**: Configuration file for IPs, ports, and buffer sizes.
- **`connections/`**: Handles connections between nodes and the bootstrap server.
- **`files/`**: Contains sample files for testing.
- **`utils/`**: Utility functions for logging, file reading, and helpers.
- **`tests/`**: Unit tests for the system.

---

## How It Works

1. **Node Initialization**:
    - A node is created with its `name`, `ip`, `port`, and optional file list.
    - Each node attempts to register with the central **bootstrap server** on startup.

2. **Bootstrap Server**:
    - Acts as an entry point for new nodes.
    - Maintains a list of registered nodes and provides neighbors to newly registered nodes.

3. **Peer-to-Peer Communication**:
    - Once nodes join the network, they can send `JOIN` messages to neighbors or `LEAVE` when disconnecting.
    - Neighbors exchange this information, ensuring the network stays updated.

---

## Configuration

The system uses the following default configurations (defined in `config/config.py`):
- **Bootstrap Server IP**: `127.0.0.1`
- **Bootstrap Server Port**: `5000`
- **Node Default Port**: `5002`
- **Buffer Size**: `1024`
- **Flask API Port**: `4000`
- **Flask API URL**: `http://127.0.0.1:4000`

---

## Installation

### Prerequisites

- Python 3.8+ (Ensure it is installed and available in your PATH)
- Virtual Environment (recommended)

### Clone the Repository

```bash
git clone https://github.com/budhitha/syncPulse-p2p-system.git
cd syncPulse-p2p-system
```

### Set Up Python Dependencies

It's a good practice to use a virtual environment.

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate       # On Linux / macOS
   venv\Scripts\activate          # On Windows
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

---
## Running the system

1. Start the Bootstrap Server
    
    Run the bootstrap server to manage node registrations: 
    ```bash
    python bootstrap_server.py
    ```
   
2. Start the Flask API

    Start the Flask API for file generation and queries:
    ```bash
    python app.py
    ```
   
3. Run the Integration Test

    Test the entire flow of the system:
    ```bash
    python integration_test.py
    ```

---

## Usage

### Starting the Bootstrap Server

1. Run the bootstrap server independently:
   ```bash
   python bootstrap_server.py
   ```
   The bootstrap server listens for incoming connections and maintains the network's state.

---

### Running a Node

You can create and initialize a node by using the `main.py` file. Here is an example of how to start a node:

1. Modify `config/config.py` (e.g., for IPs, ports):
   ```python
   BOOTSTRAP_IP = "127.0.0.1"       # Bootstrap server IP
   BOOTSTRAP_PORT = 5000            # Bootstrap server port
   NODE_DEFAULT_PORT = 5001         # Default node port
   ```

2. Run the `main.py` script:
   ```bash
   python main.py
   ```

A new node will:
- Connect to the bootstrap server.
- Request other nodes in the network (if available).
- Register itself and become part of the network.

---

### Commands Supported by Nodes

#### **Commands**
- `REG`: Register a node with the bootstrap server.
- `UNREG`: Unregister a node.
- `JOIN`: Notify neighbors when joining the network.
- `LEAVE`: Notify neighbors when leaving the network.

---
## Troubleshooting

- **Flask API Not Responding**: Ensure the Flask server is running on port 4000.
- **Port Conflicts**: Check for conflicting processes using netstat and update the configuration if needed.
- **No Plots Displayed**: Ensure plot_cdf is called after metrics are populated in integration_test.py.

---

## Example Workflow

Here's an example of interacting with the network:

1. **Start the Bootstrap Server**:
   Run `bootstrap_server.py` to listen for incoming nodes.

   ```bash
   python bootstrap_server.py
   ```

2. **Start Node 1**:
   Run `main.py` for Node 1's initialization.

   ```bash
   python main.py
   ```

   Output:
   ```plaintext
   Node registered with Bootstrap Server: Neighbors - []
   ```

3. **Start Node 2**:
   Use the same `main.py` for Node 2, but ensure a different port is specified (if applicable).

   Output:
   ```plaintext
   Node registered with Bootstrap Server: Neighbors - [Node1]
   ```

4. **Joining the Network**:
   Once Node 2 registers, it sends `JOIN` messages to Node 1.

5. **Leaving the Network**:
   If Node 2 disconnects, it sends `LEAVE` notifications to its neighbors.

---

## Testing

Unit tests are included to ensure the reliability of key components. Run all tests using:

```bash
pytest tests/
```

This will test:
- Node registration/unregistration.
- Neighbor connections.
- Message handling (e.g., forming and parsing commands).

---

## Future Improvements

- Add features for file sharing between nodes.
- Implement recovery mechanisms for failed nodes.
- Optimize neighbor discovery using advanced protocols.
- Add support for encrypted communication.

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you'd like to improve or fix something.

---

## Author

[syncPulse Team]