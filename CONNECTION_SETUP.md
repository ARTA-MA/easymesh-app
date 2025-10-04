# EasyMesh Connection Setup Guide

This guide provides detailed instructions for setting up connections between devices using EasyMesh.

## Basic Connection Setup

### Starting the EasyMesh Server

1. **Launch EasyMesh**
   - Run the EasyMesh application on your main device
   - The application will start a local server and open in your default browser
   - Note the IP address displayed in the application interface (typically shown as http://192.168.x.x:8001)

2. **Server Information**
   - The server runs on port 8001 by default
   - Your local IP address is displayed in the application header
   - This information is needed to connect other devices

### Connecting Client Devices

1. **Same Network Connection**
   - Ensure all devices are connected to the same local network (Wi-Fi or Ethernet)
   - Devices must be able to reach each other on the network

2. **Accessing from Other Devices**
   - On other devices (smartphones, tablets, laptops), open a web browser
   - Enter the server's IP address and port in the address bar (e.g., http://192.168.1.100:8001)
   - The EasyMesh interface should load, connecting this device to the network

3. **Verifying Connection**
   - Connected devices appear in the "Connected Devices" list on all interfaces
   - Each device is identified by its hostname and IP address
   - A green indicator shows active connections

## Advanced Connection Options

### Custom Port Configuration

If the default port (8001) is already in use or you prefer a different port:

1. **Changing the Port**
   - Launch EasyMesh with the `--port` parameter: `easymesh.exe --port 8080`
   - Or change the port in the settings interface under "Network Settings"

2. **Updating Connections**
   - After changing the port, all client devices must use the new port in the URL
   - Example: http://192.168.1.100:8080

### Connection Troubleshooting

#### Network Issues

1. **Firewall Configuration**
   - Ensure Windows Firewall allows EasyMesh through both private and public networks
   - To check: Open Windows Security → Firewall & Network Protection → Allow an app through firewall
   - Verify EasyMesh is checked for both Private and Public networks

2. **Router Settings**
   - Some routers have client isolation enabled, which prevents devices from seeing each other
   - Disable client isolation or AP isolation in your router settings if available

3. **VPN Interference**
   - VPNs can interfere with local network discovery
   - Temporarily disable VPNs when using EasyMesh

#### Connection Testing

If you're having trouble connecting devices:

1. **Ping Test**
   - Open Command Prompt on Windows or Terminal on other systems
   - Type `ping 192.168.x.x` (replace with the server's IP address)
   - Verify you receive replies, indicating network connectivity

2. **Port Check**
   - Use the built-in connection test in EasyMesh (Settings → Network → Test Connection)
   - This verifies if the port is accessible from other devices

3. **Manual Connection Check**
   - On the client device, open a browser and try accessing the server IP and port
   - If the page doesn't load, there may be a network or firewall issue

## Multi-Device Setup

### Creating a Device Network

1. **Hub and Spoke Model**
   - Designate one device as the main server (hub)
   - Connect all other devices to this main server
   - This creates a star topology for your EasyMesh network

2. **Device Discovery**
   - EasyMesh automatically discovers other instances on the local network
   - Discovered devices appear in the "Available Devices" list
   - Click "Connect" to establish a connection with discovered devices

### Managing Multiple Connections

1. **Connection Limits**
   - By default, EasyMesh supports up to 10 simultaneous device connections
   - This limit can be adjusted in the advanced settings

2. **Connection Priority**
   - You can set priority levels for different devices
   - Higher priority devices receive bandwidth preference during transfers

3. **Disconnecting Devices**
   - To disconnect a device, click the "Disconnect" button next to the device name
   - Disconnected devices can reconnect at any time

## Security Considerations

1. **Local Network Only**
   - EasyMesh is designed for use on trusted local networks only
   - It does not implement authentication for simplicity and ease of use

2. **Network Isolation**
   - For added security, consider using EasyMesh on an isolated network
   - This prevents unauthorized access to your file transfers

3. **Future Security Features**
   - Password protection and encryption features are planned for future releases
   - Check for updates to access these features when available