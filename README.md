# CV-Mindcare - Privacy-First Wellness Monitor 🌱

**Local wellness monitoring using camera, microphone, and air quality sensors with AI-powered recommendations.**

[![Tests](https://img.shields.io/badge/tests-263%2F285-yellow)](https://github.com/Salman-A-Alsahli/CV-Mindcare/actions)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange)](https://github.com/Salman-A-Alsahli/CV-Mindcare/releases)

---

## ⚡ Quick Start

```bash
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Install with all features
pip install -e .[dev,ml]

# Start web dashboard
./setup-frontend.sh && ./start-dashboard.sh

# Open http://localhost:5173
```

Alternative methods:
```bash
# Desktop GUI
python launcher/main.py

# API only
uvicorn backend.app:app --reload
# Visit http://localhost:8000/docs
```

---

## ✨ Features

- 🎥 **Greenery Detection** - Camera-based nature presence monitoring
- 🎤 **Noise Analysis** - Ambient sound level tracking (dB)
- 🌬️ **Air Quality** - MQ-135 sensor for CO₂, NH₃, benzene, smoke
- 🧠 **AI Recommendations** - Personalized wellness suggestions
- 📊 **Real-Time Dashboard** - Beautiful React interface
- 🔒 **Privacy-First** - All processing stays local, zero cloud
- 🔌 **WebSocket Streaming** - Live sensor data updates
- 📈 **Advanced Analytics** - Trends, anomalies, correlations

---

## 📚 Documentation

### Getting Started
- 📖 [Quick Start Guide](docs/getting-started/quick-start.md) - 5-minute setup
- 🔧 [Installation Guide](docs/getting-started/installation.md) - Detailed instructions
- 🛠️ [Hardware Setup](docs/getting-started/hardware-setup.md) - Sensor configuration

### User Guide
- 📊 [Web Dashboard](docs/user-guide/web-dashboard.md) - Using the interface
- 🖥️ [Desktop App](docs/user-guide/desktop-app.md) - GUI launcher guide
- ⚡ [Features](docs/user-guide/features.md) - Complete feature list

### Development
- 🏗️ [Architecture](docs/development/architecture.md) - System design
- 🤝 [Contributing](docs/development/contributing.md) - How to contribute
- 🧪 [Testing](docs/development/testing.md) - Test guidelines
- 📡 [API Reference](docs/development/api-reference.md) - Complete API docs

### Deployment
- 🍓 [Raspberry Pi](docs/deployment/raspberry-pi.md) - Deploy on RPi 5
- 🐳 [Docker](docs/deployment/docker.md) - Containerized deployment
- 🚀 [Production](docs/deployment/production.md) - Production checklist

### Project
- 🎯 [Milestones](docs/project-management/milestones.md) - Roadmap
- �� [Changelog](docs/project-management/changelog.md) - Version history
- 📋 [Backlog](docs/project-management/backlog.md) - Future features

---

## 🎯 Current Status

**Version**: v0.3.0 (Consolidation Release)  
**Tests**: 263/285 passing (92.3%)  
**Features**: Camera ✅ | Microphone ✅ | Air Quality ✅  
**Next Milestone**: v1.0.0 - Production Ready

---

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI, WebSockets, SQLite
- **Frontend**: React 18, Vite, Recharts, TailwindCSS
- **Sensors**: OpenCV, SoundDevice, MQ-135 (Serial/GPIO)
- **AI/ML**: DeepFace, Transformers (optional)
- **Testing**: Pytest, 285 tests, 92.3% passing

---

## 📦 Installation Options

```bash
# Base installation
pip install -e .

# With ML features (emotion detection)
pip install -e .[ml]

# With development tools
pip install -e .[dev]

# Raspberry Pi optimized
pip install -e .[rpi]

# Everything
pip install -e .[all]
```

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](docs/development/contributing.md).

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with ❤️ for privacy-conscious wellness monitoring
- Optimized for Raspberry Pi 5
- Community-driven development

---

## 🔗 Links

- [Documentation](docs/README.md)
- [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
- [GitHub Discussions](https://github.com/Salman-A-Alsahli/CV-Mindcare/discussions)
- [Project Board](https://github.com/Salman-A-Alsahli/CV-Mindcare/projects)

---

**Made with ❤️ for your wellbeing | 100% Local | 0% Cloud**
