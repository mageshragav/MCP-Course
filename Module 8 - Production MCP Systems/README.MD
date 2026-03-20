# Module 8: Production MCP Systems

Welcome to the final module. We are moving from development to production. In previous modules, you learned how to build MCP servers and connect them to LLMs. Now, we will learn how to package, secure, scale, and monitor these systems so they can run reliably in a real-world environment.

We will conclude with **Project 15: Full AI Automation Platform**, which serves as your Capstone Project, integrating every concept learned so far.

---

## Part 1: Docker Deployment for MCP

### Key Concepts
*   **Containerization**: Packaging your MCP server, its dependencies, and the runtime environment into a single unit (Docker image) to ensure it runs identically on any machine.
*   **Isolation**: Keeping the MCP server's environment separate from the host system for security and stability.
*   **Port Mapping**: Exposing the MCP server's communication port (usually STDIO for local or SSE/HTTP for remote) to the host or other containers.

### Real-World Analogy
Think of Docker as a **shipping container**. Whether you put it on a truck, a train, or a ship, the contents (your code) remain exactly the same and don't get damaged by the outside environment. Without Docker, you might arrive at the destination and find your "cargo" (dependencies) missing or broken.

### Architecture Explanation
In a production MCP setup:
1.  **MCP Server Container**: Runs the Python MCP server logic.
2.  **Network**: Containers communicate via a Docker network.
3.  **Volume Mounts**: Persistent data (like SQLite DBs or logs) is mounted from the host to the container to prevent data loss when the container restarts.

### Step-by-Step Implementation Guidance
1.  Create a `Dockerfile` defining the Python environment.
2.  Create a `.dockerignore` file to exclude unnecessary files (like `__pycache__`).
3.  Use `docker-compose.yml` to orchestrate the MCP server alongside databases (PostgreSQL/Chroma) and the API backend (FastAPI).

### Code Example: Dockerizing an MCP Server

**File: `Dockerfile`**
```python
# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for building wheels)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port if using SSE transport (STDIO doesn't need exposed ports usually)
EXPOSE 8000

# Command to run the MCP server
# For STDIO, we just run the script. 
# For SSE, we might run a FastAPI wrapper.
CMD ["python", "mcp_server.py"]
```

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: production-mcp-server
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/mcp_db
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - mcp-network
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mcp_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge

volumes:
  pgdata:
```

---

## Part 2: Scaling, Logging, and Monitoring

### Key Concepts
*   **Scaling**: Running multiple instances of an MCP server behind a load balancer (for HTTP/SSE transports) or using queue-based systems for high-volume tool execution.
*   **Logging**: Capturing structured logs (JSON format) to track tool executions, errors, and latency.
*   **Monitoring**: Observing system health (CPU, Memory) and application metrics (token usage, tool failure rates).

### Real-World Analogy
*   **Scaling**: Like opening more checkout lanes in a supermarket when the line gets too long.
*   **Logging**: Like a flight recorder (black box) on an airplane; it tells you exactly what happened before a crash.
*   **Monitoring**: Like a dashboard in a car showing speed, fuel, and engine temperature.

### Architecture Explanation
*   **Logging**: Use Python's `logging` module with a JSON formatter. Send logs to stdout/stderr so Docker can capture them, or push to a centralized system like ELK (Elasticsearch, Logstash, Kibana) or Loki.
*   **Monitoring**: Integrate with Prometheus for metrics and Grafana for visualization. Track specific MCP events like `tool_call_start`, `tool_call_end`, and `error`.

### Code Example: Structured Logging in MCP

```python
import logging
import json
import sys
from datetime import datetime

# Custom JSON Formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Configure Logger
logger = logging.getLogger("mcp_production")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

def execute_tool_safely(tool_name, args):
    logger.info(f"Executing tool: {tool_name}", extra={"tool": tool_name, "args": args})
    try:
        # Simulate tool execution
        result = f"Result from {tool_name}"
        logger.info(f"Tool success: {tool_name}")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {tool_name}", exc_info=True)
        raise

# Usage
if __name__ == "__main__":
    execute_tool_safely("get_weather", {"city": "London"})
```

---

## Part 3: Security in MCP

### Key Concepts
*   **Authentication & Authorization**: Ensuring only authorized users/clients can access specific MCP tools.
*   **Input Validation**: Preventing injection attacks (SQL, Command Injection) via tool arguments.
*   **Secret Management**: Never hardcoding API keys; use environment variables or secret managers (Vault, AWS Secrets Manager).
*   **Least Privilege**: The MCP server should only have access to the specific files or databases it needs.

### Real-World Analogy
Security is like a **bank vault**.
1.  **Auth**: You need a key card (Token) to enter.
2.  **Authorization**: Even with a key card, you can only open your specific safety deposit box, not everyone else's.
3.  **Validation**: The bank checks that the items you put in the box aren't explosives (malicious input).

### Code Example: Secure Tool Execution with Pydantic Validation

```python
from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("SecureServer")

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=5, ge=1, le=50)

    @validator('query')
    def validate_query(cls, v):
        # Prevent basic SQL injection patterns
        dangerous_chars = [';', '--', 'DROP', 'DELETE']
        if any(char in v.upper() for char in dangerous_chars):
            raise ValueError("Invalid characters in query")
        return v

