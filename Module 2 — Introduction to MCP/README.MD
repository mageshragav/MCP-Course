# Module 2 — Introduction to MCP

## Learning Pattern: Learn → Implement → Explain → Record

---

## Part 1: Key Concepts Explained Simply

### What is MCP (Model Context Protocol)?

**Simple Definition:**
MCP is a standardized protocol that allows AI models (like LLMs) to communicate with external tools, data sources, and services in a structured way.

**Real-World Analogy:**
Think of MCP as a universal remote control for AI. Just as a universal remote can control your TV, AC, and sound system through one interface, MCP allows an AI to access calculators, databases, APIs, and files through one standardized protocol.

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐         ┌──────────────┐                │
│   │  MCP Client  │◄───────►│  MCP Server  │                │
│   │  (AI/LLM)    │         │  (Your Code) │                │
│   └──────────────┘         └──────────────┘                │
│         │                       │                           │
│         │                       │                           │
│         ▼                       ▼                           │
│   ┌──────────────┐         ┌──────────────┐                │
│   │  LLM/API     │         │   Tools      │                │
│   │  (OpenAI)    │         │   Resources  │                │
│   └──────────────┘         │   Prompts    │                │
│                            └──────────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### MCP Client vs Server

| Component | Role | Example |
|-----------|------|---------|
| **MCP Client** | Requests tools, sends prompts, receives results | AI Assistant, LLM Application |
| **MCP Server** | Exposes tools, provides resources, handles requests | Your Python Server |

### Core MCP Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **Tools** | Executable functions the AI can call | calculator, weather API, file reader |
| **Resources** | Data sources the AI can access | databases, files, APIs |
| **Prompts** | Pre-defined templates for AI interactions | "Summarize this document" |
| **Context** | Information passed between client and server | conversation history, user preferences |

---

## Part 2: Python Implementation

### Prerequisites

```bash
pip install mcp fastapi uvicorn pydantic asyncio openai
```

---

## Project 3 — Simple MCP Server

### Project Objective
Build a minimal MCP server that registers tools and handles LLM requests with JSON responses.

### Architecture Diagram

```
┌─────────────┐      HTTP/JSON      ┌─────────────┐
│  MCP Client │◄──────────────────►│  MCP Server │
│  (LLM App)  │                     │  (FastAPI)  │
└─────────────┘                     └──────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │   Tools     │
                                    │  Registry   │
                                    └─────────────┘
```

### Step-by-Step Implementation

#### Step 1: Create Project Structure

```
project_3_mcp_server/
├── server.py
├── tools.py
├── models.py
├── config.py
└── requirements.txt
```

#### Step 2: Create requirements.txt

```python
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
asyncio==3.4.3
openai==1.12.0
mcp==1.0.0
```

#### Step 3: Create models.py (Data Models)

```python
# models.py
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ToolParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameter(BaseModel):
    type: ToolParameterType
    description: str
    required: bool = False
    enum: Optional[List[Any]] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ToolParameter] = {}


class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


class MCPRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
```

#### Step 4: Create tools.py (Tool Registry)

```python
# tools.py
from typing import Any, Dict, Callable
from models import ToolDefinition, ToolParameter, ToolParameterType


class ToolRegistry:
    """Central registry for all MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, description: str, 
                 parameters: Dict[str, ToolParameter],
                 handler: Callable):
        """Register a new tool"""
        self._tools[name] = {
            "definition": ToolDefinition(
                name=name,
                description=description,
                parameters=parameters
            ),
            "handler": handler
        }
        print(f"[ToolRegistry] Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all available tools"""
        return [tool["definition"] for tool in self._tools.values()]
    
    async def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        handler = tool["handler"]
        if asyncio.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)


# Global registry instance
tool_registry = ToolRegistry()


# ============== Built-in Tools ==============

def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def get_info() -> str:
    """Get server information"""
    return "MCP Server v1.0 - Simple Implementation"


# Register built-in tools
tool_registry.register(
    name="add",
    description="Add two numbers together",
    parameters={
        "a": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="First number",
            required=True
        ),
        "b": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Second number",
            required=True
        )
    },
    handler=add
)

tool_registry.register(
    name="multiply",
    description="Multiply two numbers together",
    parameters={
        "a": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="First number",
            required=True
        ),
        "b": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Second number",
            required=True
        )
    },
    handler=multiply
)

tool_registry.register(
    name="get_info",
    description="Get server information and version",
    parameters={},
    handler=get_info
)
```

