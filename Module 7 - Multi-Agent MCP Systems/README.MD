# Module 7: Multi-Agent MCP Systems

## Introduction
Welcome to Module 7. In previous modules, we built single MCP servers and integrated them with LLMs. Now, we scale up to **Multi-Agent Systems**. Here, multiple specialized AI agents collaborate via the Model Context Protocol (MCP) to solve complex problems that a single agent cannot handle alone.

We will focus on the architecture of agent collaboration, task delegation, and communication patterns using Python libraries like **CrewAI**, **LangGraph**, and **Microsoft AutoGen**, all while leveraging MCP for tool access and context sharing.

---

## Part 1: Key Concepts & Architecture

### 1. What is a Multi-Agent System (MAS)?
**Simple Explanation:** Imagine a software development company. You don't ask one person to do everything (design, code, test, deploy). Instead, you have a Project Manager, a Coder, and a QA Tester. They talk to each other, pass work back and forth, and use shared tools. A MAS is the digital version of this team.

**Real-World Analogy:** An emergency room. The triage nurse assesses, the doctor diagnoses, the surgeon operates, and the pharmacist dispenses meds. They share the patient's record (Context) and use specific tools (scalpels, X-rays). If they didn't communicate, the patient would be in trouble.

**MCP Role:** MCP acts as the standardized "hospital record system" and "tool bench." Every agent connects to the same MCP server to access patient data (Resources) and medical tools (Tools), ensuring consistency regardless of which agent is acting.

### 2. Core Architectural Patterns
1.  **Sequential Handoff:** Agent A finishes → passes result to Agent B → Agent B finishes.
2.  **Hierarchical (Manager-Worker):** A "Manager" agent breaks down a task and assigns sub-tasks to "Worker" agents.
3.  **Collaborative/Debate:** Agents discuss a problem, critique each other's outputs, and converge on a solution.

### 3. Agent Communication via MCP
In a traditional setup, agents might talk via raw JSON over HTTP. In an MCP-native system:
*   **Shared Context:** Agents read/write to MCP **Resources** (e.g., a shared `project_state.json` file exposed as a resource).
*   **Tool Discovery:** All agents connect to the same MCP Server to discover available tools dynamically.
*   **Prompt Templates:** Agents use shared MCP **Prompts** to ensure they format their requests consistently.

---

## Part 2: Libraries Overview

We will utilize three major frameworks, adapted to work with MCP principles:

1.  **CrewAI:** Best for role-based, sequential, or hierarchical workflows. It defines agents with specific roles, goals, and backstories.
    *   *Use Case:* Structured pipelines like "Research → Write → Edit".
2.  **LangGraph:** Built on LangChain, it treats agent workflows as state machines (graphs). Excellent for cyclic flows (loops) and complex conditional logic.
    *   *Use Case:* Complex decision trees where an agent might need to retry a step multiple times.
3.  **AutoGen (Microsoft):** Focuses on conversational agents that can terminate themselves. Highly flexible for ad-hoc collaboration.
    *   *Use Case:* Dynamic problem solving where the conversation flow isn't strictly predefined.

*Note: For this course, we will primarily use **CrewAI** for its clarity in defining roles, but we will architect the tools it uses as **MCP Servers**.*

---

## Part 3: Project 13 — AI Software Development Team

**Objective:** Build a multi-agent system where three agents (Planner, Coder, Tester) collaborate to write and verify a simple Python function based on a user request. They will share context via a local MCP resource (a shared state file).

### Architecture Diagram Explanation
1.  **User Input:** Receives a requirement (e.g., "Write a function to calculate Fibonacci").
2.  **MCP State Resource:** A JSON file (`team_state.json`) exposed as an MCP Resource. All agents read/write here.
3.  **Planner Agent:** Reads request, creates a plan, writes to State.
4.  **Coder Agent:** Reads plan from State, writes code, saves code to disk, updates State.
5.  **Tester Agent:** Reads code from State/Disk, runs tests, writes results to State.
6.  **Final Output:** The system returns the code and test results.

### Required Tools
*   Python 3.10+
*   `crewai`, `langchain-openai`
*   `mcp` (Python SDK)
*   `fastapi` (for the MCP server if needed, though we will use local files for simplicity in this example)
*   OpenAI API Key

### Step-by-Step Implementation

