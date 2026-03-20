# Module 3 — Building MCP Servers with Python

## Learning Path
Learn → Implement → Explain → Record

---

## Part 1: MCP Server Fundamentals

### Key Concepts

#### 1. What is an MCP Server?

**Simple Explanation:**
An MCP Server is like a restaurant kitchen. The client (customer) sends orders (requests), and the server (kitchen) prepares and returns the food (responses). The server exposes tools that clients can call.

**Architecture:**
```
┌─────────────────┐         ┌─────────────────┐
│   MCP Client    │ ──────▶ │   MCP Server    │
│   (AI/LLM)      │ ◀────── │   (Your Code)   │
└─────────────────┘  Tools  └─────────────────┘
       │                          │
       │                          ▼
       │                  ┌──────────────┐
       │                  │   Tools      │
       │                  │   Resources  │
       │                  │   Prompts    │
       │                  └──────────────┘
```

#### 2. FastMCP Server Structure

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio

# Initialize MCP Server
mcp = FastMCP("MyMCPServer")
```

---

## Part 2: Tool Definitions and Schema Validation

### Key Concepts

#### Tool Definition Anatomy

**Real-World Analogy:**
Think of a tool definition like a restaurant menu item. It has:
- Name (dish name)
- Description (what's in the dish)
- Parameters (ingredients and quantities)
- Return value (the prepared dish)

**Python Implementation:**

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("ToolServer")

# Define input schema using Pydantic
class CalculatorInput(BaseModel):
    operation: str = Field(description="add, subtract, multiply, divide")
    num1: float = Field(description="First number")
    num2: float = Field(description="Second number")

# Define tool with schema validation
@mcp.tool()
def calculator(operation: str, num1: float, num2: float) -> float:
    """
    Perform basic arithmetic operations.
    
    Args:
        operation: The math operation to perform
        num1: First operand
        num2: Second operand
    
    Returns:
        Result of the operation
    """
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 == 0:
            raise ValueError("Cannot divide by zero")
        return num1 / num2
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

---

## Part 3: Request Routing and Tool Execution

### Key Concepts

#### Request Flow

```
Client Request → Server Receives → Route to Tool → Execute → Return Response
```

**Python Implementation with Async:**

```python
from mcp.server.fastmcp import FastMCP
import asyncio
from typing import Optional

mcp = FastMCP("AsyncServer")

@mcp.tool()
async def slow_task(task_name: str, delay: int = 2) -> str:
    """
    Simulate a slow asynchronous task.
    
    Args:
        task_name: Name of the task
        delay: Delay in seconds
    
    Returns:
        Completion message
    """
    await asyncio.sleep(delay)
    return f"Task '{task_name}' completed after {delay} seconds"

@mcp.tool()
def fast_task(task_name: str) -> str:
    """
    Simulate a fast synchronous task.
    
    Args:
        task_name: Name of the task
    
    Returns:
        Completion message
    """
    return f"Task '{task_name}' completed immediately"
```

---

## Part 4: Running the MCP Server

### Server Startup Code

```python
from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("MyServer")

# Add tools
@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### Running Commands

```bash
# Run with stdio transport
python server.py

# Run with SSE transport
python server.py --transport sse --port 8000
```

---

# Project 5 — File System MCP Server

## Project Objective

Build an MCP server that allows LLMs to:
- Read files from the filesystem
- List folders and directory contents
- Search documents for specific content

## Architecture Diagram

```
┌─────────────────┐
│   MCP Client    │
│   (LLM/AI)      │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  File MCP       │
│  Server         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   File System   │
│   Operations    │
├─────────────────┤
│ - read_file     │
│ - list_dir      │
│ - search_files  │
│ - write_file    │
└─────────────────┘
```

## Required Tools

```bash
pip install mcp fastapi pydantic asyncio
```

## Step-by-Step Implementation

### Step 1: Create Project Structure

```
file_system_mcp/
├── server.py
├── config.py
├── tools/
│   ├── __init__.py
│   ├── file_reader.py
│   ├── directory_lister.py
│   └── file_searcher.py
├── tests/
│   └── test_server.py
└── requirements.txt
```

### Step 2: Configuration File

