# Module 1 — Python Foundations for MCP

Welcome to your MCP development journey! This module builds the essential Python foundation you'll need for all MCP work ahead.

---

## 📚 Learning Pattern: Learn → Implement → Explain → Record

---

## Part 1: Python Environment Setup

### Key Concepts

| Concept             | Simple Explanation        | Real-World Analogy                                      |
| ------------------- | ------------------------- | ------------------------------------------------------- |
| Virtual Environment | Isolated Python workspace | Like having separate workbenches for different projects |
| Package Manager     | Tool to install libraries | Like an app store for Python code                       |
| Dependencies        | Libraries your code needs | Like ingredients for a recipe                           |

### Step-by-Step Implementation

## ✅ Summary: Key `uv` Commands for MCP Development

| Task                 | Command                                             |
| -------------------- | --------------------------------------------------- |
| Install uv           | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Create venv          | `uv venv`                                         |
| Activate venv        | `source .venv/bin/activate`                       |
| Install packages     | `uv pip install <package>`                        |
| Install from file    | `uv pip install -r requirements.txt`              |
| Sync environment     | `uv pip sync requirements.txt`                    |
| List packages        | `uv pip list`                                     |
| Run without activate | `uv run python script.py`                         |
| Create project       | `uv init <project_name>`                          |
| Add dependency       | `uv add <package>`                                |
| Add dev dependency   | `uv add --dev <package>`                          |

---

## 1.1 `uv` Project Management (Modern Approach)

```python
# setup_uv_project.py - Modern uv project setup
import subprocess
import sys

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
```

---

## 1.2 `pyproject.toml` (uv Project Configuration)

```toml
# pyproject.toml
[project]
name = "mcp_project"
version = "0.1.0"
description = "MCP Development Project"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "httpx>=0.25.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
# uv specific configuration
dev-dependencies = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

---

## 1.3 Quick Start Commands with `uv`

```bash
# ============== INSTALL UV ==============
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# ============== VERIFY INSTALLATION ==============
uv --version

# ============== CREATE VIRTUAL ENVIRONMENT ==============
uv venv mcp_env

# ============== ACTIVATE ENVIRONMENT ==============
# Windows
mcp_env\Scripts\activate

# Mac/Linux
source mcp_env/bin/activate

# ============== INSTALL DEPENDENCIES ==============
# From requirements.txt
uv pip install -r requirements.txt

# Or individual packages
uv pip install fastapi uvicorn httpx pydantic

# ============== SYNC ENVIRONMENT ==============
uv pip sync requirements.txt

# ============== RUN PYTHON SCRIPT ==============
# Without activating environment
uv run python project1_ai_cli_assistant.py

# ============== CHECK INSTALLED PACKAGES ==============
uv pip list

# ============== UPDATE ALL PACKAGES ==============
uv pip install --upgrade --all

