# AgentAI - AI-Powered Development Platform

An intelligent development platform that uses AI agents to analyze requirements, generate code, run tests, and create documentation automatically.

## Features

- **AI Requirements Analysis**: Automated analysis of project requirements with technology stack recommendations
- **Human Approval Workflow**: Review and approve AI recommendations before development begins
- **Automated Code Generation**: AI-powered code generation using CrewAI and Ollama
- **Iterative Testing**: Automated test generation and issue detection with iterative fixes
- **Documentation Generation**: Comprehensive project documentation creation
- **Web Dashboard**: Real-time kanban board showing project progress
- **Project Management**: Complete project lifecycle management with file organization

## Architecture

- **Frontend**: FastAPI web application with real-time dashboard
- **Backend**: CrewAI agents powered by Ollama LLM
- **AI Engine**: Local Ollama with Llama 3.1 8B model
- **Storage**: JSON-based persistence with organized project folders

## Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed and running
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AgentAICoder.git
cd AgentAICoder
```

2. Install Ollama model:
```bash
ollama pull llama3.1:8b
```

3. Start the platform:
```bash
./start.sh
```

4. Open http://localhost:8000 in your browser

## Usage

1. **Create Project**: Define requirements, features, and constraints
2. **AI Analysis**: AI analyzes and recommends technology stack
3. **Human Review**: Approve, reject, or request rework of AI recommendations
4. **Development**: AI generates code, tests, and documentation
5. **Project Delivery**: Complete project with organized file structure

## Project Structure

```
AgentAICoder/
├── web/                    # Web interface
│   ├── app.py             # FastAPI application
│   ├── static/            # CSS, JS assets
│   └── data/              # JSON persistence
├── coding-crew/           # AI agent system
│   ├── agents/            # CrewAI agent definitions
│   ├── utils/             # Utilities and file management
│   └── main.py            # Backend services
├── generated_projects/    # AI-generated project outputs
└── start.sh              # Startup script
```

## Configuration

- **Ollama Model**: Configure in `coding-crew/config.py`
- **Delays**: Adjust AI processing delays in config
- **Workflow**: Customize phases and progress tracking

## Development

The platform uses:
- **CrewAI**: Multi-agent AI framework
- **Ollama**: Local LLM inference
- **FastAPI**: Modern web framework
- **UV**: Fast Python package management

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## Support

For issues and questions, please open a GitHub issue.