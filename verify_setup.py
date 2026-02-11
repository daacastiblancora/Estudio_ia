import os

def verify():
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        return

    env_vars = {}
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return

    required_keys = [
        "QDRANT_URL", "QDRANT_API_KEY", 
        "GROQ_API_KEY"
    ]
    
    missing = []
    placeholders = []
    
    for key in required_keys:
        val = env_vars.get(key)
        if not val:
            missing.append(key)
        elif "your-" in val.lower() or "tu-" in val.lower():
            placeholders.append(key)
            
    if missing:
        print("❌ The following keys are MISSING in .env:")
        for k in missing:
            print(f"   - {k}")
    
    if placeholders:
        print("⚠️  The following keys seem to still have PLACEHOLDER values:")
        for k in placeholders:
            print(f"   - {k}")

    if not missing and not placeholders:
        print("✅ .env configuration looks correct (keys present and not default placeholders).")

if __name__ == "__main__":
    verify()
