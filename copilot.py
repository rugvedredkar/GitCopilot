import requests
import subprocess
import sys
import json
import os
from pathlib import Path

# Dataset of common git commands
COMMAND_DATASET = [
    {"input": "commit all files with message", "output": "git commit -am", "category": "commit"},
    {"input": "commit changes with message", "output": "git commit -am", "category": "commit"},
    {"input": "commit and push with message", "output": "git commit -am", "category": "commit"},
    {"input": "push my code with message", "output": "git commit -am", "category": "commit"},
    {"input": "save changes with message", "output": "git commit -am", "category": "commit"},
    {"input": "create new branch", "output": "git checkout -b", "category": "branch"},
    {"input": "switch to branch", "output": "git checkout", "category": "branch"},
    {"input": "delete branch", "output": "git branch -d", "category": "branch"},
    {"input": "push to remote", "output": "git push", "category": "push"},
    {"input": "push current branch", "output": "git push", "category": "push"},
    {"input": "pull from remote", "output": "git pull origin", "category": "pull"},
    {"input": "show status", "output": "git status", "category": "status"},
    {"input": "show git log", "output": "git log --oneline", "category": "log"},
    {"input": "show recent commits", "output": "git log -10 --oneline", "category": "log"},
    {"input": "undo last commit", "output": "git reset --soft HEAD~1", "category": "reset"},
    {"input": "show differences", "output": "git diff", "category": "diff"},
    {"input": "stage all files", "output": "git add .", "category": "add"},
    {"input": "unstage files", "output": "git reset HEAD", "category": "reset"},
    {"input": "discard changes", "output": "git checkout --", "category": "checkout"},
    {"input": "merge branch", "output": "git merge", "category": "merge"},
    {"input": "rebase branch", "output": "git rebase", "category": "rebase"},
    {"input": "stash changes", "output": "git stash", "category": "stash"},
    {"input": "apply stash", "output": "git stash pop", "category": "stash"},
    {"input": "list branches", "output": "git branch -a", "category": "branch"},
    {"input": "show remote url", "output": "git remote -v", "category": "remote"},
    {"input": "clone repository", "output": "git clone", "category": "clone"},
    {"input": "fetch from remote", "output": "git fetch origin", "category": "fetch"},
]

CONFIG_FILE = Path.home() / ".gitcopilot_config.json"
REPOS_DIR = Path.home() / "gitcopilot_repos"

def load_config():
    
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"current_repo": None, "repos": {}}

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_github_repos():
    """Get list of user's GitHub repositories using gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", "--limit", "100", "--json", "name,url"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            repos = json.loads(result.stdout)
            return repos
        return []
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def clone_repo(repo_url, repo_name):
    """Clone a repository to local workspace."""
    REPOS_DIR.mkdir(exist_ok=True)
    repo_path = REPOS_DIR / repo_name
    
    if repo_path.exists():
        print(f"Repository already exists at {repo_path}")
        return str(repo_path)
    
    print(f"Cloning {repo_name}...")
    result = subprocess.run(
        ["git", "clone", repo_url, str(repo_path)],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Cloned successfully to {repo_path}")
        return str(repo_path)
    else:
        print(f"❌ Clone failed: {result.stderr}")
        return None

def switch_repo(repo_path):
    """Switch to a different repository."""
    if not Path(repo_path).exists():
        print(f"❌ Repository not found: {repo_path}")
        return False
    
    try:
        os.chdir(repo_path)
        print(f"✅ Switched to: {repo_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to switch: {e}")
        return False

def get_current_repo_name():
    """Get current repository name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).name
        return "unknown"
    except:
        return "unknown"

def build_prompt_with_dataset(user_request):
    """Build prompt using dataset examples."""
    # Find relevant examples from dataset
    relevant_examples = []
    user_lower = user_request.lower()
    
    for item in COMMAND_DATASET:
        if any(word in user_lower for word in item["input"].split()):
            relevant_examples.append(item)
            if len(relevant_examples) >= 3:
                break
    
    # Build examples string
    examples_str = "\n".join([
        f'Request: {ex["input"]} "message"\nCommand: {ex["output"]} "message"'
        for ex in relevant_examples[:3]
    ])
    
    if not examples_str:
        examples_str = """Request: commit all with message "fix"
Command: git commit -am "fix"

Request: push my code with message "update"
Command: git commit -am "update"

Request: create branch feature-x
Command: git checkout -b feature-x"""
    
    prompt = f"""You are a git command generator. Convert the request to a valid git command.

IMPORTANT RULES:
- If user says "push" WITH a message, they want to COMMIT first, use: git commit -am "message"
- If user says "push" WITHOUT a message, use: git push
- For "commit all", ALWAYS use "git commit -am"
- Output ONLY ONE command (no && or chaining)
- Always close quotes properly

Examples:
{examples_str}

Request: {user_request}
Command:"""
    
    return prompt