# ============== EXPORT REQUIREMENTS ==============
uv pip freeze > requirements.txt
```

---

## 1.4 Updated Project 1 with `uv` Structure

```bash
# Recommended Project Structure with uv
mcp_project/
├── .venv/                 # uv virtual environment
├── src/
│   └── mcp_project/
│       ├── __init__.py
│       ├── cli.py
│       ├── llm_client.py
│       └── config.py
├── tests/
│   └── test_cli.py
├── .env                   # Environment variables
├── .gitignore
├── pyproject.toml         # uv project config
├── requirements.txt       # Dependencies
└── README.md
```

---

## 1.7 `.gitignore` for uv Projects

```gitignore
# .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# uv / Virtual Environment
.venv/
venv/
ENV/
env/
.uv/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
```

---

## 1.5 Why `uv` is Better Than `pip`

| Feature                         | pip                  | uv                      |
| ------------------------------- | -------------------- | ----------------------- |
| **Speed**                 | Slow                 | 10-100x faster          |
| **Written in**            | Python               | Rust                    |
| **Dependency Resolution** | Can be slow          | Very fast               |
| **Virtual Env Creation**  | `python -m venv`   | `uv venv`             |
| **Project Management**    | Manual               | `uv init`, `uv add` |
| **Lock File**             | No (needs pip-tools) | Yes (`uv.lock`)       |
| **Python Version Mgmt**   | No                   | Yes (`uv python`)     |

---

## 1.6 Complete Setup Script (One-Command)

```python
# quickstart.py - One command setup with uv
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
```

---

## ✅ Summary: Key `uv` Commands for MCP Development

| Task                 | Command                                             |
| -------------------- | --------------------------------------------------- |
| Install uv           | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Create venv          | `uv venv`                                         |
| Activate venv        | `source .venv/bin/activate`                       |
| Install packages     | `uv pip install <package>`                        |
| Install from file    | `uv pip install -r requirements.txt`              |
| Sync environment     | `uv pip sync requirements.txt`                    |
| List packages        | `uv pip list`                                     |
| Run without activate | `uv run python script.py`                         |
| Create project       | `uv init <project_name>`                          |
| Add dependency       | `uv add <package>`                                |
| Add dev dependency   | `uv add --dev <package>`                          |

---

## Part 2: Async Programming (asyncio)

### Key Concepts

Here’s a clear explanation of **synchronous (sync)**, **asynchronous (async)**, **async context managers**, and **async generators** in Python, with examples and use cases:

---

### 1. **Synchronous (Sync) Code**

- **Definition**: Code that runs sequentially, blocking the execution of the next line until the current operation completes.
- **Example**:
  ```python
  def fetch_data():
      print("Fetching data...")
      return "Data"

  data = fetch_data()
  print(data)
  ```
- **Use Case**: Simple scripts, CPU-bound tasks, or when you don’t need concurrency.

---

### 2. **Asynchronous (Async) Code**

- **Definition**: Code that allows non-blocking execution using `async`/`await`. It enables concurrency for I/O-bound tasks (e.g., network requests, file I/O).
- **Example**:
  ```python
  import asyncio

  async def fetch_data():
      print("Fetching data...")
      await asyncio.sleep(2)  # Simulate I/O delay
      return "Data"

  async def main():
      data = await fetch_data()
      print(data)

  asyncio.run(main())
  ```
- **Key Points**:
  - Use `async def` to define an async function.
  - Use `await` to pause execution until the async operation completes.
  - Run async code with `asyncio.run()`.

---

### 3. **Async Context Managers**

- **Definition**: Context managers (`with` blocks) for async resources (e.g., database connections, file handles).
- **Example**:
  ```python
  class AsyncConnection:
      async def __aenter__(self):
          print("Connecting...")
          await asyncio.sleep(1)
          return self

      async def __aexit__(self, exc_type, exc, tb):
          print("Disconnecting...")
          await asyncio.sleep(1)

  async def main():
      async with AsyncConnection() as conn:
          print("Using connection...")

  asyncio.run(main())
  ```
- **Key Points**:
  - Use `async with` to manage async resources.
  - Define `__aenter__` and `__aexit__` methods for async setup/teardown.

---

### 4. **Async Generators**

- **Definition**: Generators that yield values asynchronously, useful for streaming data (e.g., reading large files, paginated APIs).
- **Example**:
  ```python
  async def async_counter(limit):
      for i in range(limit):
          await asyncio.sleep(1)
          yield i

  async def main():
      async for num in async_counter(3):
          print(num)

  asyncio.run(main())
  ```
- **Key Points**:
  - Use `async for` to iterate over async generators.
  - Define async generators with `async def` and `yield`.

---

### **When to Use What?**

| Feature                         | Use Case                                        |
| ------------------------------- | ----------------------------------------------- |
| **Sync**                  | Simple scripts, CPU-bound tasks                 |
| **Async**                 | I/O-bound tasks (e.g., APIs, databases)         |
| **Async Context Manager** | Managing async resources (e.g., DB connections) |
| **Async Generator**       | Streaming data asynchronously                   |

---

```python
# asyncio_fundamentals.py - Async Programming Basics
import asyncio
import time

# ============== SYNCHRONOUS (Blocking) ==============
def sync_fetch_data(id, delay):
    """Synchronous - blocks execution"""
    print(f"⏳ Sync: Starting task {id}")
    time.sleep(delay)  # BLOCKS everything
    print(f"✅ Sync: Task {id} complete")
    return f"Data-{id}"

# ============== ASYNCHRONOUS (Non-Blocking) ==============
async def async_fetch_data(id, delay):
    """Asynchronous - allows other tasks to run"""
    print(f"⏳ Async: Starting task {id}")
    await asyncio.sleep(delay)  # NON-BLOCKING
    print(f"✅ Async: Task {id} complete")
    return f"Data-{id}"

