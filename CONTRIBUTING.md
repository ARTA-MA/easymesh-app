# Contributing to EasyMesh

Thank you for your interest in contributing to EasyMesh! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the Repository**
   - Fork the repository on GitHub
   - Clone your fork locally: `git clone https://github.com/yourusername/easymesh.git`

2. **Set Up Development Environment**
   - Follow the instructions in INSTALLATION.md to set up your development environment
   - Make sure all dependencies are installed

3. **Create a Branch**
   - Create a branch for your feature or bugfix: `git checkout -b feature/your-feature-name`
   - Use descriptive branch names that reflect the changes you're making

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use 4 spaces for indentation (not tabs)
- Keep line length to a maximum of 100 characters
- Use meaningful variable and function names

### Testing

- Write tests for new features or bug fixes
- Ensure all tests pass before submitting a pull request
- Run tests using: `pytest backend/tests/`

### Documentation

- Update documentation for any changes to functionality
- Document new features thoroughly
- Use clear, concise language in comments and documentation

## Submitting Changes

1. **Commit Your Changes**
   - Make small, focused commits with clear messages
   - Format commit messages as: `[Component] Brief description of change`
   - Example: `[FileTransfer] Add retry mechanism for failed transfers`

2. **Push to Your Fork**
   - Push your changes to your fork on GitHub

3. **Create a Pull Request**
   - Go to the original EasyMesh repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of your changes
   - Reference any related issues

4. **Code Review**
   - Be responsive to feedback and questions
   - Make requested changes promptly
   - Keep the pull request updated with the latest changes

## Release Process

### Version Numbering

We follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality additions
- PATCH: Backwards-compatible bug fixes

### Creating Releases

1. Update version number in relevant files
2. Update CHANGELOG.md with changes
3. Create a tagged release on GitHub
4. Build and upload release artifacts

## Building Executable Files

To build the executable (.exe) file for Windows:

1. Ensure all dependencies are installed
2. Run the build script: `.\build-windows-easymesh.bat`
3. The executable will be created in the `dist` directory

## Questions and Support

If you have questions or need help:
- Open an issue on GitHub
- Reach out to the maintainers
- Check existing documentation and issues first

Thank you for contributing to EasyMesh!