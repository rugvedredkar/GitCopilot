import requests
import subprocess
import json
import re
import sys

SAFE_COMMANDS = ["git", "gh"]

def run_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen3:4b", "prompt": prompt},
            stream=True,
        )
        full_output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        full_output += data["response"]
                except json.JSONDecodeError:
                    pass
        return full_output.strip()
    except Exception as e:
        print("Error talking to Ollama:", e)
        return None


def sanitize_command(cmd):
    """Clean up Ollama output to ensure valid git commands only."""
    cmd = cmd.splitlines()[0].strip()  # Take only first line
    cmd = re.sub(r"[`\*#>]", "", cmd)  # Remove markdown or symbols
    cmd = cmd.replace("–", "--")  # Replace long dashes
    cmd = cmd.replace("—", "--")

    # Replace common hallucinations
    if "git merge -y" in cmd:
        cmd = "git commit -am \"auto commit\""

    # Ensure no unsafe commands
    return cmd


def is_safe_command(command):
    if not any(command.startswith(prefix + " ") for prefix in ["git", "gh"]):
        return False

    allowed_chain = "&& git push"
    if "&&" in command and allowed_chain not in command:
        return False

    unsafe_patterns = [
        "rm", "sudo", ">", ";", "|", "shutdown", "reboot", "format", "merge -y"
    ]
    return not any(pat in command for pat in unsafe_patterns)


def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip() or "main"
    except Exception:
        return "main"


def main():
    print("GitCopilot Secure Assistant (Ollama + Qwen3:4b)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        prompt = f"""
You are an expert Git assistant.
Translate the user request into ONE valid git or gh CLI command.
Output ONLY the command, nothing else.
Do not invent flags or add explanations.

Example:
User: create new branch feature-login
Output: git checkout -b feature-login

User: {user_input}
Output:
"""

        command = run_ollama(prompt)
        if not command:
            print("No response from Ollama. Is it running?")
            continue

        command = sanitize_command(command)
        print("AI →", command)

        if is_safe_command(command):
            # Auto-confirm only for commits
            auto_confirm = command.startswith("git commit")

            if not auto_confirm:
                sys.stdout.flush()
                confirm = input("Run this command? (y/n): ").strip().lower()
            else:
                confirm = "y"

            if confirm == "y":
                try:
                    result = subprocess.run(command, shell=True)
                    if result.returncode == 0:
                        print("Command executed successfully.")
                        if command.startswith("git commit"):
                            current_branch = get_current_branch()
                            print(f"Pushing to branch '{current_branch}'...")
                            subprocess.run(f"git push origin {current_branch}", shell=True)
                    else:
                        print("Command failed to execute.")
                except Exception as e:
                    print("Error running command:", e)
            elif confirm == "n":
                print("Skipped by user.")
            else:
                print("Invalid response. Type 'y' or 'n'.")
        else:
            print("Unsafe or invalid command blocked.")


if __name__ == "__main__":
    main()