# ============== RUNNING ASYNC CODE ==============
async def main():
    """Main async function"""
    # Run tasks sequentially
    result1 = await async_fetch_data(1, 1)
    result2 = await async_fetch_data(2, 1)
  
    # Run tasks concurrently (MCP uses this!)
    results = await asyncio.gather(
        async_fetch_data(3, 1),
        async_fetch_data(4, 1),
        async_fetch_data(5, 1)
    )
    return results

# ============== ASYNC CONTEXT MANAGERS ==============
class AsyncConnection:
    """Async context manager for connections"""
    async def __enter__(self):
        print("🔌 Connecting...")
        await asyncio.sleep(0.5)
        return self
  
    async def __exit__(self, exc_type, exc_val, exc_tb):
        print("🔌 Disconnecting...")
        await asyncio.sleep(0.5)

async def use_connection():
    async with AsyncConnection() as conn:
        print("📡 Using connection...")

# ============== ASYNC GENERATORS ==============
async def async_data_stream():
    """Stream data asynchronously"""
    for i in range(5):
        await asyncio.sleep(0.5)
        yield f"Chunk-{i}"

async def consume_stream():
    async for chunk in async_data_stream():
        print(f"📥 Received: {chunk}")

if __name__ == "__main__":
    print("=" * 50)
    print("ASYNCIO FUNDAMENTALS DEMO")
    print("=" * 50)
  
    print("\n1️⃣ Sequential Async Tasks:")
    asyncio.run(main())
  
    print("\n2️⃣ Async Context Manager:")
    asyncio.run(use_connection())
  
    print("\n3️⃣ Async Generator:")
    asyncio.run(consume_stream())
```

### Output Example:

```
==================================================
ASYNCIO FUNDAMENTALS DEMO
==================================================

1️⃣ Sequential Async Tasks:
⏳ Async: Starting task 1
✅ Async: Task 1 complete
⏳ Async: Starting task 2
✅ Async: Task 2 complete
⏳ Async: Starting task 3
⏳ Async: Starting task 4
⏳ Async: Starting task 5
✅ Async: Task 3 complete
✅ Async: Task 4 complete
✅ Async: Task 5 complete
```

---

## Part 3: JSON and Data Serialization

### Key Concepts

| Concept       | Purpose                 | MCP Relevance         |
| ------------- | ----------------------- | --------------------- |
| JSON          | Data exchange format    | MCP messages are JSON |
| Pydantic      | Data validation         | MCP tool schemas      |
| Serialization | Convert objects to JSON | API communication     |

### Implementation

```python
# json_serialization.py - JSON Handling for MCP
import json
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============== PYDANTIC MODELS (MCP Style) ==============
class MCPToolRequest(BaseModel):
    """Standard MCP tool request structure"""
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default={}, description="Tool parameters")
    request_id: str = Field(default_factory=lambda: f"req_{datetime.now().timestamp()}")