#### Step 5: Create server.py (Main MCP Server)

```python
# server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
import asyncio
import json
import uuid
from datetime import datetime

from models import (
    MCPRequest, MCPResponse, ToolRequest, ToolResponse,
    ToolDefinition, ToolParameterType
)
from tools import tool_registry


app = FastAPI(title="MCP Server", version="1.0.0")


# ============== MCP Protocol Endpoints ==============

@app.get("/")
async def root():
    """Root endpoint - server health check"""
    return {
        "status": "online",
        "server": "MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools = tool_registry.list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    name: {
                        "type": param.type.value,
                        "description": param.description,
                        "required": param.required
                    }
                    for name, param in tool.parameters.items()
                }
            }
            for tool in tools
        ]
    }


@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    try:
        result = await tool_registry.execute(
            name=request.tool_name,
            arguments=request.arguments
        )
        return ToolResponse(
            success=True,
            result=result
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            result=None,
            error=str(e)
        )


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP protocol endpoint"""
    response_id = request.id or str(uuid.uuid4())
    
    try:
        if request.method == "tools/list":
            tools = tool_registry.list_tools()
            return MCPResponse(
                id=response_id,
                result={"tools": [t.dict() for t in tools]}
            )
        
        elif request.method == "tools/call":
            if not request.params:
                raise ValueError("Missing params for tools/call")
            
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            result = await tool_registry.execute(
                name=tool_name,
                arguments=arguments
            )
            
            return MCPResponse(
                id=response_id,
                result={"content": [{"type": "text", "text": str(result)}]}
            )
        
        elif request.method == "initialize":
            return MCPResponse(
                id=response_id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "MCP Server",
                        "version": "1.0.0"
                    }
                }
            )
        
        else:
            raise ValueError(f"Unknown method: {request.method}")
    
    except Exception as e:
        return MCPResponse(
            id=response_id,
            error={
                "code": -32000,
                "message": str(e)
            }
        )


# ============== Context Management ==============

class ContextStore:
    """Simple in-memory context store"""
    
    def __init__(self):
        self._contexts: Dict[str, Dict[str, Any]] = {}
    
    def set(self, session_id: str, key: str, value: Any):
        if session_id not in self._contexts:
            self._contexts[session_id] = {}
        self._contexts[session_id][key] = value
    
    def get(self, session_id: str, key: str, default=None):
        return self._contexts.get(session_id, {}).get(key, default)
    
    def clear(self, session_id: str):
        if session_id in self._contexts:
            del self._contexts[session_id]


context_store = ContextStore()


@app.post("/context/{session_id}")
async def set_context(session_id: str, data: Dict[str, Any]):
    """Store context for a session"""
    for key, value in data.items():
        context_store.set(session_id, key, value)
    return {"status": "context stored", "session_id": session_id}


@app.get("/context/{session_id}")
async def get_context(session_id: str):
    """Retrieve context for a session"""
    context = context_store._contexts.get(session_id, {})
    return {"session_id": session_id, "context": context}


# ============== Server Startup ==============

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("MCP Server Starting...")
    print("=" * 50)
    print(f"Available tools: {[t.name for t in tool_registry.list_tools()]}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Testing Instructions

### Test 1: Server Health Check

```bash
curl http://localhost:8000/
```

**Expected Output:**
```json
{
    "status": "online",
    "server": "MCP Server",
    "version": "1.0.0",
    "timestamp": "2024-01-15T10:30:00"
}
```

### Test 2: List Available Tools

```bash
curl http://localhost:8000/tools
```

**Expected Output:**
```json
{
    "tools": [
        {
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "a": {"type": "number", "description": "First number", "required": true},
                "b": {"type": "number", "description": "Second number", "required": true}
            }
        },
        {
            "name": "multiply",
            "description": "Multiply two numbers together",
            "parameters": {...}
        },
        {
            "name": "get_info",
            "description": "Get server information and version",
            "parameters": {}
        }
    ]
}
```

### Test 3: Execute a Tool

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "add", "arguments": {"a": 5, "b": 3}}'
```

