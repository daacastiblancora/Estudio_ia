import os

def update_model():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace old model with new model
    old_model = "llama3-70b-8192"
    new_model = "llama-3.3-70b-versatile"
    
    if old_model in content:
        new_content = content.replace(old_model, new_model)
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Updated GROQ_MODEL_NAME to {new_model}")
    else:
        print("⚠️ Model name not found or already updated.")

if __name__ == "__main__":
    update_model()