@mcp.tool()
def secure_search(query: str, limit: int = 5) -> str:
    # Validate input using Pydantic
    validated_data = SearchQuery(query=query, limit=limit)
    
    # Simulate secure database interaction
    api_key = os.getenv("DB_API_KEY")
    if not api_key:
        raise PermissionError("Missing API Key")
        
    return f"Searching for '{validated_data.query}' with limit {validated_data.limit}"
```

---

# Project 15: Full AI Automation Platform (Capstone)

This project combines everything: MCP Tools, AI Agents, Vector Search, Database, API Backend, and Automation Workflows.

## Project Objective
Build a unified platform where users can interact via a UI (or CLI) to perform complex tasks:
1.  **AI Coding Assistant**: Analyze and generate code snippets.
2.  **AI Research Agent**: Search internal documents (RAG) and the web.
3.  **AI Data Analyst**: Query PostgreSQL database using natural language.
4.  **Automation Workflows**: Chain these tools together to complete multi-step goals.

## Architecture Diagram Explanation
1.  **Frontend/API Layer (FastAPI)**: Receives user requests, manages session state, and orchestrates agents.
2.  **Agent Orchestrator**: Decides which MCP tools to call based on user intent.
3.  **MCP Server Cluster**:
    *   `CodeMCP`: Handles file reading/writing and linting.
    *   `DataMCP`: Connects to PostgreSQL for analytics.
    *   `KnowledgeMCP`: Connects to ChromaDB for RAG.
4.  **Data Layer**: PostgreSQL (structured data), ChromaDB (vector embeddings), Local FS (codebase).
5.  **Infrastructure**: All services containerized via Docker.

## Required Tools
*   Python 3.11+
*   FastAPI, Uvicorn
*   MCP SDK (`mcp`)
*   LangChain or LlamaIndex (for agent orchestration)
*   OpenAI API
*   PostgreSQL
*   ChromaDB
*   Docker & Docker Compose

## Step-by-Step Coding Instructions

### Step 1: Project Structure
Create the following directory structure:
```text
capstone_platform/
├── docker-compose.yml
├── .env
├── requirements.txt
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI entry point
│   │   └── agents.py        # Agent orchestration logic
│   ├── mcp_servers/
│   │   ├── code_server.py
│   │   ├── data_server.py
│   │   └── knowledge_server.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   └── utils/
│       └── vector_store.py
└── tests/
```

### Step 2: Implement MCP Servers

**File: `src/mcp_servers/data_server.py` (Database Analyst)**
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import psycopg2
import os

mcp = FastMCP("DataAnalystMCP")

class SQLQuery(BaseModel):
    query: str

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "mcp_db"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASS", "pass")
    )

@mcp.tool()
def execute_analytics_query(sql: str) -> str:
    """Execute a read-only SQL query for data analysis."""
    # Security: Force READ ONLY transaction
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return str(results)
    except Exception as e:
        return f"Error executing query: {str(e)}"
```

**File: `src/mcp_servers/knowledge_server.py` (RAG)**
```python
from mcp.server.fastmcp import FastMCP
import chromadb
from chromadb.config import Settings

mcp = FastMCP("KnowledgeMCP")

client = chromadb.Client(Settings(chroma_db_impl="chromadb.db.duckdb.DuckDB", persist_directory="./chroma_data"))
collection = client.get_or_create_collection("company_docs")

@mcp.tool()
def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """Search internal documentation using vector similarity."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    if not results['documents']:
        return "No relevant documents found."
    
    context = "\n".join([doc for sublist in results['documents'] for doc in sublist])
    return context
```

### Step 3: Build the Agent Orchestrator (FastAPI + LLM)

**File: `src/api/agents.py`**
```python
import openai
from typing import List, Dict
import json

# Mocking the MCP client connection logic for brevity
# In production, use mcp.client.session to connect to running servers

async def route_request(user_intent: str, available_tools: List[str]) -> str:
    """
    Uses LLM to decide which MCP tool to call based on intent.
    """
    system_prompt = f"""
    You are an AI Orchestrator. You have access to these MCP tools: {available_tools}.
    Analyze the user request and return a JSON object with 'tool_name' and 'arguments'.
    If no tool matches, return 'chat' response.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_intent}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

async def execute_workflow(user_query: str):
    # 1. Determine intent
    tools = ["execute_analytics_query", "search_knowledge_base", "analyze_code"]
    decision = await route_request(user_query, tools)
    
    # 2. Execute specific MCP tool (Mocking the call)
    if decision.get('tool_name') == 'execute_analytics_query':
        # Call DataMCP
        return f"Calling DataMCP with: {decision['arguments']}"
    elif decision.get('tool_name') == 'search_knowledge_base':
        # Call KnowledgeMCP
        return f"Calling KnowledgeMCP with: {decision['arguments']}"
    else:
        return f"Direct LLM Response: {decision}"
```

