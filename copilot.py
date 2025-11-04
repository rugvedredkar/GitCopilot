import requests
import subprocess
import sys

def ask_ollama(user_request):
    """Get git command from Ollama."""
    prompt = f"""You are a git command generator. Convert the request to a valid git command.

Rules:
- Output ONLY the complete command
- For "commit all", ALWAYS use "git commit -am"
- Always close quotes properly

Examples:
Request: commit all files with message "fix bug"
Command: git commit -am "fix bug"

Request: commit with message "update"
Command: git commit -am "update"

Request: create branch feature-login
Command: git checkout -b feature-login

Request: push code
Command: git push

Request: {user_request}
Command:"""

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
            # Clean up response
            cmd = cmd.split('\n')[0].strip()
            cmd = cmd.replace("```", "").strip('` ')
            if cmd.lower().startswith("command:"):
                cmd = cmd[8:].strip()
            
            # Validate quotes are balanced
            if cmd.count('"') % 2 != 0:
                # Unbalanced quotes, try to fix
                if not cmd.endswith('"'):
                    cmd += '"'
            
            return cmd
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def is_safe(cmd):
    """Check if command is safe."""
    if not cmd or not (cmd.startswith("git ") or cmd.startswith("gh ")):
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


def main():
    print("=" * 50)
    print("GitCopilot - Natural Language Git Assistant")
    print("=" * 50)
    print("\nType your request or 'exit' to quit\n")

    while True:
        try:
            user_input = input("💬 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue

        print("🤖 Thinking...")
        command = ask_ollama(user_input)

        if not command:
            print("❌ Couldn't generate command. Check if Ollama is running.")
            continue

        print(f"✨ Command: {command}")

        if not is_safe(command):
            print("⚠️  Unsafe command blocked!")
            continue

        # Ask for confirmation
        confirm = input("Execute? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("⏭️  Skipped")
            continue

        # Execute command
        print("⚙️  Executing...")
        if run_command(command):
            print("✅ Success!")
            
            # Offer to push after commit
            if "git commit" in command:
                push_confirm = input(f"📤 Push to '{get_branch()}'? (y/n): ").strip().lower()
                if push_confirm == 'y':
                    if run_command(f"git push origin {get_branch()}"):
                        print("✅ Pushed!")
                    else:
                        print("❌ Push failed")
        else:
            print("❌ Failed")


if __name__ == "__main__":
    main()