**Expected Output:**
```json
{
    "success": true,
    "result": 8,
    "error": null
}
```

### Test 4: MCP Protocol Request

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {"name": "add", "arguments": {"a": 10, "b": 20}},
    "id": "req-001"
  }'
```

---

## Project 4 — MCP Tool System

### Project Objective
Create a server that exposes multiple tools (calculator, weather, text summarizer) where the LLM selects the tool automatically.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool System                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐                                          │
│   │    LLM       │                                          │
│   │  (OpenAI)    │                                          │
│   └──────┬───────┘                                          │
│          │ Tool Selection                                   │
│          ▼                                                  │
│   ┌──────────────┐     ┌──────────────┐                    │
│   │ Tool Router  │────►│   Calculator │                    │
│   └──────┬───────┘     │   Weather    │                    │
│          │             │   Summarizer │                    │
│          ▼             └──────────────┘                    │
│   ┌──────────────┐                                          │
│   │   Response   │                                          │
│   │   Builder    │                                          │
│   └──────────────┘                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Implementation

#### Step 1: Create Advanced Tools

```python
# advanced_tools.py
import asyncio
import random
from typing import Dict, Any, List
from models import ToolParameter, ToolParameterType
from tools import tool_registry


# ============== Calculator Tools ==============

def calculator_add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


def calculator_subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b


def calculator_multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def calculator_divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculator_power(base: float, exponent: float) -> float:
    """Calculate base raised to exponent"""
    return base ** exponent


# Register calculator tools
for name, func, desc in [
    ("calc_add", calculator_add, "Add two numbers"),
    ("calc_subtract", calculator_subtract, "Subtract second number from first"),
    ("calc_multiply", calculator_multiply, "Multiply two numbers"),
    ("calc_divide", calculator_divide, "Divide first number by second"),
    ("calc_power", calculator_power, "Calculate power of a number"),
]:
    tool_registry.register(
        name=name,
        description=desc,
        parameters={
            "a": ToolParameter(
                type=ToolParameterType.NUMBER,
                description="First number",
                required=True
            ),
            "b": ToolParameter(
                type=ToolParameterType.NUMBER,
                description="Second number",
                required=True
            )
        },
        handler=func
    )


# ============== Weather Tools ==============

class WeatherData:
    """Simulated weather data"""
    
    CITIES = {
        "new york": {"temp": 22, "condition": "Sunny", "humidity": 45},
        "london": {"temp": 15, "condition": "Cloudy", "humidity": 70},
        "tokyo": {"temp": 25, "condition": "Rainy", "humidity": 80},
        "paris": {"temp": 18, "condition": "Partly Cloudy", "humidity": 55},
        "sydney": {"temp": 28, "condition": "Sunny", "humidity": 40},
    }
    
    @classmethod
    def get_weather(cls, city: str) -> Dict[str, Any]:
        city_lower = city.lower()
        if city_lower in cls.CITIES:
            return cls.CITIES[city_lower]
        # Generate random weather for unknown cities
        return {
            "temp": random.randint(10, 35),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
            "humidity": random.randint(30, 90)
        }


async def get_weather(city: str) -> Dict[str, Any]:
    """Get weather information for a city"""
    await asyncio.sleep(0.1)  # Simulate API call
    weather = WeatherData.get_weather(city)
    return {
        "city": city,
        "temperature_celsius": weather["temp"],
        "condition": weather["condition"],
        "humidity_percent": weather["humidity"]
    }


async def get_weather_forecast(city: str, days: int = 3) -> List[Dict[str, Any]]:
    """Get weather forecast for multiple days"""
    await asyncio.sleep(0.2)  # Simulate API call
    base_weather = WeatherData.get_weather(city)
    forecast = []
    
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "temperature_celsius": base_weather["temp"] + random.randint(-3, 3),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
            "humidity_percent": base_weather["humidity"] + random.randint(-10, 10)
        })
    
    return forecast


tool_registry.register(
    name="get_weather",
    description="Get current weather for a city",
    parameters={
        "city": ToolParameter(
            type=ToolParameterType.STRING,
            description="City name",
            required=True
        )
    },
    handler=get_weather
)