class MCPToolResponse(BaseModel):
    """Standard MCP tool response structure"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    request_id: str

class MCPMessage(BaseModel):
    """Complete MCP message structure"""
    method: str
    params: Dict[str, Any]
    id: str
    jsonrpc: str = "2.0"

# ============== SERIALIZATION FUNCTIONS ==============
def serialize_to_json(obj: BaseModel) -> str:
    """Convert Pydantic model to JSON string"""
    return obj.model_dump_json(indent=2)

def deserialize_from_json(json_str: str, model_class: type[BaseModel]) -> BaseModel:
    """Convert JSON string to Pydantic model"""
    return model_class.model_validate_json(json_str)

def validate_mcp_message(data: Dict) -> MCPMessage:
    """Validate incoming MCP message"""
    try:
        return MCPMessage(**data)
    except Exception as e:
        raise ValueError(f"Invalid MCP message: {str(e)}")

# ============== USAGE EXAMPLES ==============
def demo_serialization():
    print("=" * 50)
    print("JSON SERIALIZATION DEMO")
    print("=" * 50)
  
    # Create request
    request = MCPToolRequest(
        tool_name="search_database",
        parameters={"query": "users", "limit": 10}
    )
  
    # Serialize
    json_str = serialize_to_json(request)
    print("\n📤 Serialized JSON:")
    print(json_str)
  
    # Deserialize
    restored = deserialize_from_json(json_str, MCPToolRequest)
    print(f"\n📥 Deserialized: {restored.tool_name}")
  
    # Create response
    response = MCPToolResponse(
        success=True,
        data={"results": ["user1", "user2"]},
        request_id=request.request_id
    )
    print(f"\n✅ Response: {serialize_to_json(response)}")

if __name__ == "__main__":
    demo_serialization()
```

---

## Part 4: API Requests (httpx)

### Key Concepts

```python
# api_requests.py - HTTP Client for MCP
import httpx
import asyncio
from typing import Optional, Dict, Any

# ============== SYNC CLIENT ==============
class SyncAPIClient:
    """Synchronous HTTP client"""
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
  
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
  
    def post(self, endpoint: str, data: Dict) -> Dict:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

# ============== ASYNC CLIENT (PREFERRED for MCP) ==============
class AsyncAPIClient:
    """Asynchronous HTTP client - MCP Standard"""
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._client: Optional[httpx.AsyncClient] = None
  
    async def __aenter__(self):
        self._client = httpx.AsyncClient(headers=self.headers)
        return self
  
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
  
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        response = await self._client.get(
            f"{self.base_url}/{endpoint}", 
            params=params
        )
        response.raise_for_status()
        return response.json()
  
    async def post(self, endpoint: str, data: Dict) -> Dict:
        response = await self._client.post(
            f"{self.base_url}/{endpoint}", 
            json=data
        )
        response.raise_for_status()
        return response.json()
  
    async def stream(self, endpoint: str, data: Dict):
        """Stream response for long-running tasks"""
        async with self._client.stream(
            "POST", 
            f"{self.base_url}/{endpoint}",
            json=data
        ) as response:
            async for line in response.aiter_lines():
                yield line

# ============== LLM API CLIENT (OpenAI Style) ==============
class LLMClient:
    """LLM API Client for AI interactions"""
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.base_url = base_url
        self.api_key = api_key
  
    async def chat_completion(
        self, 
        messages: List[Dict], 
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

# ============== USAGE EXAMPLE ==============
async def demo_api_client():
    print("=" * 50)
    print("API CLIENT DEMO")
    print("=" * 50)
  
    # Example with mock endpoint
    async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
        # GET request
        posts = await client.get("posts", params={"_limit": 2})
        print(f"\n📥 Retrieved {len(posts)} posts")
  
        # POST request
        new_post = await client.post("posts", data={
            "title": "MCP Test",
            "body": "Testing API",
            "userId": 1
        })
        print(f"✅ Created post ID: {new_post.get('id')}")

if __name__ == "__main__":
    asyncio.run(demo_api_client())
```

---

## Part 5: CLI Tools with Python (Click)

```python
# cli_tool.py - CLI Foundation for MCP
# reference link : https://click.palletsprojects.com/en/stable/
import click
import asyncio
from typing import Optional

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """MCP CLI Assistant - Foundation Tool"""
    pass

@cli.command()
@click.option("--name", default="World", help="Name to greet")
def greet(name: str):
    """Simple greeting command"""
    click.echo(f"👋 Hello, {name}!")

@cli.command()
@click.option("--prompt", required=True, help="Your prompt for the LLM")
@click.option("--model", default="gpt-3.5-turbo", help="LLM model to use")
def ask(prompt: str, model: str):
    """Send prompt to LLM (Project 1 preview)"""
    click.echo(f"🤔 Processing: {prompt}")
    click.echo(f"📡 Model: {model}")
    # In Project 1, we'll add actual API call here
    click.echo("✅ Response will appear here after API integration")

@cli.command()
def config():
    """Show current configuration"""
    config = {
        "api_key": "********",
        "model": "gpt-3.5-turbo",
        "timeout": 30
    }
    click.echo("⚙️  Configuration:")
    for key, value in config.items():
        click.echo(f"   {key}: {value}")

@cli.command()
@click.argument("task")
def run(task: str):
    """Run a task through MCP"""
    click.echo(f"🚀 Running task: {task}")
    # Async task execution
    asyncio.run(execute_task(task))

async def execute_task(task: str):
    await asyncio.sleep(1)
    click.echo(f"✅ Task '{task}' completed")

if __name__ == "__main__":
    cli()
```

### CLI Usage:

```bash
# Run the CLI
python cli_tool.py --help

# Greet command
python cli_tool.py greet --name "MCP Developer"

# Ask command (Project 1 preview)
python cli_tool.py ask --prompt "What is MCP?"

# Show config
python cli_tool.py config

# Run task
python cli_tool.py run "analyze_data"
```

---

## 🎯 PROJECT 1 — AI CLI Assistant

### Project Objective

Build a CLI tool that sends prompts to an LLM and displays responses.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AI CLI Assistant                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Click     │───▶│   httpx     │───▶│  OpenAI     │ │
│  │    CLI      │    │   Client    │    │    API      │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   User      │    │   Request   │    │   LLM       │ │
│  │   Input     │    │   Builder   │    │  Response   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Required Tools

| Tool          | Purpose       | Installation                  |
| ------------- | ------------- | ----------------------------- |
| Python 3.10+  | Runtime       | `python --version`          |
| click         | CLI framework | `pip install click`         |
| httpx         | HTTP client   | `pip install httpx`         |
| python-dotenv | Env variables | `pip install python-dotenv` |

### Step-by-Step Coding Instructions

```python
# project1_ai_cli_assistant.py - Complete Implementation
import click
import asyncio
import httpx
import os
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

# Load environment variables
load_dotenv()

# ============== CONFIGURATION ==============
class Config:
    """Centralized configuration"""
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    TIMEOUT: int = 30
    MAX_TOKENS: int = 1000

# ============== LLM CLIENT ==============
class LLMClient:
    """Async LLM API Client"""
  
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.BASE_URL
  
    async def send_prompt(
        self, 
        prompt: str, 
        model: str = Config.DEFAULT_MODEL,
        temperature: float = 0.7
    ) -> str:
        """Send prompt to LLM and get response"""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful AI assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": Config.MAX_TOKENS
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                raise Exception(f"API Error: {str(e)}")
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

# ============== CLI COMMANDS ==============
@click.group()
@click.version_option(version="1.0.0", prog_name="ai-cli")
def cli():
    """🤖 AI CLI Assistant - Your LLM Command Line Tool"""
    pass

@cli.command()
@click.option("--prompt", "-p", required=True, help="Your prompt for the AI")
@click.option("--model", "-m", default=Config.DEFAULT_MODEL, help="LLM model")
@click.option("--temperature", "-t", default=0.7, help="Temperature (0-1)")
@click.option("--output", "-o", default=None, help="Save response to file")
def ask(prompt: str, model: str, temperature: float, output: Optional[str]):
    """Send a prompt to the AI and get response"""
  
    # Validate API key
    if not Config.API_KEY:
        click.echo("❌ Error: OPENAI_API_KEY not set!")
        click.echo("💡 Set it: export OPENAI_API_KEY='your-key'")
        return
  
    click.echo(f"🤔 Processing your prompt...")
    click.echo(f"📡 Model: {model}")
    click.echo(f"🌡️  Temperature: {temperature}")
    click.echo("-" * 50)
  
    async def get_response():
        client = LLMClient(Config.API_KEY)
        return await client.send_prompt(prompt, model, temperature)
  
    try:
        # Show spinner while waiting
        with click.progressbar(length=100, label="Thinking", show_eta=False) as bar:
            async def fetch():
                response = await get_response()
                bar.update(100)
                return response
      
            response = asyncio.run(fetch())
  
        # Display response
        click.echo("\n" + "=" * 50)
        click.echo(click.style("🤖 AI Response:", fg="green", bold=True))
        click.echo("=" * 50)
        click.echo(response)
        click.echo("=" * 50)
  
        # Save to file if requested
        if output:
            with open(output, "w") as f:
                f.write(f"# AI Response - {datetime.now()}\n\n{response}")
            click.echo(f"💾 Response saved to: {output}")
  
        # Save to history
        save_to_history(prompt, response)
  
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))

@cli.command()
def history():
    """Show conversation history"""
    history_file = ".ai_cli_history.json"
    if os.path.exists(history_file):
        import json
        with open(history_file, "r") as f:
            history = json.load(f)
        click.echo(f"\n📜 History ({len(history)} entries):")
        for i, entry in enumerate(history[-5:], 1):  # Show last 5
            click.echo(f"\n{i}. {entry['timestamp']}")
            click.echo(f"   Q: {entry['prompt'][:50]}...")
            click.echo(f"   A: {entry['response'][:50]}...")
    else:
        click.echo("📭 No history found")

@cli.command()
def config():
    """Show current configuration"""
    click.echo("\n⚙️  Configuration:")
    click.echo(f"   API Key: {'********' if Config.API_KEY else 'NOT SET'}")
    click.echo(f"   Base URL: {Config.BASE_URL}")
    click.echo(f"   Default Model: {Config.DEFAULT_MODEL}")
    click.echo(f"   Timeout: {Config.TIMEOUT}s")
    click.echo(f"   Max Tokens: {Config.MAX_TOKENS}")

# ============== HELPER FUNCTIONS ==============
def save_to_history(prompt: str, response: str):
    """Save conversation to history file"""
    import json
    history_file = ".ai_cli_history.json"
  
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
  
    history.append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response
    })
  
    # Keep last 100 entries
    history = history[-100:]
  
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

# ============== ENTRY POINT ==============
if __name__ == "__main__":
    cli()
```

### Environment Setup

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
```

### Testing Instructions

```bash
# 1. Install dependencies
pip install click httpx python-dotenv

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Test basic command
python project1_ai_cli_assistant.py --help

# 4. Ask a question
python project1_ai_cli_assistant.py ask --prompt "What is Model Context Protocol?"

# 5. Save response to file
python project1_ai_cli_assistant.py ask -p "Explain asyncio" -o response.txt

# 6. View history
python project1_ai_cli_assistant.py history

# 7. Check config
python project1_ai_cli_assistant.py config
```

### Possible Improvements

| Improvement                | Difficulty | Description                     |
| -------------------------- | ---------- | ------------------------------- |
| Add streaming responses    | Medium     | Show tokens as they arrive      |
| Add conversation memory    | Medium     | Maintain context across prompts |
| Add multiple LLM providers | Easy       | Support Anthropic, Google, etc. |
| Add voice input/output     | Hard       | Speech-to-text integration      |
| Add plugin system          | Hard       | Extend with custom tools        |

---

## 🧪 Coding Exercise

```python
# exercise_1.py - Test Your Understanding
import asyncio
import httpx

# EXERCISE 1: Fix this async function
async def fetch_url(url: str) -> str:
    # TODO: Use httpx.AsyncClient to fetch URL
    # Return the response text
    pass

# EXERCISE 2: Create a Pydantic model
# TODO: Create a model called 'ToolCall' with fields:
# - tool_name (str)
# - parameters (dict)
# - timestamp (str)

# EXERCISE 3: Create a CLI command
# TODO: Add a new click command called 'status' that shows:
# - Current time
# - API key status (set or not)
# - Python version

print("Complete these exercises before moving to Module 2!")
```

---

## 📝 Module 1 Summary

| Topic                | Key Takeaway         | MCP Relevance                    |
| -------------------- | -------------------- | -------------------------------- |
| Virtual Environments | Isolate dependencies | Each MCP project needs clean env |
| Async/Await          | Non-blocking I/O     | MCP servers are async            |
| Pydantic             | Data validation      | MCP schemas use Pydantic         |
| httpx                | Async HTTP client    | LLM API calls                    |
| Click                | CLI framework        | MCP CLI tools                    |

---

## ⚠️ Common Mistakes to Avoid

```python
# ❌ WRONG: Blocking in async code
async def bad_example():
    time.sleep(1)  # BLOCKS everything!

# ✅ CORRECT: Non-blocking
async def good_example():
    await asyncio.sleep(1)  # Allows other tasks

# ❌ WRONG: No error handling
response = await client.get(url)

# ✅ CORRECT: With error handling
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.HTTPError as e:
    print(f"Request failed: {e}")
```

---

## 🎯 Interview Preparation Tips

| Question                | Answer Key Points                      |
| ----------------------- | -------------------------------------- |
| Why async for MCP?      | Non-blocking, handles multiple clients |
| Pydantic vs dict?       | Validation, type safety, auto-docs     |
| httpx vs requests?      | Async support, better performance      |
| Virtual env importance? | Dependency isolation, reproducibility  |

---
