import shutil
import os

DB_PATH = "faiss_index"

def reset_db():
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print(f"✅ Deleted existing database: {DB_PATH}")
            print("Server restart required to re-initialize empty index.")
        except Exception as e:
            print(f"❌ Failed to delete {DB_PATH}: {e}")
            print("Try stopping the server first.")
    else:
        print(f"ℹ️ No database found at {DB_PATH}. Nothing to do.")

if __name__ == "__main__":
    confirm = input(f"Are you sure you want to DELETE the vector database at '{DB_PATH}'? (y/n): ")
    if confirm.lower() == 'y':
        reset_db()
    else:
        print("Cancelled.")
