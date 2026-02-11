import os

def update_embedding_model():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the target model from config.py
    target_model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # Check for existing entry
    if "EMBEDDING_MODEL_NAME=" in content:
        # Simplistic replace line logic
        new_lines = []
        for line in content.splitlines():
            if line.startswith("EMBEDDING_MODEL_NAME="):
                new_lines.append(f"EMBEDDING_MODEL_NAME={target_model}")
                print(f"🔧 Updated existing EMBEDDING_MODEL_NAME to {target_model}")
            else:
                new_lines.append(line)
        new_content = "\n".join(new_lines) + "\n"
    else:
        # Append
        new_content = content + f"\nEMBEDDING_MODEL_NAME={target_model}\n"
        print(f"➕ Added EMBEDDING_MODEL_NAME={target_model}")

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ .env file updated with correct embedding model.")

if __name__ == "__main__":
    update_embedding_model()