tool_registry.register(
    name="get_weather_forecast",
    description="Get weather forecast for multiple days",
    parameters={
        "city": ToolParameter(
            type=ToolParameterType.STRING,
            description="City name",
            required=True
        ),
        "days": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Number of days (default: 3)",
            required=False
        )
    },
    handler=get_weather_forecast
)


# ============== Text Summarizer Tools ==============

async def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize text to a maximum length"""
    await asyncio.sleep(0.1)  # Simulate processing
    
    if len(text) <= max_length:
        return text
    
    # Simple summarization (take first sentences)
    sentences = text.split('.')
    summary = ""
    
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() + "..." if len(summary) < len(text) else summary.strip()


async def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract key words from text"""
    await asyncio.sleep(0.1)
    
    # Simple keyword extraction (remove common words)
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "must", "shall"}
    
    words = text.lower().replace(".", "").replace(",", "").split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Return most frequent keywords
    from collections import Counter
    keyword_counts = Counter(keywords)
    return [word for word, count in keyword_counts.most_common(max_keywords)]


async def count_words(text: str) -> Dict[str, int]:
    """Count words, characters, and sentences in text"""
    await asyncio.sleep(0.05)
    
    words = text.split()
    sentences = text.split('.')
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()])
    }


tool_registry.register(
    name="summarize_text",
    description="Summarize text to a maximum length",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to summarize",
            required=True
        ),
        "max_length": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Maximum length of summary",
            required=False
        )
    },
    handler=summarize_text
)

tool_registry.register(
    name="extract_keywords",
    description="Extract key words from text",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to analyze",
            required=True
        ),
        "max_keywords": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Maximum number of keywords",
            required=False
        )
    },
    handler=extract_keywords
)

tool_registry.register(
    name="count_words",
    description="Count words, characters, and sentences in text",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to analyze",
            required=True
        )
    },
    handler=count_words
)
```

#### Step 2: Create LLM Tool Router

```python
# llm_router.py
from typing import Dict, Any, List, Optional
import json
from tools import tool_registry
from models import ToolDefinition


class LLMToolRouter:
    """Routes LLM requests to appropriate tools"""
    
    def __init__(self):
        self.tools = tool_registry.list_tools()
        self.tool_definitions = self._build_tool_definitions()
    
    def _build_tool_definitions(self) -> List[Dict[str, Any]]:
        """Build OpenAI-compatible tool definitions"""
        definitions = []
        
        for tool in self.tools:
            properties = {}
            required = []
            
            for param_name, param in tool.parameters.items():
                properties[param_name] = {
                    "type": param.type.value,
                    "description": param.description
                }
                if param.required:
                    required.append(param_name)
            
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            })
        
        return definitions
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions for LLM"""
        return self.tool_definitions
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        return await tool_registry.execute(tool_name, arguments)
    
    def parse_llm_response(self, llm_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse LLM response to extract tool call"""
        if "tool_calls" in llm_response:
            return llm_response["tool_calls"][0]
        return None


# Example usage with OpenAI
async def process_with_llm(user_query: str, router: LLMToolRouter) -> str:
    """Process user query through LLM with tool selection"""
    
    # This would normally call OpenAI API
    # For demonstration, we simulate the response
    
    tool_definitions = router.get_tool_definitions()
    
    # Simulated LLM response (in real implementation, call OpenAI)
    simulated_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "tool_calls": [{
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"city": "London"})
                    }
                }]
            }
        }]
    }
    
    # Extract tool call
    tool_call = simulated_response["choices"][0]["message"]["tool_calls"][0]
    tool_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    # Execute tool
    result = await router.execute_tool(tool_name, arguments)
    
    return f"Tool '{tool_name}' executed with result: {result}"
```

#### Step 3: Create Main Application

```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import json

from tools import tool_registry
from advanced_tools import *
from llm_router import LLMToolRouter


app = FastAPI(title="MCP Tool System", version="2.0.0")
router = LLMToolRouter()


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


@app.get("/")
async def root():
    return {
        "service": "MCP Tool System",
        "version": "2.0.0",
        "available_tools": len(router.get_tool_definitions())
    }


@app.get("/tools")
async def list_tools():
    """List all available tools with definitions"""
    return {"tools": router.get_tool_definitions()}


