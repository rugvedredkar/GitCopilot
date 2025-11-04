import requests
import subprocess
import json
import re

SAFE_COMMANDS = [
    "git", "gh"
]

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

def is_safe_command(command):
    # Only allow whitelisted prefixes
    if any(command.startswith(prefix + " ") for prefix in SAFE_COMMANDS):
        # Block destructive operations
        unsafe_patterns = ["rm", "sudo", ">", "&&", ";", "|", "shutdown", "reboot"]
        return not any(pat in command for pat in unsafe_patterns)
    return False

def main():
    print("GitCopilot Secure Assistant (Ollama + Qwen3:4b)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        prompt = f"""
        You are a Git and GitHub assistant.
        Convert the following request into one safe Git or gh CLI command.
        Output only the command and nothing else.

        User: {user_input}
        """

        command = run_ollama(prompt)
        if not command:
            print("No response from Ollama. Is it running?")
            continue

        print("AI →", command)

        if is_safe_command(command):
            confirm = input("Run this command? (y/n): ").lower()
            if confirm == "y":
                subprocess.run(command, shell=True)
            else:
                print("Skipped.")
        else:
            print("Unsafe or invalid command blocked.")

if __name__ == "__main__":
    main()
