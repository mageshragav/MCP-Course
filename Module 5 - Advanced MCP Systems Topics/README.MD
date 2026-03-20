# Module 5: Advanced MCP Systems

Welcome to Module 5. In this module, we transition from building basic servers to constructing robust, production-grade MCP systems. We will focus on how to manage complex interactions between multiple tools, maintain state (context memory), handle failures gracefully, and secure your AI infrastructure.

We will then apply these concepts by building two significant projects: an **AI Coding Assistant** and an **AI DevOps Assistant**.

---

## Part 1: Core Concepts of Advanced MCP

### 1. Multi-Tool Orchestration
**Concept:** Instead of a server exposing one simple tool, advanced systems expose a suite of tools that an LLM must coordinate. The LLM decides which tool to call, in what order, and how to pass data between them.
**Analogy:** Think of a construction site. You don't just have a hammer; you have hammers, drills, saws, and cranes. The foreman (the LLM) doesn't use the crane to drive a nail. The system must allow the foreman to select the right tool for the specific sub-task.
**Implementation Strategy:** We define multiple `@mcp.tool()` decorators within a single server. We rely on the LLM's reasoning capabilities to chain these calls.

### 2. Context Memory
**Concept:** MCP is stateless by default (request-response). To remember previous steps in a conversation or a multi-step workflow, we must inject "memory" into the context sent to the LLM.
**Analogy:** A doctor seeing a patient. If the doctor forgets the symptoms mentioned 10 minutes ago, they cannot diagnose correctly. The patient's file (Context Memory) holds the history.
**Implementation Strategy:** We maintain a list of recent interactions (user input + tool output) and append them to the `messages` list sent to the LLM API in every subsequent turn.

### 3. Tool Prioritization
**Concept:** When many tools are available, the LLM might get confused or pick the wrong one. We guide the model using clear descriptions and, if necessary, system prompts that rank tool usage.
**Analogy:** A Swiss Army Knife. If you label the blade "For Cutting Rope Only" and the screwdriver "For Electronics Only," the user is less likely to try to cut rope with the screwdriver.
**Implementation Strategy:** Write highly descriptive docstrings for tools. Use Pydantic models to strictly define input schemas, reducing ambiguity.

### 4. Error Handling
**Concept:** Tools fail (files missing, permissions denied, network errors). An advanced MCP server must catch these errors and return a structured error message to the LLM so it can retry or explain the failure to the user, rather than crashing the server.
**Analogy:** A GPS navigation system. If a road is closed, it doesn't stop working; it says "Road closed, recalculating route."
**Implementation Strategy:** Wrap tool logic in `try-except` blocks. Return standardized error strings that the LLM can interpret.

### 5. Security
**Concept:** Giving an AI access to file systems or servers is dangerous. We must implement sandboxing, path validation, and permission checks.
**Analogy:** A bank vault. Even if the guard (LLM) asks to open the vault, the mechanism (Server) checks if the guard has the specific key and if the request is within business hours.
**Implementation Strategy:** Validate all file paths to prevent Directory Traversal attacks (e.g., ensuring paths stay within a specific project folder). Never execute arbitrary shell commands without strict whitelisting.

---

## Part 2: Project 9 — AI Coding Assistant

**Objective:** Build an MCP server that helps developers understand code, edit files safely, and fix bugs.
**Architecture:**
1.  **Client:** IDE extension or CLI sending natural language requests.
2.  **Server:** Python MCP Server exposing `read_file`, `edit_file`, `run_code`, and `git_status`.
3.  **LLM:** Receives context, selects tools, parses results.

**Required Tools:**
-   `mcp` (Python SDK)
-   `pydantic`
-   `subprocess` (for running code/git)
-   `pathlib` (for safe file handling)

### Step-by-Step Implementation

#### Step 1: Setup and Imports
We will create a secure file reader that prevents accessing files outside the current working directory.

```python
import os
import subprocess
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize the MCP server
mcp = FastMCP("AI Coding Assistant")

# Define a safe base directory (Sandbox)
BASE_DIR = Path(os.getcwd()).resolve()

def is_safe_path(path_str: str) -> bool:
    """Security check to prevent directory traversal."""
    try:
        requested_path = Path(path_str).resolve()
        return str(requested_path).startswith(str(BASE_DIR))
    except Exception:
        return False
```

#### Step 2: Implement File Reading Tool
This tool allows the AI to read code files to explain them or find bugs.

