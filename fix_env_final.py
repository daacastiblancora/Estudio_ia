import os
import re

def fix_env_final():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Detect the split parts
    url_part_1 = "https://35aba340-2010-44b3-a06a-bcc9771ee0"
    url_part_2 = "053.us-east4-0.gcp.cloud.qdrant.io"
    
    full_url = url_part_1 + url_part_2
    
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # If it's the main definition line
        if stripped.startswith("QDRANT_URL="):
            # We replace it entirely with the corrected full URL
            new_lines.append(f"QDRANT_URL={full_url}\n")
            print("🔧 Replaced QDRANT_URL line.")
        
        # If it's the orphan line (starts with 053...)
        elif stripped.startswith(url_part_2):
            # We skip this line (delete it)
            print("🗑️ Removed orphan URL part.")
            continue
            
        # Keep other lines (API keys etc)
        else:
            new_lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("✅ .env file fully repaired.")

if __name__ == "__main__":
    fix_env_final()
