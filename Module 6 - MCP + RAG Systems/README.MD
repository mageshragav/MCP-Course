# Module 6: MCP + RAG Systems

This module focuses on integrating Retrieval Augmented Generation (RAG) with the Model Context Protocol (MCP). We will build systems that allow Large Language Models to access external knowledge bases, perform semantic searches, and synthesize information from diverse sources like company documents and research papers.

## Core Concepts

### 1. Retrieval Augmented Generation (RAG)
RAG is an architecture that augments the capabilities of a Large Language Model by retrieving relevant data from an external knowledge base before generating a response. This reduces hallucinations and allows the model to answer questions based on up-to-date or private data.

In the context of MCP, RAG logic is encapsulated within **Tools**. The MCP server exposes a tool (e.g., `search_knowledge_base`) that the client (LLM) can call. The server handles the embedding, vector search, and context retrieval, returning the relevant text chunks for the LLM to use in its final answer.

### 2. Embeddings
Embeddings are numerical representations of text where semantically similar texts are mapped to nearby points in a high-dimensional vector space.
- **Purpose:** They enable "semantic search." Instead of matching keywords, the system matches meaning. For example, a query about "revenue growth" can retrieve documents containing "increased sales figures."
- **Implementation:** We typically use models like `text-embedding-3-small` (OpenAI) or open-source alternatives like `all-MiniLM-L6-v2` via Hugging Face.

### 3. Vector Databases
Vector databases (e.g., ChromaDB, FAISS, Pinecone) store these embeddings efficiently. They support similarity search algorithms (like Cosine Similarity) to quickly find the top-K most relevant document chunks for a given query vector.

---

## Project 11: AI Knowledge Base Chatbot

**Objective:** Build an MCP server that allows an AI assistant to answer questions based on a specific set of company documents.

**Features:**
- **Ask Company Docs:** Ingest PDFs or text files containing company policies, product specs, or HR manuals.
- **Semantic Search:** Retrieve relevant passages based on the meaning of the user's question.
- **Context Injection:** Automatically inject the retrieved text into the LLM's context window as part of the tool response.

### Implementation Guide

We will use the `mcp` Python SDK to create a server that manages a local ChromaDB instance.

#### Prerequisites
```bash
pip install mcp chromadb sentence-transformers pypdf
```

#### Step 1: Setup and Ingestion Logic
First, we define the logic to load documents, chunk them, create embeddings, and store them in the vector database.

```python
import os
from typing import List
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB (persistent storage)
client = chromadb.PersistentClient(path="./company_kb_db")
collection = client.get_or_create_collection(name="company_docs")

def ingest_pdf(file_path: str):
    """Reads a PDF, chunks it, embeds it, and stores it in the vector DB."""
    reader = PdfReader(file_path)
    text_chunks = []
    
    # Simple chunking by page (production systems use more sophisticated chunking)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Split into smaller paragraphs for better retrieval granularity
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                if len(para.strip()) > 50: # Ignore very short snippets
                    text_chunks.append({
                        "content": para.strip(),
                        "metadata": {"source": file_path, "page": i}
                    })

    # Batch process embeddings
    if not text_chunks:
        return

    contents = [chunk["content"] for chunk in text_chunks]
    embeddings = embedding_model.encode(contents).tolist()
    ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(contents))]
    metadatas = [chunk["metadata"] for chunk in text_chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=contents,
        metadatas=metadatas
    )
    print(f"Ingested {len(contents)} chunks from {file_path}")

# Example ingestion (Run this once to populate DB)
# ingest_pdf("company_handbook.pdf")
```

#### Step 2: Creating the MCP Server
Now we expose the search functionality as an MCP Tool.

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

mcp = FastMCP("KnowledgeBaseChatbot")

@mcp.tool()
def search_company_docs(query: str, n_results: int = 3) -> str:
    """
    Search the company knowledge base for relevant information.
    Use this tool when the user asks about company policies, products, or internal procedures.
    
    Args:
        query: The natural language question from the user.
        n_results: Number of relevant chunks to retrieve.
    
    Returns:
        A formatted string containing the relevant context found.
    """
    # Generate embedding for the query
    query_embedding = embedding_model.encode([query]).tolist()[0]
    
    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas"]
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "No relevant information found in the company knowledge base."
    
    # Format the context for the LLM
    context_parts = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        source = meta.get('source', 'Unknown')
        context_parts.append(f"[Source: {source}]\n{doc}")
    
    return "\n\n---\n\n".join(context_parts)

if __name__ == "__main__":
    mcp.run()
```

#### How It Works in Practice
1.  **User Ask:** "What is the policy on remote work?"
2.  **LLM Decision:** The LLM sees the `search_company_docs` tool and decides to call it with the query "remote work policy".
3.  **MCP Execution:** The server converts "remote work policy" to a vector, searches ChromaDB, and returns the specific paragraph from the handbook.
4.  **Final Answer:** The LLM receives the tool output (the actual policy text) and synthesizes a polite, accurate answer citing the source.

---

## Project 12: AI Research Assistant

**Objective:** Create a versatile MCP server capable of browsing the web, parsing academic papers (PDFs), and maintaining a memory of notes for long-term research tasks.

**Capabilities:**
- **Search Web:** Fetch real-time information using web scraping or search APIs.
- **Summarize Papers:** Download and parse PDF research papers to extract abstracts and conclusions.
- **Store Notes:** Save key findings to a persistent memory store (JSON or Vector DB) for later retrieval.

**Tools Required:**
- Web Scraping (`requests`, `beautifulsoup4`)
- PDF Parsing (`pypdf` or `pdfplumber`)
- Memory Storage (File-based or Vector DB)

### Implementation Guide

#### Prerequisites
```bash
pip install mcp requests beautifulsoup4 pdfplumber
```

#### Step 1: Define Tools for Web, PDF, and Memory

```python
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import pdfplumber
import json
import os
from datetime import datetime