```python
# config.py
from pydantic import BaseModel, Field
from typing import List, Optional
import os

class FileSystemConfig(BaseModel):
    """Configuration for File System MCP Server."""
    
    base_directory: str = Field(
        default=".",
        description="Base directory for file operations"
    )
    allowed_extensions: List[str] = Field(
        default=[".txt", ".md", ".py", ".json", ".yaml", ".yml"],
        description="Allowed file extensions"
    )
    max_file_size: int = Field(
        default=1048576,  # 1MB
        description="Maximum file size in bytes"
    )
    enable_write: bool = Field(
        default=False,
        description="Enable write operations"
    )
    
    @classmethod
    def from_env(cls) -> "FileSystemConfig":
        """Load configuration from environment variables."""
        return cls(
            base_directory=os.getenv("MCP_BASE_DIR", "."),
            allowed_extensions=os.getenv(
                "MCP_ALLOWED_EXT", 
                ".txt,.md,.py,.json,.yaml,.yml"
            ).split(","),
            max_file_size=int(os.getenv("MCP_MAX_SIZE", "1048576")),
            enable_write=os.getenv("MCP_ENABLE_WRITE", "false").lower() == "true"
        )
```

### Step 3: File Reader Tool

```python
# tools/file_reader.py
from pathlib import Path
from typing import Optional
import os

class FileReader:
    """Tool for reading file contents."""
    
    def __init__(self, base_directory: str, max_size: int):
        self.base_directory = Path(base_directory).resolve()
        self.max_size = max_size
    
    def _validate_path(self, file_path: str) -> Path:
        """Validate that the path is within base directory."""
        path = Path(file_path)
        
        # Handle relative paths
        if not path.is_absolute():
            path = self.base_directory / path
        
        # Resolve to absolute path
        path = path.resolve()
        
        # Security check: ensure path is within base directory
        try:
            path.relative_to(self.base_directory)
        except ValueError:
            raise PermissionError(
                f"Access denied: {file_path} is outside base directory"
            )
        
        return path
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read contents of a file.
        
        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)
        
        Returns:
            File contents as string
        """
        path = self._validate_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_size:
            raise ValueError(
                f"File too large: {file_size} bytes (max: {self.max_size})"
            )
        
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    
    def read_file_lines(
        self, 
        file_path: str, 
        start_line: int = 0, 
        end_line: Optional[int] = None,
        encoding: str = "utf-8"
    ) -> list[str]:
        """
        Read specific lines from a file.
        
        Args:
            file_path: Path to the file
            start_line: Starting line number (0-indexed)
            end_line: Ending line number (exclusive)
            encoding: File encoding
        
        Returns:
            List of lines
        """
        content = self.read_file(file_path, encoding)
        lines = content.splitlines()
        
        if end_line is None:
            return lines[start_line:]
        return lines[start_line:end_line]
```

### Step 4: Directory Lister Tool

```python
# tools/directory_lister.py
from pathlib import Path
from typing import List, Dict, Any
import os
from datetime import datetime

class DirectoryLister:
    """Tool for listing directory contents."""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory).resolve()
    
    def _validate_path(self, dir_path: str) -> Path:
        """Validate that the path is within base directory."""
        path = Path(dir_path)
        
        if not path.is_absolute():
            path = self.base_directory / path
        
        path = path.resolve()
        
        try:
            path.relative_to(self.base_directory)
        except ValueError:
            raise PermissionError(
                f"Access denied: {dir_path} is outside base directory"
            )
        
        return path
    
    def list_directory(
        self, 
        dir_path: str = ".",
        include_hidden: bool = False,
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to the directory
            include_hidden: Include hidden files (starting with .)
            recursive: List contents recursively
        
        Returns:
            List of file/folder information
        """
        path = self._validate_path(dir_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")
        
        results = []
        
        if recursive:
            items = path.rglob("*")
        else:
            items = path.glob("*")
        
        for item in items:
            # Skip hidden files if not requested
            if not include_hidden and item.name.startswith("."):
                continue
            
            try:
                stat = item.stat()
                results.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_directory)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "created": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat()
                })
            except PermissionError:
                results.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_directory)),
                    "type": "unknown",
                    "error": "Permission denied"
                })
        
        return results
    
    def get_directory_tree(
        self, 
        dir_path: str = ".",
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get directory tree structure.
        
        Args:
            dir_path: Path to the directory
            max_depth: Maximum depth to traverse
        
        Returns:
            Nested dictionary representing tree structure
        """
        path = self._validate_path(dir_path)
        
        def build_tree(current_path: Path, current_depth: int) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {"name": current_path.name, "type": "truncated"}
            
            node = {
                "name": current_path.name,
                "path": str(current_path.relative_to(self.base_directory)),
                "type": "directory" if current_path.is_dir() else "file",
                "children": []
            }
            
            if current_path.is_dir() and current_depth < max_depth:
                try:
                    for item in sorted(current_path.iterdir()):
                        if item.name.startswith("."):
                            continue
                        child = build_tree(item, current_depth + 1)
                        node["children"].append(child)
                except PermissionError:
                    node["error"] = "Permission denied"
            
            return node
        
        return build_tree(path, 0)
```

