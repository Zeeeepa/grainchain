# Grainchain Dashboard

**Professional sandbox management interface for modern development workflows**

## 🚀 Overview

Grainchain Dashboard is a comprehensive web application for managing sandbox environments, providers, files, snapshots, and terminal operations. Built with Reflex (Python) and featuring a modern, responsive UI.

## ✨ Features

### 🏠 **Dashboard Overview**
- Real-time statistics and metrics
- Quick action buttons for common tasks
- System status monitoring
- Activity overview

### 🔌 **Provider Management**
- Support for 5 sandbox providers (Local, E2B, Daytona, Morph, Modal)
- Secure API key management with encryption
- Real-time provider status monitoring
- Interactive configuration modals

### 💻 **Interactive Terminal**
- Execute commands in sandbox environments
- Command history with persistence
- Real-time output display
- Professional terminal interface

### 📁 **File Management**
- Browse, upload, and download files
- Directory navigation
- File operations (create, delete, edit)
- Search and filtering capabilities

### 📸 **Snapshot Management**
- Create and restore sandbox snapshots
- Snapshot metadata and versioning
- Import/export functionality
- Progress tracking

### ⚙️ **Settings & Configuration**
- Theme preferences (Light/Dark)
- Provider defaults
- Notification settings
- Advanced configuration options

## 🛠️ Technology Stack

- **Frontend**: Reflex (Python-based React)
- **Backend**: Python with SQLAlchemy
- **Database**: SQLite (configurable)
- **Security**: Cryptography for API key encryption
- **UI**: Modern component-based design system

## 📁 Project Structure

```
grainchain_dashboard/
├── src/                    # Source code
│   ├── main.py            # Main application entry point
│   ├── state.py           # Application state management
│   ├── components/        # UI components
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── docs/                 # Documentation
│   ├── user-guide/       # User documentation
│   ├── developer-guide/  # Developer documentation
│   ├── api/              # API documentation
│   └── deployment/       # Deployment guides
├── config/               # Configuration files
└── scripts/              # Utility scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd grainchain_dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   cd src
   reflex run
   ```

4. **Access the dashboard**
   Open your browser to `http://localhost:3000`

## 📚 Documentation

- **[User Guide](user-guide/)** - End-user documentation
- **[Developer Guide](developer-guide/)** - Development setup and architecture
- **[API Documentation](api/)** - API reference and integration guides
- **[Deployment Guide](deployment/)** - Production deployment instructions

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/
```

## 🔧 Development

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run in development mode**
   ```bash
   cd src
   reflex run --dev
   ```

3. **Run tests with coverage**
   ```bash
   python -m pytest tests/ --cov=src/
   ```

### Code Quality

- **Linting**: `flake8 src/`
- **Type checking**: `mypy src/`
- **Formatting**: `black src/`

## 🚀 Deployment

See the [Deployment Guide](deployment/) for detailed production deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics and reporting
- [ ] Plugin system for custom providers
- [ ] Mobile-responsive improvements
- [ ] API rate limiting and monitoring

---

**Built with ❤️ by the Grainchain Team**
