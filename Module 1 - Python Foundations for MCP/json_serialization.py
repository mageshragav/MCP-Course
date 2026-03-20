import json
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


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