#### Step 1: Set up the MCP State Manager
First, we create a simple MCP server that manages the shared state (`team_state.json`). This ensures all agents access the *same* truth.

```python
# mcp_state_server.py
import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent

# Initialize the MCP server
server = Server("dev-team-state")

STATE_FILE = Path("team_state.json")

def load_state():
    if not STATE_FILE.exists():
        return {"status": "initialized", "plan": "", "code": "", "test_result": ""}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

@server.list_resources()
async def list_resources():
    # Expose the current state as a resource
    return [
        Resource(
            uri="state://current",
            name="Current Team State",
            description="Shared JSON state for Planner, Coder, and Tester",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri):
    if uri == "state://current":
        state = load_state()
        return [TextContent(type="text", text=json.dumps(state, indent=2))]
    raise ValueError(f"Unknown resource: {uri}")

# We won't implement write via MCP protocol directly for safety in this demo,
# instead agents will call a 'tool' to update state.
@server.list_tools()
async def list_tools():
    return [
        # Tool to update the state
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "update_state":
        current = load_state()
        current.update(arguments)
        save_state(current)
        return [TextContent(type="text", text=f"State updated: {json.dumps(current)}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 2: Define the CrewAI Agents with MCP Integration
Now we build the agent team. We will simulate the MCP connection by having the agents call the `update_state` tool (which would normally go over stdio to the server above, but here we mock the direct file interaction for the sake of a runnable single-script example).

*Note: In a production environment, you would run `mcp_state_server.py` as a separate process and connect CrewAI tools to it via `StdioMCPClient`.*

```python
# project_13_dev_team.py
import os
import json
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Ensure API Key is set
# os.environ["OPENAI_API_KEY"] = "your-key-here"

STATE_FILE = Path("team_state.json")

# --- Mock MCP Client Functions (Simulating the MCP Server interaction) ---
def mcp_read_state():
    if not STATE_FILE.exists():
        return {"status": "idle", "requirement": "", "plan": "", "code": "", "test_result": ""}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def mcp_update_state(**kwargs):
    current = mcp_read_state()
    current.update(kwargs)
    with open(STATE_FILE, "w") as f:
        json.dump(current, f, indent=2)
    return f"State updated successfully. Current status: {current['status']}"

def mcp_write_code(code_content):
    with open("generated_solution.py", "w") as f:
        f.write(code_content)
    return "Code written to generated_solution.py"

def mcp_run_tests():
    # Simple mock test runner
    try:
        # In real life, this would subprocess.run(['pytest', ...])
        # For demo, we just check if file exists
        if Path("generated_solution.py").exists():
            return "Tests Passed: Syntax OK, Logic assumed correct for demo."
        return "Tests Failed: File not found."
    except Exception as e:
        return f"Tests Failed: {str(e)}"

# --- Define Agents ---

llm = ChatOpenAI(model="gpt-4o")

planner = Agent(
    role="Senior Technical Planner",
    goal="Break down user requirements into a strict step-by-step technical plan.",
    backstory="You are an expert system architect. You don't write code, you design the logic.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[] # Planner reads state, doesn't need external tools in this simple flow
)

coder = Agent(
    role="Expert Python Developer",
    goal="Write clean, efficient, and documented Python code based on the plan.",
    backstory="You are a senior dev who loves PEP8 and type hinting. You only code what is planned.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[mcp_write_code] 
)

tester = Agent(
    role="QA Automation Engineer",
    goal="Verify the code works and report results.",
    backstory="You are meticulous. You break things to make them stronger.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[mcp_run_tests]
)

# --- Define Tasks ---

# Task 1: Initialize and Plan
task_plan = Task(
    description="""
    1. Read the current state from the shared context.
    2. If the requirement is empty, wait. (For this demo, we assume requirement is passed in context).
    3. Create a detailed technical plan to solve the requirement: '{requirement}'.
    4. Update the shared state with your plan using the update_state mechanism.
    5. Output ONLY the plan summary.
    """,
    expected_output="A concise technical plan string.",
    agent=planner,
    human_input=False
)

# Task 2: Code
task_code = Task(
    description="""
    1. Read the plan from the shared state.
    2. Implement the Python code according to the plan.
    3. Use the 'mcp_write_code' tool to save the file.
    4. Update the shared state status to 'coding_complete'.
    """,
    expected_output="Confirmation that code is written.",
    agent=coder,
    human_input=False
)