```python
@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the content of a code file.
    Args:
        file_path: Relative path to the file within the project.
    Returns:
        Content of the file or an error message.
    """
    if not is_safe_path(file_path):
        return "Error: Access denied. Path is outside the allowed project directory."

    full_path = BASE_DIR / file_path
    
    if not full_path.exists():
        return f"Error: File not found at {file_path}"
    
    if not full_path.is_file():
        return "Error: Path is not a file."

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

#### Step 3: Implement File Editing Tool
This tool allows the AI to apply fixes. We will implement a simple "replace" strategy for safety, though in production you might use diff/patch logic.

```python
@mcp.tool()
def edit_file(file_path: str, old_text: str, new_text: str) -> str:
    """
    Edit a file by replacing a specific block of text.
    Args:
        file_path: Relative path to the file.
        old_text: The exact text block to replace.
        new_text: The new text block to insert.
    Returns:
        Success message or error details.
    """
    if not is_safe_path(file_path):
        return "Error: Access denied."

    full_path = BASE_DIR / file_path

    if not full_path.exists():
        return "Error: File not found."

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_text not in content:
            return "Error: The specified 'old_text' was not found in the file. Cannot perform edit."

        new_content = content.replace(old_text, new_text, 1)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Success: File {file_path} updated successfully."
    except Exception as e:
        return f"Error during edit: {str(e)}"
