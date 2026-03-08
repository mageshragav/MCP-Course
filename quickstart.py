import subprocess
import sys
import os

def quickstart():
    """Complete one-command setup"""
    print("🚀 MCP Project Quickstart with uv")
    print("=" * 50)
  
    # Step 1: Check uv
    print("\n1️⃣  Checking uv installation...")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"   ✅ {result.stdout.strip()}")
    except FileNotFoundError:
        print("   ❌ uv not found! Installing...")
        if os.name == 'nt':
            subprocess.run(["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"])
        else:
            subprocess.run(["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"], shell=True)
  
    # Step 2: Create virtual environment
    print("\n2️⃣  Creating virtual environment...")
    subprocess.run(["uv", "venv", ".venv"])
  
    # Step 3: Install dependencies
    print("\n3️⃣  Installing dependencies...")
    if os.name == 'nt':
        uv_pip = ".venv\\Scripts\\uv"
    else:
        uv_pip = ".venv/bin/uv"
  
    subprocess.run([uv_pip, "pip", "install", "-r", "requirements.txt"])
  
    # Step 4: Verify
    print("\n4️⃣  Verifying installation...")
    subprocess.run([uv_pip, "pip", "list"])
  
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("   1. Copy .env.example to .env")
    print("   2. Add your OPENAI_API_KEY to .env")
    print("   3. Run: uv run python src/mcp_project/cli.py --help")
    print("=" * 50)

if __name__ == "__main__":
    quickstart()