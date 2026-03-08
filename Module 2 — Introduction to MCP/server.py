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