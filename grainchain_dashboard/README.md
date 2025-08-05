# Grainchain Dashboard 🚀

A modern, web-based dashboard for managing Grainchain sandbox providers, built with [Reflex](https://reflex.dev/).

## Features ✨

### 🏗️ **Core Functionality**
- **Multi-Provider Support**: E2B, Daytona, Morph, Modal, and Local providers
- **Sandbox Management**: Create, manage, and monitor sandbox instances
- **Command Execution**: Interactive terminal with real-time output
- **File Operations**: Upload, download, and browse sandbox files
- **Snapshot Management**: Create, restore, and manage sandbox snapshots

### 🎯 **Advanced Features**
- **Provider Health Monitoring**: Real-time status of all providers
- **Configuration Management**: Secure API key and settings management
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live feedback for all operations
- **Keyboard Shortcuts**: Efficient navigation and control

### 🛡️ **Security & Reliability**
- **Encrypted Credential Storage**: Secure API key management
- **Error Handling**: Comprehensive error recovery and user feedback
- **Async Operations**: Non-blocking UI with background processing
- **Resource Cleanup**: Automatic sandbox and resource management

## Quick Start 🚀

### Prerequisites
- Python 3.12+
- Node.js 18+ (for Reflex)

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd grainchain_dashboard
pip install -r requirements.txt
```

2. **Configure providers** (optional):
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

3. **Run the dashboard**:
```bash
reflex run
```

4. **Open in browser**:
```
http://localhost:3000
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file with your provider configurations:

```bash
# App Configuration
DEBUG=false
HOST=localhost
PORT=3000
SECRET_KEY=your-secret-key-here

# Provider API Keys
E2B_API_KEY=your-e2b-api-key
DAYTONA_API_KEY=your-daytona-api-key
MORPH_API_KEY=your-morph-api-key
MODAL_TOKEN_ID=your-modal-token-id
MODAL_TOKEN_SECRET=your-modal-token-secret

# Provider Settings
DEFAULT_PROVIDER=local
LOCAL_WORKING_DIR=./workspace
E2B_TEMPLATE=base
DAYTONA_WORKSPACE_TEMPLATE=python-dev
MORPH_IMAGE_ID=morphvm-minimal

# Dashboard Features
ENABLE_MONITORING=true
ENABLE_ANALYTICS=true
ENABLE_COLLABORATION=false
```

### Provider Setup

#### Local Provider ✅
- **No setup required** - works out of the box
- **Best for**: Development and testing

#### E2B Provider 🌐
```bash
pip install grainchain[e2b]
export E2B_API_KEY=your-api-key
```
- **Get API key**: [E2B Dashboard](https://e2b.dev/dashboard)
- **Best for**: Production workloads

#### Daytona Provider 🛠️
```bash
pip install grainchain[daytona]
export DAYTONA_API_KEY=your-api-key
```
- **Get API key**: [Daytona Dashboard](https://daytona.io/)
- **Best for**: Full development environments

#### Morph Provider ⚡
```bash
pip install grainchain[morph]
export MORPH_API_KEY=your-api-key
```
- **Get API key**: [Morph Dashboard](https://morph.dev/)
- **Best for**: Fast snapshots and custom images

#### Modal Provider 🚀
```bash
pip install grainchain[modal]
export MODAL_TOKEN_ID=your-token-id
export MODAL_TOKEN_SECRET=your-token-secret
```
- **Get tokens**: [Modal Dashboard](https://modal.com/)
- **Best for**: Scalable cloud compute

## Usage Guide 📖

### 1. **Provider Selection**
- Navigate to the **Providers** page
- Check provider status and availability
- Configure API keys in **Settings**
- Select your preferred provider

### 2. **Sandbox Management**
- Click **Create Sandbox** to start a new instance
- Monitor active sandboxes in the **Dashboard**
- Switch between sandboxes as needed

### 3. **Command Execution**
- Go to the **Terminal** page
- Enter commands in the input field
- View real-time output and history
- Use quick command buttons for common operations

### 4. **File Operations**
- Access the **Files** page
- Browse sandbox directories
- Upload files using the upload form
- Download files with the context menu

### 5. **Snapshot Management**
- Visit the **Snapshots** page
- Create snapshots with descriptions
- Restore previous states
- Manage snapshot lifecycle

## Architecture 🏗️

```
┌─────────────────┐
│   Reflex UI     │  ← Web Interface
└─────────────────┘
         │
┌─────────────────┐
│ Dashboard State │  ← State Management
└─────────────────┘
         │
┌─────────────────┐
│ Service Layer   │  ← Async Bridge
└─────────────────┘
         │
┌─────────────────┐
│   Grainchain    │  ← Core Library
└─────────────────┘
         │
┌─────────────────┐
│   Providers     │  ← Sandbox Services
│ (E2B, Daytona,  │
│  Morph, etc.)   │
└─────────────────┘
```

### Key Components

- **`main.py`**: Application entry point and routing
- **`state.py`**: Reflex state management and business logic
- **`services/`**: Async-to-sync bridge for Grainchain operations
- **`components/`**: Reusable UI components
- **`pages/`**: Page-level components and layouts
- **`config.py`**: Configuration management

## Development 🛠️

### Project Structure
```
grainchain_dashboard/
├── main.py              # App entry point
├── state.py             # State management
├── config.py            # Configuration
├── components/          # UI components
│   ├── provider_settings.py
│   ├── command_terminal.py
│   ├── file_browser.py
│   ├── snapshot_manager.py
│   ├── sidebar.py
│   └── status_bar.py
├── pages/               # Page components
│   └── dashboard.py
├── services/            # Business logic
│   └── grainchain_service.py
├── security/            # Security utilities
├── utils/               # Helper functions
└── tests/               # Test files
```

### Running in Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
reflex run --env dev

# Run tests
pytest tests/

# Format code
black grainchain_dashboard/
```

### Adding New Providers

1. **Update configuration** in `config.py`
2. **Add provider settings** in `components/provider_settings.py`
3. **Test integration** with the service layer
4. **Update documentation**

## Troubleshooting 🔧

### Common Issues

#### Provider Not Available
- Check API keys in settings
- Verify provider dependencies are installed
- Check network connectivity

#### Sandbox Creation Fails
- Ensure provider is healthy
- Check resource limits and quotas
- Verify configuration settings

#### Commands Not Executing
- Confirm sandbox is selected and running
- Check command syntax and permissions
- Review error messages in output

#### File Operations Failing
- Verify file paths and permissions
- Check available disk space
- Ensure sandbox is accessible

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
reflex run
```

### Logs and Monitoring

- Application logs: Check console output
- Provider status: Monitor the Providers page
- System metrics: View the Dashboard overview

## Contributing 🤝

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest`
5. **Submit a pull request**

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for changes
- Ensure all providers are tested

## Security 🔒

### Best Practices

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Regularly rotate** API keys and secrets
- **Monitor access logs** for unusual activity

### Reporting Security Issues

Please report security vulnerabilities privately to the maintainers.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- **Documentation**: Check this README and inline comments
- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

## Roadmap 🗺️

### Upcoming Features
- [ ] **Batch Operations**: Manage multiple sandboxes simultaneously
- [ ] **Usage Analytics**: Track resource usage and costs
- [ ] **Team Collaboration**: Share sandboxes and configurations
- [ ] **API Integration**: REST API for external integrations
- [ ] **Plugin System**: Custom provider extensions
- [ ] **Mobile App**: Native mobile companion app

### Performance Improvements
- [ ] **Caching Layer**: Improve response times
- [ ] **Background Tasks**: Better async operation handling
- [ ] **Resource Optimization**: Reduce memory usage
- [ ] **Connection Pooling**: Optimize provider connections

---

**Built with ❤️ using [Reflex](https://reflex.dev/) and [Grainchain](https://github.com/codegen-sh/grainchain)**