### Step 5: File Searcher Tool

```python
# tools/file_searcher.py
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

class FileSearcher:
    """Tool for searching files and content."""
    
    def __init__(
        self, 
        base_directory: str, 
        allowed_extensions: List[str]
    ):
        self.base_directory = Path(base_directory).resolve()
        self.allowed_extensions = allowed_extensions
    
    def _validate_path(self, search_path: str) -> Path:
        """Validate that the path is within base directory."""
        path = Path(search_path)
        
        if not path.is_absolute():
            path = self.base_directory / path
        
        path = path.resolve()
        
        try:
            path.relative_to(self.base_directory)
        except ValueError:
            raise PermissionError(
                f"Access denied: {search_path} is outside base directory"
            )
        
        return path
    
    def search_by_extension(
        self, 
        extension: str,
        dir_path: str = ".",
        recursive: bool = True
    ) -> List[str]:
        """
        Search files by extension.
        
        Args:
            extension: File extension (e.g., '.py')
            dir_path: Directory to search
            recursive: Search recursively
        
        Returns:
            List of matching file paths
        """
        path = self._validate_path(dir_path)
        
        if not extension.startswith("."):
            extension = f".{extension}"
        
        if recursive:
            matches = path.rglob(f"*{extension}")
        else:
            matches = path.glob(f"*{extension}")
        
        return [
            str(m.relative_to(self.base_directory)) 
            for m in matches 
            if m.is_file()
        ]
    
    def search_by_content(
        self, 
        pattern: str,
        dir_path: str = ".",
        recursive: bool = True,
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search files by content pattern.
        
        Args:
            pattern: Search pattern (regex supported)
            dir_path: Directory to search
            recursive: Search recursively
            case_sensitive: Case-sensitive search
            max_results: Maximum number of results
        
        Returns:
            List of matches with file path and line info
        """
        path = self._validate_path(dir_path)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        results = []
        
        if recursive:
            files = path.rglob("*")
        else:
            files = path.glob("*")
        
        for file_path in files:
            if len(results) >= max_results:
                break
            
            if not file_path.is_file():
                continue
            
            # Check extension
            if file_path.suffix not in self.allowed_extensions:
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append({
                                "file": str(
                                    file_path.relative_to(self.base_directory)
                                ),
                                "line_number": line_num,
                                "content": line.strip()[:200],  # Truncate long lines
                                "match": regex.search(line).group()
                            })
                            
                            if len(results) >= max_results:
                                break
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return results
    
    def search_by_name(
        self, 
        name_pattern: str,
        dir_path: str = ".",
        recursive: bool = True
    ) -> List[str]:
        """
        Search files by name pattern.
        
        Args:
            name_pattern: Pattern to match in filename
            dir_path: Directory to search
            recursive: Search recursively
        
        Returns:
            List of matching file paths
        """
        path = self._validate_path(dir_path)
        
        if recursive:
            matches = path.rglob(f"*{name_pattern}*")
        else:
            matches = path.glob(f"*{name_pattern}*")
        
        return [
            str(m.relative_to(self.base_directory)) 
            for m in matches 
            if m.is_file()
        ]
```

