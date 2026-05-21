# Smart Aid AI — Kaggle Notebook Setup
# Run each cell in order on Kaggle (GPU T4 x2 recommended)

# ════════════════════════════════════════
# CELL 1: Install dependencies
# ════════════════════════════════════════
!pip install -q streamlit sentence-transformers faiss-cpu numpy \
    transformers accelerate bitsandbytes huggingface_hub pyngrok

# ════════════════════════════════════════
# CELL 2: Set HuggingFace token (from Kaggle Secrets)
# ════════════════════════════════════════
import os
from kaggle_secrets import UserSecretsClient

secrets = UserSecretsClient()
os.environ["HF_TOKEN"] = secrets.get_secret("HF_TOKEN")

# Login to HuggingFace (needed to download Gemma 4)
from huggingface_hub import login
login(token=os.environ["HF_TOKEN"])
print("✅ Logged in to HuggingFace")

# ════════════════════════════════════════
# CELL 3: Upload your project files
# ════════════════════════════════════════
# Upload these files to Kaggle (via +Add Data or Upload):
#   - rag_engine.py
#   - smart_aid_handler.py
#   - model.py
#   - smart_aid_combined.json
#   - smart_aid_data_handler.py (optional)

# Then copy them to working directory:
import shutil, glob

PROJECT_DIR = "/kaggle/input/smart-aid-files"  # adjust to your dataset name
WORK_DIR = "/kaggle/working"

for f in glob.glob(f"{PROJECT_DIR}/*"):
    shutil.copy(f, WORK_DIR)
    print(f"Copied: {f}")

# ════════════════════════════════════════
# CELL 4: Run Streamlit via ngrok tunnel
# ════════════════════════════════════════
from pyngrok import ngrok
import subprocess, threading, time

# Set your ngrok authtoken (from https://dashboard.ngrok.com/get-started/your-authtoken)
# Add as Kaggle secret: NGROK_TOKEN
ngrok_token = secrets.get_secret("NGROK_TOKEN")
ngrok.set_auth_token(ngrok_token)

# Start Streamlit in background
proc = subprocess.Popen(
    ["streamlit", "run", f"{WORK_DIR}/model.py",
     "--server.port", "8501",
     "--server.headless", "true",
     "--server.enableCORS", "false"],
    cwd=WORK_DIR
)

time.sleep(5)  # Wait for Streamlit to start

# Open ngrok tunnel
tunnel = ngrok.connect(8501)
print("=" * 50)
print(f"🌐 Smart Aid AI is LIVE at:")
print(f"   {tunnel.public_url}")
print("=" * 50)
print("Press Kaggle's Stop button to shut down.")

# ════════════════════════════════════════
# CELL 5 (Alternative): Test without Streamlit
# ════════════════════════════════════════
# Uncomment to test just the RAG + Gemma pipeline:

# import sys
# sys.path.insert(0, WORK_DIR)
# from smart_aid_handler import generate, search
#
# query = "free food in Lahore"
# answer, results = generate(query)
# print("=== Gemma 4 Answer ===")
# print(answer)
# print(f"\n=== Source Records ({len(results)}) ===")
# for r in results:
#     print(f"  - {r['name']} ({r['city']})")
