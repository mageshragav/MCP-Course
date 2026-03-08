import subprocess
import sys
import os

def check_uv_installed():
    """Check if uv is installed"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv found: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_uv():
    """Install uv if not present"""
    print("🔧 uv not found. Installing uv...")
  
    # Cross-platform uv installation
    if os.name == 'nt':  # Windows
        subprocess.run(["powershell", "-c", 
            "irm https://astral.sh/uv/install.ps1 | iex"], check=True)
    else:  # Unix/Linux/Mac
        subprocess.run(["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"], 
                      shell=True, check=True)
  
    print("✅ uv installed successfully!")


def setup_uv_project(project_name="mcp_project"):
    """Initialize a new uv project (modern approach)"""
    print(f"🔧 Creating uv project: {project_name}")
  
    if not check_uv_installed():
        install_uv()
    # Initialize new uv project
    subprocess.run(["uv", "init", project_name], check=True)
  
    # Add dependencies
    dependencies = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "python-dotenv",
        "click"
    ]
  
    print("📦 Adding dependencies...")
    for dep in dependencies:
        subprocess.run(["uv", "add", dep], check=True)
  
    # Add dev dependencies
    dev_dependencies = [
        "pytest",
        "black",
        "ruff",
        "mypy"
    ]
  
    print("📦 Adding dev dependencies...")
    for dep in dev_dependencies:
        subprocess.run(["uv", "add", "--dev", dep], check=True)
  
    print("✅ uv project setup complete!")

if __name__ == "__main__":
    setup_uv_project()