def ask_ollama(user_request):
    """Get git command from Ollama using dataset."""
    prompt = build_prompt_with_dataset(user_request)
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "options": {"num_predict": 50}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            cmd = response.json().get("response", "").strip()
            cmd = cmd.split('\n')[0].strip()
            cmd = cmd.replace("```", "").strip('` ')
            if cmd.lower().startswith("command:"):
                cmd = cmd[8:].strip()
            
            # Fix unbalanced quotes
            if cmd.count('"') % 2 != 0:
                if not cmd.endswith('"'):
                    cmd += '"'
            
            # Remove compound commands (we handle push separately)
            if "&&" in cmd:
                cmd = cmd.split("&&")[0].strip()
            
            # Auto-fix commit commands
            user_lower = user_request.lower()
            if ("push" in user_lower or "commit" in user_lower or "save" in user_lower) and "message" in user_lower:
                # User wants to commit, not just push
                if "git push" in cmd and "git commit" not in cmd:
                    cmd = cmd.replace("git push origin -u", "git commit -am").replace("git push", "git commit -am")
                elif "git commit -m" in cmd and "git commit -am" not in cmd:
                    cmd = cmd.replace("git commit -m", "git commit -am")
            
            return cmd
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def is_safe(cmd):
    """Check if command is safe."""
    if not cmd or not (cmd.startswith("git ") or cmd.startswith("gh ")):
        return False
    
    # Block compound commands (we handle push separately)
    if "&&" in cmd:
        return False
    
    unsafe = ["rm", "sudo", ";", "|", "shutdown", "--force", "reset --hard"]
    return not any(bad in cmd.lower() for bad in unsafe)

def run_command(cmd):
    """Execute shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def get_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "main"
    except:
        return "main"

def show_help():
    """Show available commands."""
    print("""
Available Commands:
  - Natural language git commands (e.g., "commit all files with message test")
  - !repos          : List your GitHub repositories
  - !clone <name>   : Clone a repository from your GitHub
  - !switch <path>  : Switch to a different repository
  - !current        : Show current repository
  - !dataset        : Show command dataset
  - !help           : Show this help
  - exit/quit       : Exit the program
""")

def show_dataset():
    """Show available command patterns."""
    print("\n📚 Command Dataset:")
    categories = {}
    for item in COMMAND_DATASET:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f"  • {item['input']} → {item['output']}")
    
    for cat, commands in categories.items():
        print(f"\n{cat.upper()}:")
        for cmd in commands:
            print(cmd)
    print()

def main():
    print("=" * 60)
    print("GitCopilot PRO - Multi-Repo + Dataset Enhanced")
    print("=" * 60)
    
    config = load_config()
    
    # Set initial repo if exists
    if config.get("current_repo"):
        switch_repo(config["current_repo"])
    
    print(f"\n📁 Current repo: {get_current_repo_name()}")
    print("Type '!help' for commands or your git request\n")

    while True:
        try:
            user_input = input(f"💬 [{get_current_repo_name()}] You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Special commands
        if user_input.startswith("!"):
            cmd_parts = user_input.split(maxsplit=1)
            cmd = cmd_parts[0].lower()
            
            if cmd == "!help":
                show_help()
            elif cmd == "!dataset":
                show_dataset()
            elif cmd == "!current":
                print(f"📁 Current: {os.getcwd()}")
                print(f"📦 Repo: {get_current_repo_name()}")
            elif cmd == "!repos":
                print("🔍 Fetching your GitHub repositories...")
                repos = get_github_repos()
                if repos:
                    print(f"\n📚 Your Repositories ({len(repos)}):")
                    for idx, repo in enumerate(repos, 1):
                        print(f"  {idx}. {repo['name']}")
                else:
                    print("No repositories found or gh CLI not configured")
            elif cmd == "!clone":
                if len(cmd_parts) < 2:
                    print("Usage: !clone <repo-name>")
                else:
                    repo_name = cmd_parts[1]
                    repos = get_github_repos()
                    matching = [r for r in repos if r['name'] == repo_name]
                    if matching:
                        repo_path = clone_repo(matching[0]['url'], repo_name)
                        if repo_path:
                            config["repos"][repo_name] = repo_path
                            config["current_repo"] = repo_path
                            save_config(config)
                            switch_repo(repo_path)
                    else:
                        print(f"Repository '{repo_name}' not found")
            elif cmd == "!switch":
                if len(cmd_parts) < 2:
                    print("Usage: !switch <path>")
                else:
                    path = cmd_parts[1]
                    if switch_repo(path):
                        config["current_repo"] = path
                        save_config(config)
            else:
                print(f"Unknown command: {cmd}")
            continue

        # Regular git command processing
        print("🤖 Thinking...")
        command = ask_ollama(user_input)

        if not command:
            print("❌ Couldn't generate command. Check if Ollama is running.")
            continue

        print(f"✨ Command: {command}")

        if not is_safe(command):
            print("⚠️  Unsafe command blocked!")
            continue

        confirm = input("Execute? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("⏭️  Skipped")
            continue

        print("⚙️  Executing...")
        if run_command(command):
            print("✅ Success!")
            
            # Auto-push offer after commit
            if "git commit" in command:
                current_branch = get_branch()
                push_confirm = input(f"📤 Push to '{current_branch}'? (y/n): ").strip().lower()
                if push_confirm == 'y':
                    push_cmd = f"git push origin {current_branch}"
                    print(f"⚙️  Pushing to {current_branch}...")
                    if run_command(push_cmd):
                        print("✅ Pushed!")
                    else:
                        print("❌ Push failed")
        else:
            print("❌ Failed")


if __name__ == "__main__":
    main()