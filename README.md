# EasyMesh

EasyMesh is a WebRTC-based peer-to-peer file transfer application that allows users to share files directly between browsers without server intervention.

## Features

- Direct peer-to-peer file transfers using WebRTC
- No server required for file transfer (signaling server only)
- Cross-platform compatibility
- Simple and intuitive user interface
- Secure file transfers
- Support for multiple file transfers simultaneously

## Architecture

EasyMesh consists of two main components:

1. **Frontend**: A React application that handles the user interface and WebRTC connections
2. **Backend**: A Python FastAPI server that acts as a signaling server to facilitate connection establishment between peers

## Installation

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.7 or higher)
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/easymesh.git
   cd easymesh
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the signaling server:
   ```bash
   cd backend
   python server.py
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

The application will be available at `http://localhost:3000`.

## Usage

1. Open the application in two different browsers or browser tabs
2. One user creates a room by clicking "Create Room"
3. The other user joins the room by entering the room ID
4. Once connected, either user can select files to send
5. The receiving user will get a notification and can choose to accept or reject the file transfer

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.