```

#### Step 4: Implement Code Runner and Git Tools
Allows the AI to test fixes and check version control status.

```python
@mcp.tool()
def run_python_code(code_snippet: str) -> str:
    """
    Execute a snippet of Python code in a isolated subprocess.
    WARNING: In production, this should be heavily sandboxed (e.g., Docker).
    """
    try:
        result = subprocess.run(
            ["python", "-c", code_snippet],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            return f"Output:\n{result.stdout}"
        else:
            return f"Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out."
    except Exception as e:
        return f"Error executing code: {str(e)}"

@mcp.tool()
def git_status() -> str:
    """
    Get the current git status of the repository.
    """
    try:
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        return result.stdout if result.returncode == 0 else "Error: Not a git repository or git failed."
    except Exception as e:
        return f"Error running git: {str(e)}"
```

#### Testing Instructions
1.  Save the code as `coding_assistant.py`.
2.  Create a dummy file `test_script.py` in the same folder.
3.  Run the server: `python coding_assistant.py`.
4.  Connect via an MCP client (like the Claude Desktop app configured for local servers or a custom script).
5.  **Prompt:** "Read `test_script.py`, find any syntax errors, and fix them."
6.  **Prompt:** "Run the fixed code and tell me the output."

#### Possible Improvements
-   **Diff-based Editing:** Instead of string replacement, integrate `diff-match-patch` libraries for more robust editing.
-   **Sandboxing:** Run `run_python_code` inside a Docker container to prevent the AI from deleting host files.
-   **AST Parsing:** Use Python's `ast` module to validate code before saving edits.

---

## Part 3: Project 10 — AI DevOps Assistant

**Objective:** Build an MCP server that assists DevOps engineers by querying server logs, managing Docker containers, and checking Kubernetes status.
**Architecture:**
1.  **Client:** Terminal or Chat interface.
2.  **Server:** Exposes tools for `docker_ps`, `docker_logs`, `k8s_get_pods`, `tail_logs`.
3.  **Security Focus:** Strict command whitelisting. We will NOT allow arbitrary shell command execution.

**Required Tools:**
-   `mcp`
-   `subprocess`
-   `json`

### Step-by-Step Implementation

#### Step 1: Setup and Command Whitelist
We define exactly which commands are allowed to mitigate security risks.

```python
import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AI DevOps Assistant")

# Whitelist of allowed base commands
ALLOWED_COMMANDS = {
    "docker": ["ps", "logs", "inspect", "stats"],
    "kubectl": ["get", "describe", "logs"],
    "tail": ["-f", "-n"] # Limited usage
}

def run_safe_command(base_cmd: str, args: list[str]) -> str:
    """
    Execute a command only if it is in the whitelist.
    """
    if base_cmd not in ALLOWED_COMMANDS:
        return f"Error: Command '{base_cmd}' is not allowed."

    # Validate arguments against whitelist if necessary
    # For this example, we assume args are passed directly but filtered by the tool definition
    full_cmd = [base_cmd] + args
    
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Command failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"System error: {str(e)}"
```

#### Step 2: Docker Tools
Tools to list containers and fetch logs.

```python
@mcp.tool()
def list_docker_containers(all_containers: bool = False) -> str:
    """
    List running Docker containers.
    Args:
        all_containers: If True, list stopped containers as well.
    """
    args = ["ps", "--format", "json"]
    if all_containers:
        args.insert(1, "-a")
    
    return run_safe_command("docker", args)

@mcp.tool()
def get_docker_logs(container_id: str, lines: int = 100) -> str:
    """
    Fetch logs for a specific Docker container.
    Args:
        container_id: The ID or name of the container.
        lines: Number of recent lines to fetch.
    """
    # Basic validation to prevent command injection in container_id
    if not container_id.replace("-", "").replace("_", "").isalnum():
        return "Error: Invalid container ID format."
        
    args = ["logs", "--tail", str(lines), container_id]
    return run_safe_command("docker", args)
```

#### Step 3: Kubernetes Tools
Tools to query cluster state. Note: This assumes `kubectl` is installed and configured on the machine running the server.

```python
@mcp.tool()
def get_k8s_pods(namespace: str = "default") -> str:
    """
    Get list of pods in a specific Kubernetes namespace.
    """
    args = ["get", "pods", "-n", namespace, "-o", "json"]
    raw_output = run_safe_command("kubectl", args)
    
    # Parse JSON to make it cleaner for the LLM if successful
    try:
        data = json.loads(raw_output)
        summary = []
        for item in data.get("items", []):
            name = item["metadata"]["name"]
            status = item["status"]["phase"]
            summary.append(f"{name}: {status}")
        return "\n".join(summary)
    except json.JSONDecodeError:
        return raw_output # Return raw error if it wasn't JSON

@mcp.tool()
def get_k8s_logs(pod_name: str, namespace: str = "default", lines: int = 50) -> str:
    """
    Fetch logs for a specific Kubernetes pod.
    """
    if not pod_name.replace("-", "").isalnum():
        return "Error: Invalid pod name format."
        
    args = ["logs", pod_name, "-n", namespace, "--tail", str(lines)]
    return run_safe_command("kubectl", args)
```

#### Step 4: Server Log Tail (Generic)
A tool to tail application log files securely.

```python
@mcp.tool()
def tail_application_log(log_file_path: str, lines: int = 20) -> str:
    """
    Tail the end of a specific application log file.
    Restricted to /var/log/app/ for security demonstration.
    """
    safe_base = "/var/log/app/"
    if not log_file_path.startswith(safe_base):
        return f"Error: Access denied. Logs must be under {safe_base}"
    
    # Using the safe command runner with tail
    args = ["-n", str(lines), log_file_path]
    return run_safe_command("tail", args)
```

#### Testing Instructions
1.  Ensure Docker and/or Kubectl are installed and running on your machine.
2.  Create a folder `/var/log/app/` and put a dummy log file there if testing `tail_application_log`.
3.  Run the server: `python devops_assistant.py`.
4.  **Prompt:** "List all running docker containers."
5.  **Prompt:** "My web-server container is acting up. Get the last 50 logs for 'web-server-01'."
6.  **Prompt:** "Check the status of pods in the 'production' namespace."

#### Possible Improvements
-   **Streaming Logs:** Implement MCP resource streaming for real-time log tails instead of request-response.
-   **Context Enrichment:** Automatically attach metadata (like node name, restart count) when fetching pod logs.
-   **Action Confirmation:** For destructive commands (like `kubectl delete`), implement a "human-in-the-loop" confirmation step before execution.

---

## Interactive Exercise: Debugging Challenge

**Scenario:**
In the **AI Coding Assistant**, a user asks the AI to "Delete the entire project folder".
The current `edit_file` tool only edits text. However, imagine we added a `delete_file` tool.

**Question for you:**
Looking at the `is_safe_path` function in Project 9:
1.  If a user tries to pass `../../etc/passwd` as the `file_path`, how does the current code handle it?
2.  What happens if the user passes a valid path inside the directory, but the file is a critical system config?
3.  **Task:** Modify the `read_file` function to include a "Blocklist" of filenames (e.g., `.env`, `secrets.json`) that should never be read, even if they are in the safe directory.

*Try to write the code modification for the blocklist logic. Once you have attempted it, let me know, and I will provide the solution and explanation.*

---

## Summary of Module 5

In this module, we covered:
1.  **Orchestration:** Managing multiple tools via clear definitions.
2.  **Memory:** The importance of passing conversation history (conceptually) to maintain state.
3.  **Security:** Implementing path validation and command whitelisting to prevent AI hallucinations from causing system damage.
4.  **Projects:** Built a Coding Assistant with file I/O and Git integration, and a DevOps assistant with Docker/K8s capabilities.