### Step 4: FastAPI Entry Point

**File: `src/api/main.py`**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agents import execute_workflow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Automation Platform")

class UserRequest(BaseModel):
    query: str
    user_id: str

@app.post("/automate")
async def automate_task(request: UserRequest):
    logger.info(f"Received request from user {request.user_id}: {request.query}")
    try:
        result = await execute_workflow(request.query)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 5: Docker Compose for Full Stack

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  api-gateway:
    build: 
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MCP_DATA_URL=http://data-mcp:8001
      - MCP_KNOWLEDGE_URL=http://knowledge-mcp:8002
    depends_on:
      - data-mcp
      - knowledge-mcp
    networks:
      - mcp-net

  data-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    command: ["python", "src/mcp_servers/data_server.py"]
    environment:
      - DB_HOST=db
      - DB_NAME=mcp_db
      - DB_USER=user
      - DB_PASS=pass
    networks:
      - mcp-net

  knowledge-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    command: ["python", "src/mcp_servers/knowledge_server.py"]
    volumes:
      - chroma-data:/app/chroma_data
    networks:
      - mcp-net

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mcp_db
    volumes:
      - pg-data:/var/lib/postgresql/data
    networks:
      - mcp-net

networks:
  mcp-net:

volumes:
  pg-data:
  chroma-data:
```

## Testing Instructions
1.  **Start the stack**: `docker-compose up --build`
2.  **Seed Data**: Insert sample rows into PostgreSQL and add documents to ChromaDB (write a seed script).
3.  **Test API**:
    ```bash
    curl -X POST http://localhost:8000/automate \
      -H "Content-Type: application/json" \
      -d '{"query": "What were the total sales last month?", "user_id": "test123"}'
    ```
4.  **Check Logs**: `docker-compose logs -f api-gateway` to see the orchestration flow.

## Possible Improvements
*   **Caching**: Implement Redis to cache frequent LLM responses or DB queries.
*   **Streaming**: Use Server-Sent Events (SSE) in FastAPI to stream the agent's thought process to the UI in real-time.
*   **Human-in-the-loop**: Add a step where the agent asks for human approval before executing destructive database commands.
*   **Observability**: Integrate LangSmith or Phoenix for tracing LLM calls and tool executions.

---

# Final Course Wrap-Up

## Best Practices Recap
1.  **Modular Design**: Keep MCP servers small and focused on one domain (Single Responsibility Principle).
2.  **Strict Typing**: Always use Pydantic models for tool inputs/outputs to prevent runtime errors.
3.  **Error Handling**: Never let an MCP server crash; catch exceptions and return structured error messages.
4.  **Security First**: Validate all inputs, use least privilege, and manage secrets externally.

## Common Mistakes to Avoid
*   **Hardcoding Secrets**: Putting API keys directly in the code.
*   **Blocking I/O**: Using synchronous file/network operations in async MCP servers (use `asyncio`).
*   **Overly Broad Tools**: Creating tools that do "everything" instead of specific, composable actions.
*   **Ignoring Context Limits**: Sending massive amounts of data to the LLM without summarization or RAG filtering.

## Interview Preparation Tips for AI Engineers
*   **Concept**: Be ready to explain the difference between *Function Calling* and *MCP*. (Answer: MCP is a standardized protocol for connecting AI to data/tools, whereas function calling is an LLM feature).
*   **Architecture**: Draw how you would scale an MCP system to handle 10,000 concurrent users. (Mention Load Balancers, Statelessness, Queueing).
*   **Coding**: Practice writing a Pydantic model with custom validators and an async function that interacts with a mock database.
*   **Scenario**: "How do you handle an LLM hallucinating a tool argument?" (Answer: Strict schema validation at the MCP server level rejects invalid inputs before execution).

## Recommended GitHub Project Structure
```text
my-mcp-project/
├── .github/workflows/ci.yml
├── docs/
├── src/
│   ├── servers/
│   ├── clients/
│   ├── shared/
│   └── tests/
├── docker-compose.yml
├── README.md
└── requirements.txt
```

You have now completed the journey from Python foundations to building a Production-Ready AI Automation Platform using MCP. You are equipped to design, build, and deploy sophisticated AI systems.