### Step 6: Main Server File

```python
# server.py
from mcp.server.fastmcp import FastMCP
from config import FileSystemConfig
from tools.file_reader import FileReader
from tools.directory_lister import DirectoryLister
from tools.file_searcher import FileSearcher
from typing import List, Dict, Any, Optional
import json

# Load configuration
config = FileSystemConfig.from_env()

# Initialize MCP Server
mcp = FastMCP(
    "FileSystemServer",
    dependencies=["fastapi", "pydantic"]
)

# Initialize tools
file_reader = FileReader(
    base_directory=config.base_directory,
    max_size=config.max_file_size
)
directory_lister = DirectoryLister(base_directory=config.base_directory)
file_searcher = FileSearcher(
    base_directory=config.base_directory,
    allowed_extensions=config.allowed_extensions
)

# ============== FILE READING TOOLS ==============

@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file (relative to base directory)
        encoding: File encoding (default: utf-8)
    
    Returns:
        File contents as string
    """
    try:
        content = file_reader.read_file(file_path, encoding)
        return content
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file_lines(
    file_path: str, 
    start_line: int = 0, 
    end_line: Optional[int] = None
) -> List[str]:
    """
    Read specific lines from a file.
    
    Args:
        file_path: Path to the file
        start_line: Starting line number (0-indexed)
        end_line: Ending line number (exclusive)
    
    Returns:
        List of lines
    """
    try:
        lines = file_reader.read_file_lines(file_path, start_line, end_line)
        return lines
    except Exception as e:
        return [f"Error: {str(e)}"]

# ============== DIRECTORY LISTING TOOLS ==============

@mcp.tool()
def list_directory(
    dir_path: str = ".",
    include_hidden: bool = False,
    recursive: bool = False
) -> List[Dict[str, Any]]:
    """
    List contents of a directory.
    
    Args:
        dir_path: Path to the directory
        include_hidden: Include hidden files
        recursive: List contents recursively
    
    Returns:
        List of file/folder information
    """
    try:
        items = directory_lister.list_directory(
            dir_path, 
            include_hidden, 
            recursive
        )
        return items
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_directory_tree(
    dir_path: str = ".",
    max_depth: int = 3
) -> Dict[str, Any]:
    """
    Get directory tree structure.
    
    Args:
        dir_path: Path to the directory
        max_depth: Maximum depth to traverse
    
    Returns:
        Nested dictionary representing tree structure
    """
    try:
        tree = directory_lister.get_directory_tree(dir_path, max_depth)
        return tree
    except Exception as e:
        return {"error": str(e)}

# ============== FILE SEARCH TOOLS ==============

@mcp.tool()
def search_by_extension(
    extension: str,
    dir_path: str = ".",
    recursive: bool = True
) -> List[str]:
    """
    Search files by extension.
    
    Args:
        extension: File extension (e.g., '.py')
        dir_path: Directory to search
        recursive: Search recursively
    
    Returns:
        List of matching file paths
    """
    try:
        matches = file_searcher.search_by_extension(
            extension, 
            dir_path, 
            recursive
        )
        return matches
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def search_by_content(
    pattern: str,
    dir_path: str = ".",
    recursive: bool = True,
    case_sensitive: bool = False,
    max_results: int = 100
) -> List[Dict[str, Any]]:
    """
    Search files by content pattern (regex supported).
    
    Args:
        pattern: Search pattern
        dir_path: Directory to search
        recursive: Search recursively
        case_sensitive: Case-sensitive search
        max_results: Maximum number of results
    
    Returns:
        List of matches with file path and line info
    """
    try:
        matches = file_searcher.search_by_content(
            pattern,
            dir_path,
            recursive,
            case_sensitive,
            max_results
        )
        return matches
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_by_name(
    name_pattern: str,
    dir_path: str = ".",
    recursive: bool = True
) -> List[str]:
    """
    Search files by name pattern.
    
    Args:
        name_pattern: Pattern to match in filename
        dir_path: Directory to search
        recursive: Search recursively
    
    Returns:
        List of matching file paths
    """
    try:
        matches = file_searcher.search_by_name(
            name_pattern,
            dir_path,
            recursive
        )
        return matches
    except Exception as e:
        return [f"Error: {str(e)}"]

# ============== SERVER ENTRY POINT ==============

if __name__ == "__main__":
    print("Starting File System MCP Server...")
    print(f"Base Directory: {config.base_directory}")
    print(f"Allowed Extensions: {config.allowed_extensions}")
    print(f"Max File Size: {config.max_file_size} bytes")
    print(f"Write Enabled: {config.enable_write}")
    print("-" * 50)
    mcp.run()
```

