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