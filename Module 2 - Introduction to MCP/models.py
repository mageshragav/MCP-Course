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