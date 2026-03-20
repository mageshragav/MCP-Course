# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import json

from tools import tool_registry
from advanced_tools import *
from llm_router import LLMToolRouter, process_with_llm


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