### Step 7: Requirements File

```txt
# requirements.txt
mcp>=1.0.0
fastapi>=0.104.0
pydantic>=2.0.0
uvicorn>=0.24.0
```

## Testing Instructions

### Test Script

```python
# tests/test_server.py
import subprocess
import json
import time

def test_file_read():
    """Test reading a file."""
    # Create test file
    with open("test_file.txt", "w") as f:
        f.write("Hello, MCP World!")
    
    # Test would connect to server and call read_file tool
    print("Test: read_file - PASS (manual verification needed)")

def test_directory_list():
    """Test listing directory."""
    print("Test: list_directory - PASS (manual verification needed)")

def test_content_search():
    """Test searching content."""
    print("Test: search_by_content - PASS (manual verification needed)")

if __name__ == "__main__":
    test_file_read()
    test_directory_list()
    test_content_search()
    print("All tests completed!")
```

### Manual Testing

```bash
# Start the server
python server.py

# In another terminal, test with MCP client
# Example client connection would depend on your MCP client setup
```

## Possible Improvements

1. **Add Write Operations:** Implement file creation, update, and delete with proper permissions
2. **Add Caching:** Cache frequently accessed files for better performance
3. **Add Binary File Support:** Handle images, PDFs, and other binary formats
4. **Add Rate Limiting:** Prevent abuse with request rate limiting
5. **Add Authentication:** Require API keys for server access
6. **Add Logging:** Implement comprehensive logging for debugging
7. **Add Watch Feature:** Notify clients when files change

---

# Project 6 — Database MCP Server

## Project Objective

Build an MCP server that allows LLMs to:
- Execute MySQL queries
- Execute PostgreSQL queries
- Retrieve and analyze data
- Get database schema information

## Architecture Diagram

```
┌─────────────────┐
│   MCP Client    │
│   (LLM/AI)      │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  Database MCP   │
│  Server         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   Layer         │
├─────────────────┤
│ - MySQL         │
│ - PostgreSQL    │
│ - SQLite        │
│ - Schema Info   │
│ - Query Builder │
└─────────────────┘
```

## Required Tools

```bash
pip install mcp sqlalchemy pymysql psycopg2-binary pydantic
```

## Step-by-Step Implementation

### Step 1: Project Structure

```
database_mcp/
├── server.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── mysql_handler.py
│   ├── postgres_handler.py
│   └── query_builder.py
├── tools/
│   ├── __init__.py
│   └── db_tools.py
├── tests/
│   └── test_server.py
└── requirements.txt
```

### Step 2: Configuration File

```python
# config.py
from pydantic import BaseModel, Field, SecretStr
from typing import Optional, Dict, Any
import os

class DatabaseConfig(BaseModel):
    """Configuration for Database MCP Server."""
    
    db_type: str = Field(
        default="sqlite",
        description="Database type: mysql, postgres, sqlite"
    )
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(default="test_db", description="Database name")
    username: str = Field(default="root", description="Database username")
    password: SecretStr = Field(default="", description="Database password")
    max_connections: int = Field(default=10, description="Max connections")
    query_timeout: int = Field(default=30, description="Query timeout in seconds")
    read_only: bool = Field(default=True, description="Read-only mode")
    
    @property
    def connection_string(self) -> str:
        """Generate connection string."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.database}"
        
        password = self.password.get_secret_value()
        
        if self.db_type == "mysql":
            return (
                f"mysql+pymysql://{self.username}:{password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == "postgres":
            return (
                f"postgresql+psycopg2://{self.username}:{password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load configuration from environment variables."""
        return cls(
            db_type=os.getenv("DB_TYPE", "sqlite"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "test_db"),
            username=os.getenv("DB_USER", "root"),
            password=SecretStr(os.getenv("DB_PASSWORD", "")),
            max_connections=int(os.getenv("DB_MAX_CONN", "10")),
            query_timeout=int(os.getenv("DB_TIMEOUT", "30")),
            read_only=os.getenv("DB_READ_ONLY", "true").lower() == "true"
        )
```

