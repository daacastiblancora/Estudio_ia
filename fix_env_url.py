import os

def fix_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("QDRANT_URL="):
            # Split key and value
            key, value = line.split("=", 1)
            # Remove all whitespace/newlines from value
            clean_value = "".join(value.split())
            new_lines.append(f"{key}={clean_value}\n")
            print(f"🔧 Fixed QDRANT_URL: {clean_value}")
        else:
            new_lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("✅ .env file updated")

if __name__ == "__main__":
    fix_env()
