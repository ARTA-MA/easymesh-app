# EasyMesh Installation Guide

This document provides detailed instructions for installing and setting up EasyMesh on different platforms.

## Windows Installation

### Method 1: Using Pre-built Executable (Recommended)

1. **Download the Application**
   - Go to the [Releases](https://github.com/yourusername/easymesh/releases) page
   - Download the latest `easymesh.exe` file

2. **Run the Application**
   - Double-click the downloaded `easymesh.exe` file
   - If Windows Defender SmartScreen shows a warning, click "More info" and then "Run anyway"
   - When prompted by Windows Firewall, select "Allow access" for private networks

3. **Verify Installation**
   - The application will automatically start and open in your default web browser
   - You should see the EasyMesh interface at `http://localhost:8001`

### Method 2: Building from Source

#### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- Node.js and npm (for frontend development)

#### Steps

1. **Clone the Repository**
   ```
   git clone https://github.com/yourusername/easymesh.git
   cd easymesh
   ```

2. **Set Up Python Environment**
   ```
   python -m venv .venv
   ```

   Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install Backend Dependencies**
   ```
   pip install -r backend/requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```
   cd frontend
   npm install
   cd ..
   ```

5. **Build the Application**
   - Windows: `.\build-windows-easymesh.bat`
   - Linux/Mac: `./build-linux-easymesh.sh` (if available)

6. **Run the Built Application**
   - Windows: `.\dist\easymesh.exe`
   - Linux/Mac: `./dist/easymesh` (if available)

## Linux Installation

Currently, EasyMesh is primarily developed for Windows. Linux support is planned for future releases. However, you can run the development version:

1. **Clone and Set Up**
   ```
   git clone https://github.com/yourusername/easymesh.git
   cd easymesh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Run Development Server**
   ```
   cd backend
   python run_local.py
   ```

3. **Access the Application**
   - Open your browser and navigate to `http://localhost:8001`

## Mac Installation

Mac support is planned for future releases. The development version can be run similarly to the Linux instructions.

## Troubleshooting Installation Issues

### Common Issues and Solutions

1. **Application Won't Start**
   - Ensure you have the necessary permissions to run executables
   - Check if another application is using port 8001
   - Try running as administrator (right-click, "Run as administrator")

2. **Missing Dependencies**
   - If building from source, ensure all required Python packages are installed
   - Check the console output for specific error messages

3. **Firewall Blocking**
   - Ensure Windows Firewall or other security software allows EasyMesh
   - Configure your antivirus to allow EasyMesh

4. **Browser Doesn't Open**
   - Manually navigate to `http://localhost:8001` in your browser
   - Check if the server is running by looking for the EasyMesh process in Task Manager

### Getting Help

If you continue to experience installation issues:

1. Check the logs in `%APPDATA%\EasyMesh\logs` (Windows) or `~/.easymesh/logs` (Linux/Mac)
2. Open an issue on the [GitHub repository](https://github.com/yourusername/easymesh/issues) with:
   - Your operating system and version
   - Steps you've taken
   - Any error messages
   - Log files if available