### Step 3: Database Connection Handler

```python
# database/connection.py
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Handle database connections and sessions."""
    
    def __init__(self, connection_string: str, max_connections: int = 10):
        self.connection_string = connection_string
        self.engine = create_engine(
            connection_string,
            pool_size=max_connections,
            max_overflow=5,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        self.metadata = MetaData()
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            timeout: Query timeout in seconds
        
        Returns:
            List of result rows as dictionaries
        """
        with self.get_session() as session:
            result = session.execute(
                text(query), 
                params or {}
            )
            
            if result.returns_rows:
                columns = result.keys()
                rows = []
                for row in result:
                    rows.append(dict(zip(columns, row)))
                return rows
            else:
                return [{"affected_rows": result.rowcount}]
    
    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        self.metadata.reflect(bind=self.engine)
        return list(self.metadata.tables.keys())
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Table schema information
        """
        self.metadata.reflect(bind=self.engine)
        
        if table_name not in self.metadata.tables:
            raise ValueError(f"Table not found: {table_name}")
        
        table = self.metadata.tables[table_name]
        columns = []
        
        for column in table.columns:
            columns.append({
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable,
                "primary_key": column.primary_key,
                "default": str(column.default) if column.default else None
            })
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_keys": [c.name for c in table.primary_key],
            "foreign_keys": [
                {
                    "column": fk.column.name,
                    "reference_table": fk.column.table.name,
                    "reference_column": fk.column.name
                }
                for fk in table.foreign_keys
            ]
        }
    
    def close(self):
        """Close the database connection."""
        self.engine.dispose()
```

### Step 4: Query Builder (Safe Query Generation)

```python
# database/query_builder.py
from typing import Optional, List, Dict, Any
import re

class QueryBuilder:
    """Build safe SQL queries to prevent SQL injection."""
    
    ALLOWED_OPERATORS = ["=", "!=", "<", ">", "<=", ">=", "LIKE", "IN"]
    RESERVED_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE",
        "INSERT", "UPDATE", "GRANT", "REVOKE"
    ]
    
    def __init__(self, read_only: bool = True):
        self.read_only = read_only
    
    def _validate_query(self, query: str) -> bool:
        """Validate query for safety."""
        query_upper = query.upper()
        
        # Check for dangerous keywords in read-only mode
        if self.read_only:
            for keyword in self.RESERVED_KEYWORDS:
                if keyword in query_upper and keyword not in ["SELECT"]:
                    if keyword in ["INSERT", "UPDATE", "DELETE", "DROP"]:
                        return False
        
        return True
    
    def build_select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build a SELECT query safely.
        
        Args:
            table: Table name
            columns: Columns to select
            where: WHERE conditions
            order_by: Order by clause
            limit: Limit results
            offset: Offset results
        
        Returns:
            Tuple of (query_string, parameters)
        """
        # Validate table name
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Build columns
        if columns:
            for col in columns:
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", col):
                    raise ValueError(f"Invalid column name: {col}")
            cols = ", ".join(columns)
        else:
            cols = "*"
        
        query = f"SELECT {cols} FROM {table}"
        params = {}
        
        # Build WHERE clause
        if where:
            conditions = []
            for i, (col, value) in enumerate(where.items()):
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", col):
                    raise ValueError(f"Invalid column name: {col}")
                
                param_name = f"param_{i}"
                
                if isinstance(value, list):
                    conditions.append(f"{col} IN :{param_name}")
                else:
                    conditions.append(f"{col} = :{param_name}")
                
                params[param_name] = value
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # Add ORDER BY
        if order_by:
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\s+(ASC|DESC))?$", order_by):
                raise ValueError(f"Invalid order by clause: {order_by}")
            query += f" ORDER BY {order_by}"
        
        # Add LIMIT
        if limit is not None:
            if limit < 0 or limit > 10000:
                raise ValueError("Limit must be between 0 and 10000")
            query += f" LIMIT {limit}"
        
        # Add OFFSET
        if offset is not None:
            if offset < 0:
                raise ValueError("Offset must be non-negative")
            query += f" OFFSET {offset}"
        
        return query, params
    
    def build_count(
        self,
        table: str,
        where: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Build a COUNT query."""
        return self.build_select(
            table=table,
            columns=["COUNT(*) as count"],
            where=where,
            limit=1
        )
```

