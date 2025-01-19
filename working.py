import subprocess

def call_ollama_llama3(prompt: str):
    try:
        # Running the Ollama command with the correct syntax
        print(f"Running Ollama with prompt: {prompt}")
        result = subprocess.run(
            ['ollama', 'run', 'llama3', prompt],  # Running the model directly with prompt as argument
            capture_output=True, text=True
        )
        
        # Check if there’s any output
        if result.returncode == 0:
            print("Success! Here's the response:")
            return result.stdout
        else:
            print("Error running Ollama:")
            return result.stderr
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage with a simple prompt
prompt = "Tell me about the weather today."
response = call_ollama_llama3(prompt)

# Print the response or error
if response:
    print("Response from Llama3:", response)
else:
    print("No response received.")