# Task 3: Test
task_test = Task(
    description="""
    1. Verify the code exists.
    2. Run the 'mcp_run_tests' tool.
    3. Update the shared state with the test results.
    4. Provide a final report.
    """,
    expected_output="Final test report and status.",
    agent=tester,
    human_input=False
)

# --- Execution ---

def run_dev_team(user_requirement):
    # Initialize State
    mcp_update_state(requirement=user_requirement, status="planning")
    
    crew = Crew(
        agents=[planner, coder, tester],
        tasks=[task_plan, task_code, task_test],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff(inputs={"requirement": user_requirement})
    return result

if __name__ == "__main__":
    print("--- Starting AI Software Development Team ---")
    req = "Create a function that calculates the factorial of a number recursively with error handling."
    final_report = run_dev_team(req)
    print("\n--- Final Report ---")
    print(final_report)
    
    # Show final state
    print("\n--- Final Shared State ---")
    print(json.dumps(mcp_read_state(), indent=2))
```

### Testing Instructions
1.  Install dependencies: `pip install crewai langchain-openai`.
2.  Set your `OPENAI_API_KEY`.
3.  Run the script: `python project_13_dev_team.py`.
4.  Observe the console output showing the Planner thinking, the Coder writing, and the Tester validating.
5.  Check the generated `team_state.json` and `generated_solution.py` files.

### Possible Improvements
*   **Real MCP Transport:** Replace the mock functions with `mcp.ClientSession` connecting to the running `mcp_state_server.py` via stdio.
*   **Looping:** If the Tester fails, add logic to send the task back to the Coder (requires LangGraph or CrewAI conditional tasks).
*   **Human in the Loop:** Pause before the Tester runs to allow a human to review the code.

---

## Part 4: Project 14 — Autonomous AI Workflow System

**Objective:** Create a system that accepts a high-level natural language request, autonomously breaks it down, selects the right MCP tools, executes them, and aggregates the result without step-by-step human intervention.

### Architecture Explanation
1.  **Orchestrator Agent:** The brain. It receives the user prompt.
2.  **Task Decomposer:** Breaks the prompt into a list of atomic steps.
3.  **Tool Router:** Maps steps to specific MCP Tools (e.g., `search_web`, `query_db`, `send_email`).
4.  **Execution Engine:** Runs tools sequentially or in parallel.
5.  **Synthesizer:** Combines tool outputs into a final answer.

This project demonstrates **Dynamic Task Delegation**. Unlike Project 13 (fixed sequence), this flow changes based on the input.

### Implementation Strategy (Using LangGraph for State Management)

We will use **LangGraph** because it excels at cyclic graphs (e.g., "If tool fails, retry" or "If more info needed, search again").

```python
# project_14_autonomous_workflow.py
import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import operator

# Setup LLM
llm = ChatOpenAI(model="gpt-4o")

# --- Define State ---
class WorkflowState(TypedDict):
    messages: Annotated[List, operator.add]
    plan: str
    steps: List[str]
    current_step_index: int
    results: List[str]
    is_complete: bool

# --- Mock MCP Tools ---
def mcp_search_database(query: str) -> str:
    return f"DB Result for '{query}': Found 3 records matching criteria."

def mcp_send_notification(message: str) -> str:
    return f"Notification sent: {message}"

def mcp_generate_report(data: str) -> str:
    return f"Report generated based on: {data}"

tool_map = {
    "search_db": mcp_search_database,
    "notify": mcp_send_notification,
    "report": mcp_generate_report
}

# --- Nodes ---

def planner_node(state: WorkflowState):
    """Breaks user request into steps."""
    last_msg = state["messages"][-1].content if state["messages"] else ""
    
    prompt = f"""
    Analyze this request: '{last_msg}'
    Create a numbered list of steps to solve it using these available tools: {list(tool_map.keys())}.
    Return ONLY the JSON list of steps strings.
    """
    # In a real app, use structured output (Pydantic)
    response = llm.invoke(prompt).content
    # Mock parsing for demo (assume LLM returns valid list string representation)
    steps = ["search_db: check user stats", "report: generate summary", "notify: alert admin"] 
    
    return {
        "plan": "Autonomous workflow initiated",
        "steps": steps,
        "current_step_index": 0,
        "results": []
    }

def executor_node(state: WorkflowState):
    """Executes the current step."""
    idx = state["current_step_index"]
    steps = state["steps"]
    
    if idx >= len(steps):
        return {"is_complete": True}
    
    current_task = steps[idx]
    # Parse tool name (simple split for demo)
    parts = current_task.split(":")
    tool_name = parts[0].strip()
    args = parts[1].strip() if len(parts) > 1 else ""
    
    if tool_name in tool_map:
        result = tool_map[tool_name](args)
        new_results = state["results"] + [f"Step {idx+1} ({tool_name}): {result}"]
        return {
            "results": new_results,
            "current_step_index": idx + 1
        }
    else:
        return {
            "results": state["results"] + [f"Step {idx+1}: Unknown tool {tool_name}"],
            "current_step_index": idx + 1
        }

def synthesizer_node(state: WorkflowState):
    """Generates final response."""
    results = "\n".join(state["results"])
    prompt = f"Based on these execution results:\n{results}\n\nProvide a final summary to the user."
    response = llm.invoke(prompt)
    return {
        "messages": [response]
    }

# --- Graph Construction ---

workflow = StateGraph(WorkflowState)

workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("synthesizer", synthesizer_node)

workflow.set_entry_point("planner")

# Logic: Planner -> Executor (Loop until done) -> Synthesizer
def route_after_plan(state):
    return "executor"

def route_after_exec(state):
    if state["is_complete"] or state["current_step_index"] >= len(state["steps"]):
        return "synthesizer"
    return "executor"

workflow.add_edge("planner", "executor")
workflow.add_conditional_edges("executor", route_after_exec, {
    "executor": "executor",
    "synthesizer": "synthesizer"
})
workflow.add_edge("synthesizer", END)

app = workflow.compile()

# --- Run ---
if __name__ == "__main__":
    user_input = "Check the database for active users, generate a report, and notify the admin."
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "plan": "",
        "steps": [],
        "current_step_index": 0,
        "results": [],
        "is_complete": False
    }
    
    print("Starting Autonomous Workflow...")
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Answer ---")
    print(final_state["messages"][-1].content)