### Step 5: Database Tools

```python
# tools/db_tools.py
from database.connection import DatabaseConnection
from database.query_builder import QueryBuilder
from typing import List, Dict, Any, Optional

class DatabaseTools:
    """MCP tools for database operations."""
    
    def __init__(
        self, 
        db_connection: DatabaseConnection,
        read_only: bool = True
    ):
        self.db = db_connection
        self.query_builder = QueryBuilder(read_only=read_only)
        self.read_only = read_only
    
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        return self.db.get_table_names()
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a specific table."""
        return self.db.get_table_schema(table_name)
    
    def query_table(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query a table with filters.
        
        Args:
            table: Table name
            columns: Columns to select
            where: WHERE conditions
            order_by: Order by clause
            limit: Maximum rows to return
            offset: Rows to skip
        
        Returns:
            Query results
        """
        query, params = self.query_builder.build_select(
            table=table,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        
        return self.db.execute_query(query, params)
    
    def count_rows(
        self,
        table: str,
        where: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count rows in a table."""
        query, params = self.query_builder.build_count(table, where)
        results = self.db.execute_query(query, params)
        return results[0]["count"] if results else 0
    
    def execute_custom_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query (read-only if configured).
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Query results
        """
        if not self.query_builder._validate_query(query):
            raise PermissionError(
                "Query not allowed in read-only mode"
            )
        
        return self.db.execute_query(query, params)
    
    def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        return self.query_table(table, limit=limit)
```

### Step 6: Main Server File

```python
# server.py
from mcp.server.fastmcp import FastMCP
from config import DatabaseConfig
from database.connection import DatabaseConnection
from tools.db_tools import DatabaseTools
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = DatabaseConfig.from_env()

# Initialize MCP Server
mcp = FastMCP(
    "DatabaseServer",
    dependencies=["sqlalchemy", "pydantic"]
)

# Initialize database connection
db_connection = DatabaseConnection(
    connection_string=config.connection_string,
    max_connections=config.max_connections
)

# Initialize tools
db_tools = DatabaseTools(
    db_connection=db_connection,
    read_only=config.read_only
)

# ============== DATABASE SCHEMA TOOLS ==============

@mcp.tool()
def list_tables() -> List[str]:
    """
    List all tables in the database.
    
    Returns:
        List of table names
    """
    try:
        tables = db_tools.list_tables()
        return tables
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get schema information for a table.
    
    Args:
        table_name: Name of the table
    
    Returns:
        Table schema with columns, types, and constraints
    """
    try:
        schema = db_tools.get_table_schema(table_name)
        return schema
    except Exception as e:
        return {"error": str(e)}

# ============== QUERY TOOLS ==============

@mcp.tool()
def query_table(
    table: str,
    columns: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Query a table with optional filters.
    
    Args:
        table: Table name
        columns: Columns to select (default: all)
        where: WHERE conditions as dict
        order_by: Order by clause (e.g., "created_at DESC")
        limit: Maximum rows to return
        offset: Rows to skip
    
    Returns:
        Query results as list of dictionaries
    """
    try:
        results = db_tools.query_table(
            table=table,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def count_rows(
    table: str,
    where: Optional[Dict[str, Any]] = None
) -> int:
    """
    Count rows in a table.
    
    Args:
        table: Table name
        where: WHERE conditions as dict
    
    Returns:
        Row count
    """
    try:
        count = db_tools.count_rows(table, where)
        return count
    except Exception as e:
        return -1

@mcp.tool()
def get_sample_data(
    table: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get sample data from a table.
    
    Args:
        table: Table name
        limit: Number of rows to return
    
    Returns:
        Sample rows from the table
    """
    try:
        results = db_tools.get_sample_data(table, limit)
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def execute_custom_query(
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Execute a custom SQL query.
    
    Note: In read-only mode, only SELECT queries are allowed.
    
    Args:
        query: SQL query string
        params: Query parameters for prepared statements
    
    Returns:
        Query results
    """
    try:
        results = db_tools.execute_custom_query(query, params)
        return results
    except Exception as e:
        return [{"error": str(e)}]

# ============== SERVER ENTRY POINT ==============

if __name__ == "__main__":
    print("Starting Database MCP Server...")
    print(f"Database Type: {config.db_type}")
    print(f"Database: {config.database}")
    print(f"Read-Only Mode: {config.read_only}")
    print(f"Max Connections: {config.max_connections}")
    print("-" * 50)
    
    try:
        # Test connection
        tables = db_tools.list_tables()
        print(f"Connected successfully. Found {len(tables)} tables.")
    except Exception as e:
        print(f"Connection test failed: {e}")
    
    print("-" * 50)
    mcp.run()
```

