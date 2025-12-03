# 🚀 GitCopilot PRO

> Natural Language Git Assistant powered by Local AI

Transform your git workflow with natural language commands. No more memorizing complex git syntax—just tell GitCopilot what you want to do!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Required-orange.svg)

## ✨ Features

- 🗣️ **Natural Language Interface** - Use plain English instead of git commands
- 🤖 **AI-Powered** - Runs locally with Ollama (Llama 3.2)
- 📚 **Smart Dataset** - 24+ built-in command patterns for better accuracy
- 🔄 **Multi-Repository Support** - Easily switch between your GitHub repos
- 🔐 **Safety First** - Validates and confirms commands before execution
- ⚡ **Auto-Push** - Automatically offers to push after commits
- 📦 **GitHub Integration** - List, clone, and manage your repositories

## 🎬 Demo

```bash
💬 You: commit all files with message fix login bug
🤖 Thinking...
✨ Command: git commit -am "fix login bug"
Execute? (y/n): y
⚙️  Executing...
✅ Success!
📤 Push to 'main'? (y/n): y
✅ Pushed!
```

## 📋 Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai) installed and running
- [GitHub CLI](https://cli.github.com/) (optional, for multi-repo features)

## 🛠️ Installation

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com)

### 2. Pull the AI Model

```bash
ollama pull llama3.2:latest
```

### 3. Install GitHub CLI (Optional)

**macOS:**
```bash
brew install gh
gh auth login
```

**Linux:**
```bash
sudo apt install gh
gh auth login
```

**Windows:**
```bash
winget install GitHub.cli
gh auth login
```

### 4. Clone and Run GitCopilot

```bash
git clone https://github.com/yourusername/gitcopilot.git
cd gitcopilot
python3 copilot.py
```

## 🎯 Usage

### Basic Commands

```bash
# Commit changes
commit all files with message added new feature

# Create a branch
create new branch feature-auth

# Push code
push my code with message updated docs

# Check status
show git status

# View commit history
show recent commits
```

### Multi-Repository Commands

```bash
# List your GitHub repositories
!repos

# Clone a repository
!clone my-awesome-project

# Switch to different repository
!switch /path/to/another/repo

# Show current repository
!current

# View command dataset
!dataset

# Show help
!help
```

### Special Commands

| Command | Description |
|---------|-------------|
| `!repos` | List all your GitHub repositories |
| `!clone <name>` | Clone a repository from GitHub |
| `!switch <path>` | Switch to a different local repository |
| `!current` | Show current repository information |
| `!dataset` | Display all available command patterns |
| `!help` | Show help and available commands |
| `exit` or `quit` | Exit GitCopilot |

## 📚 Command Examples

### Commits
- "commit all files with message fixed bug"
- "save changes with message updated readme"
- "push my code with message new feature"

### Branches
- "create new branch feature-login"
- "switch to main branch"
- "delete branch old-feature"
- "list all branches"

### Pull/Push/Fetch
- "push to remote"
- "pull latest changes"
- "fetch from origin"

### History & Status
- "show git status"
- "show recent commits"
- "show git log"
- "show differences"

### Stash
- "stash my changes"
- "apply stashed changes"

## 🔧 Configuration

GitCopilot stores configuration in `~/.gitcopilot_config.json`:

```json
{
  "current_repo": "/path/to/current/repo",
  "repos": {
    "my-project": "/path/to/my-project",
    "another-project": "/path/to/another-project"
  }
}
```

Cloned repositories are stored in `~/gitcopilot_repos/`

## 🛡️ Safety Features

- **Command Validation** - Blocks unsafe operations (rm, sudo, force flags)
- **User Confirmation** - Always asks before executing commands
- **No Compound Commands** - Prevents chaining with `&&` or `;`
- **Quote Balance Check** - Ensures proper syntax
- **Branch Protection** - Shows current branch before pushing

## 🎨 Customization

### Add Your Own Command Patterns

Edit the `COMMAND_DATASET` in `copilot.py`:

```python
COMMAND_DATASET = [
    {"input": "your custom pattern", "output": "git command", "category": "custom"},
    # Add more patterns here
]
```

### Change AI Model

Update the model in the `ask_ollama()` function:

```python
"model": "llama3.2:latest",  # Change to your preferred model
```

Available models:
- `llama3.2:latest` (Recommended)
- `llama3.2:1b` (Faster, smaller)
- `qwen2.5:3b` (Alternative)
- `codellama` (Code-focused)

## 🐛 Troubleshooting

### Ollama Not Responding
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Test the model
ollama run llama3.2:latest "Hello"
```

### GitHub CLI Not Working
```bash
# Re-authenticate
gh auth login

# Check authentication
gh auth status
```

### Command Not Generated Correctly
- Try rephrasing your request
- Use simpler language
- Check `!dataset` for supported patterns

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions
- Add more command patterns to the dataset
- Support for other AI models
- GUI interface
- Git conflict resolution assistance
- Advanced git operations (rebase, cherry-pick)
- Multi-language support

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - For local AI inference
- [GitHub CLI](https://cli.github.com/) - For GitHub integration
- [Llama 3.2](https://ai.meta.com/llama/) - For the powerful language model

## 📧 Contact

Created by [@rugvedredkar](https://github.com/rugvedredkar)

- GitHub: [rugvedredkar](https://github.com/rugvedredkar)
- Email: rugvedredkar02@gmail.com

## ⭐ Star History

If you find GitCopilot useful, please give it a star! ⭐

---