# 🚀 MCP Python AI Platform

**Model Context Protocol (MCP) based AI system using Python, FastAPI & LLMs**

---

## 📌 Overview

This project is a **production-ready MCP (Model Context Protocol) platform** built using Python. It enables Large Language Models (LLMs) to interact with tools, databases, APIs, and systems through a structured interface.

The system supports:

* Tool calling
* Context management
* Multi-agent workflows
* RAG (Retrieval-Augmented Generation)
* Automation pipelines

---

## 🧠 What is MCP?

Model Context Protocol (MCP) is a framework that allows LLMs to:

* Discover tools
* Execute functions
* Access resources
* Maintain context across interactions

---

## 🏗️ Architecture

```
User → API (FastAPI) → MCP Server → Tools → External Systems
                                ↓
                             LLM Layer
                                ↓
                        Context / Memory
```

---

## ⚙️ Tech Stack

* **Backend:** Python, FastAPI
* **LLM:** OpenAI / Claude / Gemini
* **Validation:** Pydantic
* **Async:** asyncio
* **Database:** PostgreSQL / MySQL
* **Vector DB:** FAISS / ChromaDB
* **Agents:** LangChain / LangGraph / CrewAI
* **Deployment:** Docker

---

## ✨ Features

* 🔌 MCP-compliant tool system
* 🧠 Context-aware AI responses
* 📂 File system access tools
* 🗄️ Database query tools
* 🔍 RAG-based document search
* 🤖 Multi-agent workflows
* ⚡ Async execution
* 🔐 Secure tool execution

---

## 📁 Project Structure

```
mcp-python-platform/
│
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py
│   ├── dependencies.py
│
├── mcp/
│   ├── server.py           # MCP server core
│   ├── client.py           # MCP client logic
│   ├── context.py          # Context management
│
├── tools/
│   ├── calculator.py
│   ├── filesystem.py
│   ├── database.py
│   ├── search.py
│
├── agents/
│   ├── planner.py
│   ├── executor.py
│
├── rag/
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│
├── services/
│   ├── llm_service.py
│
├── models/
│   ├── schemas.py
│
├── tests/
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/mcp-python-platform.git
cd mcp-python-platform
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_key
DATABASE_URL=your_db_url
```

---

### 5️⃣ Run Server

```bash
uvicorn app.main:app --reload
```

---

## 🔧 Example MCP Tool

```python
def add_numbers(a: int, b: int) -> int:
    return a + b
```

---

## 🧪 API Example

```bash
POST /ask

{
  "query": "What is 10 + 20?"
}
```

---

## 📦 Projects Included

### Beginner

* AI CLI Assistant
* JSON Context Manager
* Basic MCP Server

### Intermediate

* Tool-based MCP system
* File System MCP
* Database MCP

### Advanced

* AI Data Analyst
* Document Search (RAG)
* AI Coding Assistant

### Expert

* DevOps Assistant
* Multi-Agent System
* Autonomous Workflow
* Full AI Automation Platform

---

## 🔍 RAG Workflow

1. Load documents
2. Generate embeddings
3. Store in vector DB
4. Retrieve relevant chunks
5. Send to LLM

---

## 🤖 Multi-Agent System

Agents:

* Planner → breaks tasks
* Executor → runs tools
* Reviewer → validates output

---

## 🐳 Docker Setup

```bash
docker build -t mcp-app .
docker run -p 8000:8000 mcp-app
```

---

## 🧠 Best Practices

* Use async for scalability
* Validate inputs with Pydantic
* Keep tools modular
* Limit tool permissions
* Log all tool executions

---

## ⚠️ Common Mistakes

* Overloading context
* Poor prompt design
* No error handling
* Tight coupling of tools

---

## 📈 Future Improvements

* UI Dashboard
* Real-time streaming
* Plugin system
* Authentication layer

---

## 🤝 Contributing

Pull requests are welcome!
Please follow clean code and modular design.

---

## 📜 License

MIT License

---

## 🙌 Acknowledgements

* OpenAI
* Anthropic
* LangChain
* FastAPI

---