@app.post("/query")
async def process_query(request: QueryRequest):
    """Process a natural language query"""
    try:
        result = await process_with_llm(request.query, router)
        return {"query": request.query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/call")
async def call_tool(request: ToolCallRequest):
    """Directly call a tool"""
    try:
        result = await router.execute_tool(request.tool_name, request.arguments)
        return {
            "tool": request.tool_name,
            "arguments": request.arguments,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tool/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    tools = router.get_tool_definitions()
    for tool in tools:
        if tool["function"]["name"] == tool_name:
            return tool
    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("MCP Tool System Starting...")
    print("=" * 60)
    print(f"Total tools registered: {len(tool_registry.list_tools())}")
    print("Tools:", [t.name for t in tool_registry.list_tools()])
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## Testing Instructions for Project 4

### Test 1: List All Tools

```bash
curl http://localhost:8001/tools
```

### Test 2: Call Calculator Tool

```bash
curl -X POST http://localhost:8001/tool/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "calc_add", "arguments": {"a": 15, "b": 25}}'
```

**Expected Output:**
```json
{
    "tool": "calc_add",
    "arguments": {"a": 15, "b": 25},
    "result": 40
}
```

### Test 3: Get Weather

```bash
curl -X POST http://localhost:8001/tool/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_weather", "arguments": {"city": "Tokyo"}}'
```

**Expected Output:**
```json
{
    "tool": "get_weather",
    "arguments": {"city": "Tokyo"},
    "result": {
        "city": "Tokyo",
        "temperature_celsius": 25,
        "condition": "Rainy",
        "humidity_percent": 80
    }
}
```

### Test 4: Summarize Text

```bash
curl -X POST http://localhost:8001/tool/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "summarize_text",
    "arguments": {
        "text": "This is a long text that needs to be summarized. It contains multiple sentences. We want to extract the key information.",
        "max_length": 50
    }
  }'
```

---

## Common Mistakes & Best Practices

### Common Mistakes

| Mistake | Solution |
|---------|----------|
| Not validating tool parameters | Use Pydantic models for validation |
| Blocking async operations | Use `await` for all async functions |
| No error handling | Wrap tool execution in try-except |
| Hardcoding tool definitions | Use registry pattern for dynamic tools |
| No rate limiting | Implement request throttling |

### Best Practices

1. **Always validate inputs** - Use Pydantic for schema validation
2. **Use async/await** - MCP servers should be non-blocking
3. **Log all tool executions** - For debugging and auditing
4. **Implement timeouts** - Prevent hanging requests
5. **Version your tools** - Track changes over time
6. **Document tool parameters** - Clear descriptions help LLMs

---

## Interview Preparation Tips

### Common MCP Interview Questions

1. **Q: What is the difference between MCP Client and Server?**
   - A: Client requests tools and sends prompts. Server exposes tools and handles requests.

2. **Q: How does tool calling work with LLMs?**
   - A: LLM receives tool definitions, decides which tool to call, returns tool name and arguments, server executes and returns result.

3. **Q: How do you handle context in MCP?**
   - A: Use session IDs to maintain state, store context in memory or database, pass context with each request.

4. **Q: What are the security considerations?**
   - A: Validate all inputs, implement rate limiting, authenticate clients, sanitize outputs.

---

## Coding Exercise

### Exercise 1: Add a New Tool

Add a tool called `convert_currency` that converts between currencies.

```python
# Your task: Implement this tool
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    # Hint: Use a dictionary for exchange rates
    pass
```

### Exercise 2: Add Error Handling

Modify the `calculator_divide` function to handle division by zero gracefully.

---

## Possible Improvements

1. Add database persistence for context
2. Implement authentication for MCP server
3. Add rate limiting per client
4. Create a web UI for tool testing
5. Add tool usage analytics
6. Implement tool caching
7. Add support for streaming responses

---

## Record Section

### What We Learned

- MCP architecture (Client/Server model)
- Tool registration and execution
- JSON-RPC protocol for MCP
- Context management
- LLM tool routing

### What We Built

- Simple MCP Server (Project 3)
- Advanced MCP Tool System (Project 4)
- Calculator, Weather, and Text tools
- LLM-compatible tool definitions
