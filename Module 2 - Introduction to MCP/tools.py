from typing import Any, Dict, Callable, Optional, List
from models import ToolDefinition, ToolParameter, ToolParameterType
import inspect

def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def get_info() -> str:
    """Get server information"""
    return "MCP Server v1.0 - Simple Implementation"


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
        if inspect.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)
        
tool_registry = ToolRegistry()

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