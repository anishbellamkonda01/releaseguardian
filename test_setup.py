"""
Test script to verify your setup is working.
Run this with: python test_setup.py
"""

print("=" * 50)
print("ReleaseGuardian Setup Test")
print("=" * 50)

# Test 1: Python packages
print("\n1. Testing package imports...")
try:
    import streamlit
    print(f"   ✓ Streamlit {streamlit.__version__}")
except ImportError:
    print("   ✗ Streamlit NOT installed")

try:
    from google import genai
    print(f"   ✓ Google GenAI installed")
except ImportError:
    print("   ✗ Google GenAI NOT installed")

try:
    import plotly
    print(f"   ✓ Plotly {plotly.__version__}")
except ImportError:
    print("   ✗ Plotly NOT installed")

try:
    from dotenv import load_dotenv
    print(f"   ✓ python-dotenv installed")
except ImportError:
    print("   ✗ python-dotenv NOT installed")

try:
    from PIL import Image
    print(f"   ✓ Pillow installed")
except ImportError:
    print("   ✗ Pillow NOT installed")

# Test 2: API Key
print("\n2. Testing API key...")
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key and api_key != "AIzaSyDOjwa3ezFnf8138tU68gSs96aDBNMsz9c":
    print(f"   ✓ API key found (starts with {api_key[:10]}...)")
else:
    print("   ✗ API key NOT found or still placeholder")

# Test 3: Gemini connection
print("\n3. Testing Gemini connection...")
try:
    from utils.gemini_client import call_gemini
    result = call_gemini("Say hello in exactly 5 words.")
    if result:
        print(f"   ✓ Gemini responded: {result.strip()}")
    else:
        print("   ✗ Gemini returned empty response")
except Exception as e:
    print(f"   ✗ Gemini connection failed: {e}")

# Test 4: Folder structure
print("\n4. Testing folder structure...")
folders = ["agents", "data", "utils", "pages"]
for folder in folders:
    if os.path.isdir(folder):
        print(f"   ✓ {folder}/ exists")
    else:
        print(f"   ✗ {folder}/ MISSING")

files = [".env", ".gitignore", "requirements.txt"]
for f in files:
    if os.path.isfile(f):
        print(f"   ✓ {f} exists")
    else:
        print(f"   ✗ {f} MISSING")

print("\n" + "=" * 50)
print("Setup test complete!")
print("=" * 50)