```

### Testing Instructions
1.  Install: `pip install langgraph langchain-openai`.
2.  Run: `python project_14_autonomous_workflow.py`.
3.  The system will plan the steps, execute the mock MCP tools in a loop, and provide a summary.

### Possible Improvements
*   **Dynamic Tool Selection:** Integrate real MCP `list_tools()` calls so the Planner knows exactly what tools are available at runtime.
*   **Error Recovery:** Add a node to handle exceptions and retry failed steps.
*   **Parallel Execution:** Use LangGraph's `Send` API to run independent steps (like searching two different databases) in parallel.

---

## Advanced Topics Recap for Interviews

When discussing Multi-Agent MCP systems in an interview:
1.  **Context Consistency:** Emphasize how MCP Resources prevent "hallucinated state" between agents. All agents read the same source of truth.
2.  **Scalability:** Explain that adding a new agent (e.g., a "Security Auditor") only requires giving it access to the MCP server; no code changes needed in existing agents.
3.  **Tool Abstraction:** Highlight that agents don't need to know *how* a tool works, only *what* it does (via MCP Tool definitions). This decouples logic from implementation.

## Common Mistakes to Avoid
*   **Tight Coupling:** Hardcoding agent communication logic instead of using a shared state (MCP Resource).
*   **Infinite Loops:** In autonomous workflows, failing to set a maximum iteration count or a clear termination condition.
*   **Context Overload:** Passing the entire conversation history to every agent in every step. Use MCP Resources to store summarized state instead.

---

## Next Steps
We have covered the architecture and implementation of Multi-Agent systems using CrewAI and LangGraph with MCP concepts.

**Exercise for You:**
Modify **Project 13** to include a fourth agent: **"Refactor Agent"**.
*   **Condition:** If the "Tester Agent" finds a bug, the workflow should *not* end. Instead, it should pass the code to the "Refactor Agent" to fix it, then loop back to the "Tester".
*   **Hint:** You will need to change the `Process` in CrewAI to handle loops or switch to LangGraph for this specific cyclic logic.