mcp = FastMCP("ResearchAssistant")

MEMORY_FILE = "research_notes.json"

# --- Helper Functions ---

def load_notes():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def save_note(topic: str, content: str):
    notes = load_notes()
    new_note = {
        "id": len(notes) + 1,
        "topic": topic,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    notes.append(new_note)
    with open(MEMORY_FILE, 'w') as f:
        json.dump(notes, f, indent=2)
    return f"Note saved successfully with ID {new_note['id']}."

# --- MCP Tools ---

@mcp.tool()
def search_web(query: str) -> str:
    """
    Search the web for current information. 
    Note: This uses a mock implementation for demonstration. 
    In production, integrate with Google Custom Search API or Bing API.
    
    Args:
        query: The search term.
        
    Returns:
        Summarized search results.
    """
    # Mocking a search result for safety in this example without API keys
    # Real implementation would hit an API endpoint
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        results = data.get('query', {}).get('search', [])
        
        if not results:
            return "No web results found."
            
        summary = []
        for item in results[:3]: # Top 3 results
            summary.append(f"Title: {item['title']}\nSnippet: {item['snippet']}\n")
            
        return "\n".join(summary)
    except Exception as e:
        return f"Error searching web: {str(e)}"

@mcp.tool()
def summarize_paper(pdf_url: str) -> str:
    """
    Download a PDF paper from a URL and extract the text for summarization.
    
    Args:
        pdf_url: Direct URL to the PDF file.
        
    Returns:
        The first 2000 characters of the extracted text (acting as context for summarization).
    """
    try:
        # Download PDF
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        # Save temporarily
        temp_filename = "temp_paper.pdf"
        with open(temp_filename, 'wb') as f:
            f.write(response.content)
            
        # Parse PDF
        text_content = ""
        with pdfplumber.open(temp_filename) as pdf:
            # Extract text from first 3 pages (usually Abstract + Intro)
            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
        
        # Cleanup
        os.remove(temp_filename)
        
        if not text_content:
            return "Could not extract text from the PDF."
            
        return f"Extracted Content (for summarization):\n{text_content[:2000]}..."
        
    except Exception as e:
        return f"Error processing paper: {str(e)}"

@mcp.tool()
def store_research_note(topic: str, finding: str) -> str:
    """
    Store a key finding or summary in the long-term memory.
    
    Args:
        topic: The subject of the note.
        finding: The specific insight or summary to store.
        
    Returns:
        Confirmation message.
    """
    return save_note(topic, finding)

@mcp.tool()
def recall_research_notes(topic_keyword: str) -> str:
    """
    Retrieve previously stored notes related to a keyword.
    
    Args:
        topic_keyword: Keyword to filter notes.
        
    Returns:
        List of relevant notes.
    """
    notes = load_notes()
    relevant = [n for n in notes if topic_keyword.lower() in n['topic'].lower() or topic_keyword.lower() in n['content'].lower()]
    
    if not relevant:
        return "No notes found matching that keyword."
    
    output = []
    for note in relevant:
        output.append(f"[{note['timestamp']}] Topic: {note['topic']}\nFinding: {note['content']}")
    
    return "\n\n".join(output)

if __name__ == "__main__":
    mcp.run()
```

### Workflow Demonstration

1.  **Research Phase:**
    *   User: "Find recent developments in solid-state batteries."
    *   LLM calls `search_web("solid-state batteries")`.
    *   MCP returns snippets from Wikipedia/News.
    *   LLM identifies a promising paper URL.

2.  **Deep Dive:**
    *   User: "Summarize this paper: [URL]"
    *   LLM calls `summarize_paper([URL])`.
    *   MCP downloads, parses the PDF, and returns the abstract/intro text.
    *   LLM generates a concise summary.

3.  **Memory Retention:**
    *   User: "Save the key efficiency metric from that summary."
    *   LLM calls `store_research_note(topic="Solid State Batteries", finding="New prototype achieves 500 Wh/kg density.")`.
    *   MCP saves to `research_notes.json`.

4.  **Recall:**
    *   (Next day) User: "What did we find out about battery density last time?"
    *   LLM calls `recall_research_notes("density")`.
    *   MCP retrieves the saved note, allowing the conversation to continue with context.

---

## Summary

In Module 6, we expanded the capabilities of MCP servers beyond simple function calling.
1.  **RAG Architecture:** We learned how to decouple knowledge storage (Vector DB) from reasoning (LLM) using MCP tools as the bridge.
2.  **Embeddings & Vectors:** We implemented semantic search to find information based on meaning rather than keywords.
3.  **Project 11:** Built a secure, internal Knowledge Base Chatbot for company data.
4.  **Project 12:** Created a dynamic Research Assistant capable of interacting with the live web, parsing complex documents, and maintaining stateful memory.

These patterns form the backbone of modern enterprise AI applications, allowing organizations to leverage their proprietary data securely through the standardized MCP interface.