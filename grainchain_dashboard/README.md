# 🌾 Grainchain Dashboard - Production Ready

A fully-featured, production-ready dashboard for managing Grainchain sandboxes with comprehensive functionality including snapshot management, real-time program execution, file operations, and multi-provider support.

## ✨ Features

### 🚀 Core Functionality
- **Real Sandbox Management**: Create, manage, and monitor sandboxes across multiple providers
- **Live Program Execution**: Interactive terminal with real-time command execution
- **Snapshot Operations**: Create, save, restore, and manage sandbox snapshots
- **File Management**: Upload, download, browse, and edit files within sandboxes
- **Multi-Provider Support**: E2B, Daytona, Morph, Modal, and Local providers

### 🔧 Advanced Features
- **Real-time Status Monitoring**: Live updates of sandbox status and resource usage
- **Command History**: Full command history with autocomplete
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Security**: Secure credential management and input validation
- **Responsive Design**: Modern, dark-themed UI that works on all devices

### 🏗️ Architecture
- **Production-Ready**: Built with real Grainchain integration, not mock data
- **Service Layer**: Clean separation between UI and business logic
- **Async Operations**: Full async support for non-blocking operations
- **State Management**: Reactive state management with Reflex
- **Modular Design**: Component-based architecture for maintainability

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Grainchain installed and configured
- Provider credentials (E2B, Daytona, etc.) if using cloud providers

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your provider credentials
   ```

3. **Run the Dashboard**
   ```bash
   python main.py
   ```

4. **Access Dashboard**
   Open http://localhost:3000 in your browser

## 📖 Usage Guide

### 1. Initialize Grainchain
- Click "Initialize Grainchain" on the dashboard
- This connects to all available providers

### 2. Create Sandboxes
- Go to "Providers" page
- Select an available provider
- Click "Create Sandbox"

### 3. Execute Commands
- Go to "Terminal" page
- Enter commands in the terminal
- View real-time output

### 4. Manage Files
- Go to "Files" page
- Browse, upload, and download files
- Edit files directly in the browser

### 5. Work with Snapshots
- Go to "Snapshots" page
- Create snapshots of current state
- Restore from previous snapshots

## 🔌 Provider Support

### Local Provider
- ✅ Always available
- ✅ Direct system access
- ✅ Full feature support

### E2B Provider
- 🔑 Requires API key
- ✅ Cloud sandboxes
- ✅ Template support
- ✅ Auto-scaling

### Daytona Provider
- 🔑 Requires API key
- ✅ Development workspaces
- ✅ Collaboration features

### Morph Provider
- 🔑 Requires API key
- ✅ Custom VMs
- ✅ Fast snapshots
- ✅ Resource control

### Modal Provider
- 🔑 Requires tokens
- ✅ Serverless compute
- ✅ Automatic scaling

## 🛠️ Configuration

### Environment Variables
```bash
# Provider credentials
E2B_API_KEY=your_e2b_key
DAYTONA_API_KEY=your_daytona_key
MORPH_API_KEY=your_morph_key
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret

# Local provider settings
LOCAL_WORKING_DIR=/tmp/grainchain

# Dashboard settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=3000
```

## 🏗️ Architecture Details

### Service Layer
- `GrainchainService`: Main service for all Grainchain operations
- Async/await pattern for non-blocking operations
- Connection pooling and session management
- Error handling and logging

### State Management
- `DashboardState`: Reactive state with Reflex
- Real-time updates across all components
- Persistent state across page navigation
- Automatic cleanup and resource management

### UI Components
- Modular component architecture
- Consistent design system
- Responsive layout
- Dark theme optimized for development

## 🔒 Security

### Credential Management
- Environment variable based configuration
- No hardcoded secrets
- Secure credential storage
- Input validation and sanitization

### Sandbox Security
- Isolated execution environments
- Resource limits and timeouts
- Path validation for file operations
- Command sanitization

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=grainchain_dashboard tests/
```

## 📊 Monitoring

### Built-in Metrics
- Active sandbox count
- Total sandboxes created
- Commands executed
- Snapshot count
- Provider status

### Logging
- Structured logging with levels
- Provider-specific logs
- Error tracking and reporting
- Performance monitoring

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t grainchain-dashboard .
docker run -p 3000:3000 grainchain-dashboard
```

### Production Considerations
- Use environment variables for configuration
- Set up proper logging and monitoring
- Configure resource limits
- Enable HTTPS in production
- Set up backup for snapshots

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting guide
- Review provider documentation
- Open an issue on GitHub
- Contact the development team

---

**Built with ❤️ using Grainchain and Reflex**
