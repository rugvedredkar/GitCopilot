import requests
import subprocess
import json

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

def main():
    print("GitHub Copilot Terminal Assistant (Ollama + Qwen3:4b)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        prompt = f"""
        You are a helpful Git assistant.
        Convert the following user request into a safe git command.
        Output only the command, nothing else.

        User: {user_input}
        """

        command = run_ollama(prompt)
        if not command:
            print("No response from Ollama. Is it running?")
            continue

        print("AI →", command)

        if command.startswith("git "):
            confirm = input("Run this command? (y/n): ").lower()
            if confirm == "y":
                subprocess.run(command, shell=True)
            else:
                print("Skipped.")
        else:
            print("Unsafe command blocked.")

if __name__ == "__main__":
    main()
