import os

def switch_to_local():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("QDRANT_URL="):
            # Point to a local directory "qdrant_data"
            new_lines.append("QDRANT_URL=qdrant_data\n")
        elif line.startswith("QDRANT_API_KEY="):
            # Empty key
            new_lines.append("QDRANT_API_KEY=\n")
        else:
            new_lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("✅ Switched .env to LOCAL Qdrant mode (path: qdrant_data)")

if __name__ == "__main__":
    switch_to_local()