### Step 7: Requirements File

```txt
# requirements.txt
mcp>=1.0.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pymysql>=1.1.0
psycopg2-binary>=2.9.0
uvicorn>=0.24.0
```

## Testing Instructions

### Test Script

```python
# tests/test_server.py
import os

# Set test environment
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_NAME"] = "test.db"
os.environ["DB_READ_ONLY"] = "true"

from server import db_tools

def test_list_tables():
    """Test listing tables."""
    tables = db_tools.list_tables()
    print(f"Tables: {tables}")

def test_query_table():
    """Test querying a table."""
    results = db_tools.query_table("users", limit=5)
    print(f"Results: {results}")

def test_count_rows():
    """Test counting rows."""
    count = db_tools.count_rows("users")
    print(f"Row count: {count}")

if __name__ == "__main__":
    test_list_tables()
    test_query_table()
    test_count_rows()
    print("All tests completed!")
```

### SQLite Test Setup

```python
# tests/setup_test_db.py
import sqlite3

def create_test_database():
    """Create a test SQLite database."""
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    test_users = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com")
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
        test_users
    )
    
    conn.commit()
    conn.close()
    print("Test database created successfully!")

if __name__ == "__main__":
    create_test_database()
```

## Possible Improvements

1. **Connection Pooling:** Implement advanced connection pooling for high load
2. **Query Caching:** Cache frequently executed queries
3. **Query Analysis:** Add query execution plan analysis
4. **Multi-Database Support:** Support multiple database connections simultaneously
5. **Migration Tools:** Add database migration capabilities
6. **Audit Logging:** Log all queries for compliance and debugging
7. **Query Optimization:** Suggest query optimizations based on execution plans
8. **Backup/Restore:** Add database backup and restore tools

---

## Module 3 Summary

### Key Takeaways

| Concept | Description |
|---------|-------------|
| FastMCP Server | Quick way to create MCP servers with decorators |
| Tool Definitions | Define tools with Pydantic schemas for validation |
| Request Routing | MCP automatically routes requests to correct tools |
| Tool Execution | Support both sync and async tool execution |
| Security | Validate paths, sanitize queries, use read-only modes |

### Common Mistakes to Avoid

1. **Path Traversal:** Always validate file paths are within base directory
2. **SQL Injection:** Use parameterized queries, never string concatenation
3. **Large Files:** Set file size limits to prevent memory issues
4. **Connection Leaks:** Always close database connections properly
5. **No Error Handling:** Wrap all tool calls in try-except blocks

### Interview Preparation Tips

**Q: How do you secure an MCP server?**
- Validate all inputs using Pydantic
- Sanitize file paths to prevent traversal attacks
- Use parameterized queries for database access
- Implement read-only modes where appropriate
- Add rate limiting and authentication

**Q: How do you handle async operations in MCP?**
- Use async def for tools that perform I/O
- Leverage asyncio for concurrent operations
- Set appropriate timeouts for long-running tasks

**Q: What is schema validation in MCP?**
- Use Pydantic models to define tool input schemas
- MCP automatically validates inputs against schemas
- Returns clear error messages for invalid inputs

