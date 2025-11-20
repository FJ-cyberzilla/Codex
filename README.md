# Codex 
### Enterprise Code Quality Gate

<div align="center">


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-6.1.1-pink.svg)](https://github.com/FJ-cyberzilla/codex)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)](https://github.com/FJ-cyberzilla/codex/actions)[![Codex Quality Gate](https://github.com/FJ-cyberzilla/codex/actions/workflows/codex-ci.yml/badge.svg)](https://github.com/FJ-cyberzilla/codex/actions/workflows/codex-ci.yml)

**The Ultimate Production-Ready Code Quality Tool**  
Thread-Safe | Auto-Fix | Multi-Language | CI/CD Ready

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [CI/CD](#-cicd-integration)

</div>

---

## 🚀 Features

- ✅ **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Rust, C/C++
- 🔧 **Auto-Fix Mode**: Automatically fixes code style issues
- 🧵 **Thread-Safe**: Concurrent file processing with proper locking
- 📊 **Detailed Reports**: JSON exports and interactive terminal output
- 📈 **History Tracking**: Compare quality trends over time
- 🔄 **Rollback Safety**: Automatic backup/restore on fix failures
- 🎯 **Quality Gate**: CI/CD integration with exit codes
- 🎨 **Interactive Menu**: User-friendly CLI interface
- ⚙️ **Configurable**: Flexible JSON configuration system
- 🚀 **Zero Dependencies**: Uses only Python standard library (linters optional)

---

## 📦 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/FJ-cyberzilla/codex.git
cd codex

# Make executable
chmod +x codex.py

# Run interactive mode
python codex.py --interactive
```

### Install Linters (Optional)

#### Python
```bash
pip install -r requirements.txt
```

#### JavaScript/TypeScript
```bash
npm install -g eslint prettier
```

#### Go
```bash
# Install golangci-lint
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin
```

#### Rust
```bash
rustup component add clippy
```

---

## 🎮 Usage

### Interactive Mode (Recommended)

```bash
python codex.py --interactive
```

**Menu Options:**
- `[1]` Analyze Code (Check Only)
- `[2]` Analyze & Auto-Fix Issues
- `[3]` View Analysis History
- `[4]` Cleanup Backup Files
- `[5]` Configuration Info
- `[0]` Exit

### Command Line Mode

```bash
# Analyze current directory (check only)
python codex.py .

# Analyze specific path
python codex.py /path/to/project

# Auto-fix issues
python codex.py . --fix

# Verbose output
python codex.py . --fix --verbose

# Help
python codex.py --help
```

### Exit Codes

- `0`: All files passed quality checks
- `1`: One or more files failed quality checks
- `130`: User interrupted (Ctrl+C)

---

## ⚙️ Configuration

Create a `.codexrc.json` or `codex.json` in your project root:

```json
{
  "app_settings": {
    "max_workers": 4,
    "history_file": "codex_history.json",
    "output_dir": "reports",
    "default_timeout": 30,
    "skip_dirs": ["docs", "examples", "tests/__snapshots__"]
  },
  "language_tools": {
    "python": [
      {
        "tool": "pylint",
        "command": ["pylint", "--output-format=json", "--score=n"],
        "check": true,
        "fix": false,
        "timeout": 30
      },
      {
        "tool": "black",
        "command": ["black", "-q"],
        "check": false,
        "fix": true,
        "timeout": 30
      }
    ],
    "javascript": [
      {
        "tool": "eslint",
        "command": ["eslint", "--format=json"],
        "check": true,
        "fix": false,
        "timeout": 30
      },
      {
        "tool": "prettier",
        "command": ["prettier", "--write"],
        "check": false,
        "fix": true,
        "timeout": 30
      }
    ]
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_workers` | int | 4 | Number of concurrent file processors |
| `history_file` | string | `codex_history.json` | Path to history log file |
| `output_dir` | string | `reports` | Directory for JSON reports |
| `default_timeout` | int | 30 | Tool execution timeout (seconds) |
| `skip_dirs` | array | See defaults | Directories to exclude from scanning |

**Default Skip Directories:**
`node_modules`, `venv`, `.venv`, `__pycache__`, `.git`, `build`, `dist`, `.ipynb_checkpoints`, `site-packages`

---

## 🔄 CI/CD Integration

### GitHub Actions

Create `.github/workflows/codex-ci.yml`:

```yaml
name: Codex Quality Gate

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        
    - name: Install linters
      run: |
        pip install pylint black flake8
        npm install -g eslint prettier
        
    - name: Run Codex Analysis
      run: |
        python codex.py . --verbose
        
    - name: Upload Report
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: codex-report
        path: reports/
```

### GitLab CI

```yaml
stages:
  - quality

code_quality:
  stage: quality
  image: python:3.10
  before_script:
    - pip install pylint black
    - apt-get update && apt-get install -y nodejs npm
    - npm install -g eslint prettier
  script:
    - python codex.py . --verbose
  artifacts:
    when: always
    paths:
      - reports/
  allow_failure: false
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running Codex quality check..."
python codex.py . --fix

if [ $? -ne 0 ]; then
    echo "❌ Code quality check failed! Fix issues before committing."
    exit 1
fi

echo "✅ Code quality check passed!"
exit 0
```

```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 Reports

### Terminal Output

```
╔══════════════════════════════════════════════════════════════╗
║                    FINAL REPORT                              ║
╠══════════════════════════════════════════════════════════════╣
║ STATUS   | TYPE       | FILE                  | DETAILS      ║
╠══════════════════════════════════════════════════════════════╣
║   ✓      | Python     | main.py               | OK           ║
║   ✗      | JavaScript | app.js                | 3 Err        ║
║          └─ [eslint] 'foo' is not defined                    ║
╚══════════════════════════════════════════════════════════════╝
Files: 2 | Passed: 1 | Failed: 1 | Auto-Fixed: 0
```

### JSON Export

Reports are saved to `reports/codex_report_<timestamp>.json`:

```json
[
  {
    "file_path": "main.py",
    "language": "Python",
    "success": true,
    "errors": [],
    "warnings": [],
    "was_fixed": false
  }
]
```

---

## 🛠️ Advanced Usage

### Custom Tool Configuration

Add support for new languages:

```json
{
  "language_tools": {
    "go": [
      {
        "tool": "golangci-lint",
        "command": ["golangci-lint", "run"],
        "check": true,
        "fix": false,
        "timeout": 60
      }
    ]
  }
}
```

### Cleanup Orphaned Backups

```bash
# Manual cleanup
python codex.py --interactive
# Choose option [4]

# Or via CLI
python -c "from codex import cleanup_backups; cleanup_backups('.')"
```

---

## 🐛 Troubleshooting

### "Tool not found" Warning

**Cause:** Linter not installed or not in system PATH

**Fix:**
```bash
# Python
pip install pylint black

# JavaScript
npm install -g eslint prettier
```

### Permission Denied on Backup Files

**Cause:** Previous run crashed leaving locked `.codex.bak` files

**Fix:**
```bash
find . -name "*.codex.bak" -delete
```

### Timeout Errors

**Cause:** Large files or slow tools

**Fix:** Increase timeout in config:
```json
{
  "app_settings": {
    "default_timeout": 60
  }
}
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📬 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/FJ-cyberzilla/codex/issues)
- **Discussions**: [Ask questions](https://github.com/FJ-cyberzilla/codex/discussions)
- **Email**: contact@cyberzilla.dev

---

## 🙏 Acknowledgments

Built with 🎖️ by **FJ-cyberzilla**

Special thanks to:
- Python Software Foundation
- ESLint & Prettier teams
- All open-source linter maintainers

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

[⬆ Back to Top](#-cyberzilla-codex---enterprise-code-quality-gate)

</div>
