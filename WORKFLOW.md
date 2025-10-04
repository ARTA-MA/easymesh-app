# EasyMesh Application Workflow

This document explains the internal workflow of the EasyMesh application, providing insights into how the system operates.

## Application Architecture

EasyMesh follows a client-server architecture with these main components:

1. **Backend Server**: Python-based FastAPI server handling file transfers and device connections
2. **Frontend Interface**: Web-based UI for user interaction
3. **File Transfer System**: Optimized system for transferring files between devices
4. **Connection Manager**: Handles device discovery and connection maintenance

## Startup Workflow

1. **Initialization Process**
   - Application executable starts the Python backend server
   - Server initializes the FastAPI application and routers
   - Static files are mounted for the frontend interface
   - Default configuration is loaded from environment variables or defaults

2. **Network Interface Setup**
   - Server identifies available network interfaces
   - Local IP address is determined for connection purposes
   - Server binds to the specified port (default: 8001)

3. **Frontend Launch**
   - Web interface is automatically opened in the default browser
   - Frontend connects to the backend API
   - Initial device status is displayed

## Device Discovery Workflow

1. **Local Network Scanning**
   - Application broadcasts its presence on the local network
   - Listens for other EasyMesh instances broadcasting
   - Builds a list of available devices

2. **Connection Establishment**
   - When a new device connects to the web interface
   - Connection details are registered in the backend
   - Device appears in the connected devices list on all interfaces

3. **Heartbeat Mechanism**
   - Regular heartbeat signals maintain connection status
   - Devices that stop responding are marked as disconnected
   - Automatic reconnection attempts for temporarily disconnected devices

## File Transfer Workflow

### Single File Transfer

1. **Transfer Initiation**
   - User selects a file and destination device
   - Frontend sends transfer request to backend
   - Backend generates a unique transfer ID

2. **Transfer Execution**
   - File is read using the BufferedFileReader for efficiency
   - Data is sent to the destination using optimized socket settings
   - Progress is tracked and reported back to the frontend

3. **Transfer Completion**
   - Destination confirms successful receipt
   - Transfer is marked as complete
   - Success notification is displayed to the user

### Parallel File Transfer (Large Files)

1. **File Analysis**
   - Backend analyzes file size to determine if chunking is beneficial
   - For files above the threshold, parallel transfer is used

2. **Chunking Process**
   - File is divided into optimal-sized chunks
   - Chunk size is determined based on file size and network conditions
   - Each chunk is assigned a sequence number

3. **Parallel Upload**
   - Multiple connections are established (default: 3)
   - Chunks are uploaded simultaneously using ThreadPoolExecutor
   - Each chunk transfer has independent progress tracking

4. **Reassembly**
   - Once all chunks are transferred, they are reassembled on the destination
   - Integrity verification ensures complete and accurate transfer
   - Temporary chunk files are cleaned up

## Error Handling Workflow

1. **Transfer Failure Detection**
   - Network interruptions or errors are detected during transfer
   - Transfer status is updated to reflect the error

2. **Automatic Retry System**
   - Failed transfers trigger the retry mechanism
   - Exponential backoff algorithm determines retry timing
   - System attempts up to 3 retries by default

3. **User Notification**
   - Transfer status updates are pushed to the frontend
   - Users are notified of errors and retry attempts
   - Manual retry option is provided for persistently failing transfers

## Shutdown Workflow

1. **Transfer Completion**
   - Active transfers are completed or paused based on user preference
   - Transfer status is saved for resumption if needed

2. **Connection Termination**
   - Connected devices are notified of shutdown
   - Connections are gracefully closed

3. **Resource Cleanup**
   - Temporary files are removed
   - Network sockets are closed
   - Server process is terminated

## Performance Optimization

EasyMesh continuously optimizes performance through:

1. **Adaptive Chunking**
   - Chunk sizes are adjusted based on network conditions
   - Optimal parallel connection count is determined dynamically

2. **Memory Management**
   - ChunkedFileReader streams data directly without loading entire files
   - Buffer sizes are optimized for current system resources

3. **Connection Pooling**
   - Connections are reused when possible to reduce overhead
   - Connection pool is managed to prevent resource exhaustion

## Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Source     │     │  EasyMesh   │     │ Destination │
│  Device     │────▶│  Server     │────▶│  Device     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   ▲                   │
       │                   │                   │
       ▼                   │                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  File       │     │  Transfer   │     │  File       │
│  System     │────▶│  Manager    │────▶│  System     │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          │
                          ▼
                    ┌─────────────┐
                    │  Progress   │
                    │  Tracker    │
                    └─────────────┘
```

This workflow documentation provides a comprehensive overview of how EasyMesh operates internally, from startup to shutdown, including the optimized file transfer mechanisms and error handling procedures.