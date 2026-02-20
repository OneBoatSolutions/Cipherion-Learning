# 🤖 Building an AI Coding Agent from Scratch

> A step-by-step guide using the **OpenAI SDK** — from your first API call to a complete multi-agent software development system.

**Everything is built from scratch.** No LangChain, no CrewAI, no external agent frameworks. You'll understand every line of code because you wrote it.

---

## Table of Contents

| Chapter | Title | What You'll Build |
|---------|-------|-------------------|
| [1](#chapter-1-hello-chat-completion) | Hello, Chat Completion | Your first OpenAI API call |
| [2](#chapter-2-building-a-simple-chatbot) | Building a Simple Chatbot | Multi-turn conversational chatbot with streaming |
| [3](#chapter-3-chat-completion-with-tool-execution) | Chat Completion with Tool Execution | Teaching the model to call your Python functions |
| [4](#chapter-4-chatbot-with-tool-use) | Chatbot with Tool Use | Multi-turn chatbot with automatic tool calling |
| [5](#chapter-5-building-a-simple-ai-agent) | Building a Simple AI Agent | The Agent class — from chatbot to autonomous agent |
| [6](#chapter-6-the-agentic-loop) | The Agentic Loop | Think → Decide → Act → Observe → Check |
| [7](#chapter-7-multi-agent-cli-project) | Multi-Agent CLI Project | Full software development system with 4 agents |

---

## Prerequisites

```bash
# 1. Install dependencies
pip install openai python-dotenv

# 2. Create a .env file in the project root
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

Get your API key from: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## Project Structure

```
agent/
├── .env.example                        # Template for your API key
├── requirements.txt                    # Dependencies
├── guide.md                            # ← This file
│
├── chapter_01_chat_completion/
│   └── main.py                         # First API call
│
├── chapter_02_chatbot/
│   └── main.py                         # Multi-turn chatbot with streaming
│
├── chapter_03_tools/
│   └── main.py                         # Tool calling (function calling)
│
├── chapter_04_chatbot_tools/
│   └── main.py                         # Chatbot + tools combined
│
├── chapter_05_simple_agent/
│   ├── agent.py                        # The Agent class
│   └── main.py                         # Demo
│
├── chapter_06_agentic_loop/
│   ├── agent.py                        # AgenticAgent with loop
│   └── main.py                         # Demo
│
└── chapter_07_multi_agent_project/
    ├── main.py                         # CLI entry point
    ├── framework/
    │   ├── base_agent.py               # Base agent class
    │   ├── tool_registry.py            # Tool registration engine
    │   ├── message_bus.py              # Inter-agent communication
    │   └── orchestrator.py             # Pipeline controller
    ├── tools/
    │   ├── file_tools.py               # read/write/list files
    │   ├── shell_tools.py              # Execute shell commands
    │   └── search_tools.py             # Search & grep
    └── agents/
        ├── clarifier_agent.py          # Elaborates requirements
        ├── prd_agent.py                # Generates PRD
        ├── planner_agent.py            # Breaks PRD into tasks
        └── coder_agent.py             # Writes code
```

---

# Chapter 1: Hello, Chat Completion

> **Goal:** Make your first API call and understand the basic concepts.

## Key Concepts

### The Chat Completions API
The OpenAI API works like a conversation. You send a list of **messages** and the model responds with the next message.

### Roles
Every message has a **role**:

| Role | Purpose | Example |
|------|---------|---------|
| `system` | Sets the AI's personality/behavior | "You are a helpful assistant" |
| `user` | Your input/question | "What is an AI agent?" |
| `assistant` | The AI's response | "An AI agent is..." |

### Key Parameters

| Parameter | What it does | Typical value |
|-----------|-------------|---------------|
| `model` | Which AI model to use | `gpt-4o-mini` |
| `temperature` | Controls randomness (0=deterministic, 2=creative) | `0.7` |
| `max_tokens` | Maximum response length | `256` |

## The Code

```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "What is an AI agent in 3 sentences?"},
    ],
    temperature=0.7,
    max_tokens=256,
)

print(response.choices[0].message.content)
```

## What Happens Under the Hood

```
Your Code                    OpenAI API                    Model
───────                      ─────────                     ─────
messages=[...]  ─────────►   Validates request  ─────────► Generates tokens
                             Returns response   ◄─────────
print(content)  ◄─────────   
```

## Run It

```bash
cd chapter_01_chat_completion
python main.py
```

**💡 Key Takeaway:** The chat completions API is stateless — it doesn't remember previous calls. YOU must manage the conversation history yourself. This becomes critical in Chapter 2.

---

# Chapter 2: Building a Simple Chatbot

> **Goal:** Create a multi-turn conversational chatbot with streaming.

## The Critical Concept: Conversation History

The model has no memory between API calls. To create a multi-turn conversation, YOU must maintain a `messages` list and send it with every API call.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
]

# Turn 1
messages.append({"role": "user", "content": "My name is Alice"})
response = call_api(messages)
messages.append({"role": "assistant", "content": response})

# Turn 2 — the model knows your name because it's in the messages!
messages.append({"role": "user", "content": "What's my name?"})
response = call_api(messages)  # Will correctly answer "Alice"
```

## Streaming

Instead of waiting for the entire response, you can receive tokens as they're generated:

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,               # ← This enables streaming
)

for chunk in stream:
    token = chunk.choices[0].delta.content
    if token:
        print(token, end="", flush=True)
```

## The Full Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    CHATBOT LOOP                         │
│                                                         │
│  1. Read user input                                     │
│  2. Append {"role": "user", "content": input}           │
│  3. Call API with full messages list                     │
│  4. Print response (streaming)                          │
│  5. Append {"role": "assistant", "content": response}   │
│  6. Go to step 1                                        │
│                                                         │
│  messages = [system, user1, asst1, user2, asst2, ...]   │
└─────────────────────────────────────────────────────────┘
```

## Run It

```bash
cd chapter_02_chatbot
python main.py
```

**💡 Key Takeaway:** The `messages` list IS the chatbot's memory. Managing this list properly is the foundation for everything we build next.

---

# Chapter 3: Chat Completion with Tool Execution

> **Goal:** Teach the model to call YOUR Python functions.

This is the **breakthrough concept** — the model doesn't just generate text, it can decide to call tools (functions) that you define.

## How Tool Calling Works

```
Step 1: You define tools ──────────────────────────────────────────────────────
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }]

Step 2: Send them with the API call ───────────────────────────────────────────
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,           # ← Tell the model what tools exist
        tool_choice="auto",    # ← Let the model decide when to use them
    )

Step 3: The model responds with tool_calls ────────────────────────────────────
    # Instead of text, the model returns:
    # tool_calls = [{ id: "call_123", function: { name: "get_weather", arguments: '{"city":"Tokyo"}' }}]

Step 4: You execute the function locally ──────────────────────────────────────
    result = get_weather(city="Tokyo")

Step 5: Send the result back ──────────────────────────────────────────────────
    messages.append({"role": "tool", "tool_call_id": "call_123", "content": json.dumps(result)})

Step 6: Call the API again — model uses the result ────────────────────────────
    final_response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    # Now the model says: "The weather in Tokyo is 28°C and humid."
```

## The Three Pieces You Need

### 1. Python functions (what actually runs)
```python
def get_weather(city: str) -> dict:
    return {"city": city, "temp": "28°C", "condition": "Humid"}
```

### 2. JSON schemas (tells the model what exists)
```python
tools = [{"type": "function", "function": {"name": "get_weather", ...}}]
```

### 3. Function map (connects names to callables)
```python
FUNCTIONS = {"get_weather": get_weather}
```

## Run It

```bash
cd chapter_03_tools
python main.py
```

**💡 Key Takeaway:** The model doesn't execute code — it just decides WHICH tool to call and with WHAT arguments. YOU execute the function and send back the result. This separation is the heart of tool calling.

---

# Chapter 4: Chatbot with Tool Use

> **Goal:** Combine the chatbot loop (Ch 2) with tool execution (Ch 3).

## The Key Pattern: The Inner Tool Loop

The challenge: the model might call **multiple tools** in a single turn, or call tools in **sequential steps**. You need an inner loop that keeps running until the model stops requesting tools.

```python
def process_tool_calls(messages):
    """Inner loop: handles tool calls until the model responds with text."""
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
        )
        
        assistant_message = response.choices[0].message
        
        if assistant_message.tool_calls:
            # Execute tools, append results, loop again
            messages.append(assistant_message)
            for tool_call in assistant_message.tool_calls:
                result = execute(tool_call)
                messages.append({"role": "tool", ...})
            continue  # ← Model might want more tools
        else:
            # No tools — return the text response
            return assistant_message.content
```

## Two Levels of Looping

```
OUTER LOOP (conversation turns)     INNER LOOP (tool execution)
────────────────────────────────     ─────────────────────────────
User says something                 Model wants to call tools?
  └─► Call inner loop                 ├─ YES → Execute them
        └─► Returns text              │         Send results
              └─► Print it            │         Loop again
                    └─► Next turn     └─ NO  → Return text response
```

## Run It

```bash
cd chapter_04_chatbot_tools
python main.py
```

Try: "What's the weather in London and what is 42 * 58?"

**💡 Key Takeaway:** The inner `while True` loop that processes tool calls is the foundation of all agent behavior. In Chapter 5, we wrap this pattern into a reusable Agent class.

---

# Chapter 5: Building a Simple AI Agent

> **Goal:** Create an `Agent` class — the leap from chatbot to autonomous agent.

## Chatbot vs. Agent

| | Chatbot | Agent |
|---|---------|-------|
| **Input** | User messages | A **task** to complete |
| **Behavior** | Responds to prompts | **Decides** what to do |
| **Control** | User drives the conversation | Agent drives its own actions |
| **Output** | Text responses | **Results** and **side effects** |

## The Agent Class

```python
class Agent:
    def __init__(self, client, name, system_prompt, tools, functions, model):
        self.client = client
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.functions = functions
        self.model = model

    def run(self, task: str) -> str:
        """Give the agent a task → it works autonomously → returns result."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user",   "content": task},
        ]
        
        while True:
            response = call_api(messages, self.tools)
            if response.tool_calls:
                execute_tools(response.tool_calls)
                continue
            else:
                return response.content
```

## What makes this an "Agent"?

1. **Encapsulation** — Name, personality, tools are bundled together
2. **Autonomy** — You give it a task, it decides what tools to use
3. **Composability** — You can create multiple agents with different roles

## Run It

```bash
cd chapter_05_simple_agent
python main.py
```

**💡 Key Takeaway:** An Agent = System Prompt + Tools + Agentic Loop. That's it. The system prompt defines WHO it is, the tools define WHAT it can do, and the loop defines HOW it works.

---

# Chapter 6: The Agentic Loop

> **Goal:** Build a robust, production-ready agent loop with safety features.

## The Five-Step Loop

```
    ┌──────────────────────────────────────────────┐
    │              THE AGENTIC LOOP                │
    │                                              │
    │  ┌────────┐                                  │
    │  │ THINK  │  Call the model with context      │
    │  └───┬────┘                                  │
    │      │                                       │
    │  ┌───▼────┐                                  │
    │  │ DECIDE │  Tool calls or text response?     │
    │  └───┬────┘                                  │
    │      │                                       │
    │  ┌───▼────┐                                  │
    │  │  ACT   │  Execute the tool functions       │
    │  └───┬────┘                                  │
    │      │                                       │
    │  ┌───▼────┐                                  │
    │  │OBSERVE │  Feed results back to model       │
    │  └───┬────┘                                  │
    │      │                                       │
    │  ┌───▼────┐       ┌──────────┐               │
    │  │ CHECK  ├──YES──► COMPLETE │               │
    │  └───┬────┘       └──────────┘               │
    │      │ NO                                    │
    │      └────────────── loop ──────────────────►│
    └──────────────────────────────────────────────┘
```

## Three Improvement over Chapter 5

### 1. Max Iterations (Safety Valve)
```python
max_iterations = 10
for iteration in range(max_iterations):
    # ... loop body ...
# If we get here, the agent ran too long → stop safely
```

### 2. Explicit Completion Tool
```python
# The agent calls this when it's DONE
{"name": "task_complete", "parameters": {"result": "Here is my analysis..."}}
```
This is better than just "no more tool calls" because:
- The agent explicitly decides it's done
- It provides a structured final result

### 3. Error Recovery
```python
try:
    result = execute_tool(name, args)
except Exception as e:
    result = {"error": str(e)}  # Agent sees the error and can recover
```

## Run It

```bash
cd chapter_06_agentic_loop
python main.py
```

**💡 Key Takeaway:** The agentic loop IS the agent. Everything else — the system prompt, the tools, the model — are inputs to this loop. Master this pattern and you can build any agent.

---

# Chapter 7: Multi-Agent CLI Project

> **Goal:** Build a complete software development system with 4 specialized agents working together.

This is the capstone. Everything from Chapters 1–6 comes together here.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                             │
│  Manages the pipeline and routes data between agents         │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐   ┌────────┐  │
│  │ Clarifier│───►│PRD Agent │───►│ Planner  │──►│ Coder  │  │
│  │          │    │          │    │ (Master) │   │        │  │
│  └────┬─────┘    └──────────┘    └──────────┘   └────────┘  │
│       │                                                      │
│       ▼                                                      │
│  User Feedback                                               │
│  Loop                                                        │
└──────────────────────────────────────────────────────────────┘
```

## The Pipeline

### Phase 1: Clarification
```
User: "Build a todo app"
  │
  ▼
Clarifier Agent:
  "Here's what I understand you want:
   1. A command-line todo application
   2. Features: add, list, complete, delete tasks
   3. Persistence: save to JSON file
   4. Tech: Python with argparse
   
   Is this correct? (yes / no / edit)"
  │
  ▼
User: "yes" or "add priority levels"
```

### Phase 2: PRD Generation
```
Approved Spec
  │
  ▼
PRD Agent produces:
  - FR-1: Add task with title and priority
  - FR-2: List tasks with filters
  - FR-3: Mark task as complete
  - FR-4: Delete task
  - File structure, implementation order...
```

### Phase 3: Task Planning & Code Generation
```
PRD Document
  │
  ▼
Planner breaks into tasks:
  Task 1: Create project structure     → Coder
  Task 2: Implement data model         → Coder
  Task 3: Implement CLI interface       → Coder
  Task 4: Add persistence              → Coder
  Task 5: Integration & testing        → Coder
```

## The Framework (Built from Scratch)

### BaseAgent (`framework/base_agent.py`)
```python
class BaseAgent:
    """Every agent inherits from this."""
    
    def __init__(self, client, name, system_prompt, model, max_iterations, color):
        self.tool_registry = ToolRegistry()  # Each agent has its own tools
    
    def run(self, task: str) -> str:
        """The agentic loop — same pattern from Chapter 6."""
    
    def pre_run(self, task):    # Hook: modify task before processing
    def post_run(self, result): # Hook: modify result before returning
```

### ToolRegistry (`framework/tool_registry.py`)
```python
class ToolRegistry:
    """Manages tool registration and execution."""
    
    def register(self, name, description, parameters, func):
        """Register a Python function as a tool."""
    
    def get_schemas(self) -> list[dict]:
        """Get OpenAI-compatible tool schemas."""
    
    def execute(self, name, arguments) -> any:
        """Execute a tool by name."""
```

### MessageBus (`framework/message_bus.py`)
```python
class MessageBus:
    """Structured inter-agent communication."""
    
    def send(self, sender, receiver, msg_type, content):
    def receive(self, receiver, msg_type=None):
    def get_conversation(self, agent_a, agent_b):
```

### Orchestrator (`framework/orchestrator.py`)
```python
class Orchestrator:
    """Controls the pipeline: Clarifier → PRD → Planner → Coder."""
    
    def register_agent(self, name, agent):
    def run(self, user_input):    # Executes the full pipeline
```

## The Tools (Built from Scratch)

### File Tools (`tools/file_tools.py`)
| Tool | Description |
|------|-------------|
| `read_file(path)` | Read a file's contents |
| `write_file(path, content)` | Write content to a file (auto-creates dirs) |
| `list_directory(path)` | List files and directories |
| `create_directory(path)` | Create directories recursively |

### Shell Tools (`tools/shell_tools.py`)
| Tool | Description |
|------|-------------|
| `run_command(command, cwd)` | Execute a shell command (30s timeout, danger blocking) |

### Search Tools (`tools/search_tools.py`)
| Tool | Description |
|------|-------------|
| `search_files(directory, pattern)` | Find files by name pattern |
| `grep_in_file(file_path, search_term)` | Search inside a file |

## The Agents

### 1. Clarifier Agent
- **Role:** Requirements analyst
- **Input:** Raw user idea
- **Output:** Detailed specification
- **Special:** Includes user feedback loop

### 2. PRD Agent
- **Role:** Product manager
- **Input:** Approved specification
- **Output:** Formal PRD with numbered functional requirements

### 3. Planner Agent (Master)
- **Role:** Technical project manager
- **Input:** PRD document  
- **Output:** Ordered task list
- **Special:** Has `assign_task_to_coder` tool — delegates each task to the Coder agent

### 4. Coder Agent
- **Role:** Software developer
- **Input:** Individual coding task
- **Output:** Working code files
- **Tools:** All file, shell, and search tools

## Run It

```bash
cd chapter_07_multi_agent_project

# With a command-line argument
python main.py "Build a simple calculator in Python"

# Or interactive mode
python main.py
```

## Example Session

```
══════════════════════════════════════════════════════════════
  MULTI-AGENT SOFTWARE DEVELOPMENT SYSTEM
══════════════════════════════════════════════════════════════
  Input: Build a todo app with Flask

──────────────────────────────────────────────────────────────
  Phase 1: Requirement Clarification
──────────────────────────────────────────────────────────────

[Clarifier] 📋 Task received
[Clarifier] 🔄 Iteration 1/5
[Clarifier] ✅ Task complete!

══════════════════════════════════════════════════════════════
  ELABORATED SPECIFICATION
══════════════════════════════════════════════════════════════
  # Todo App with Flask
  ## Purpose
  A web-based task management application...
  ## Features
  1. Create, read, update, delete todos
  2. Priority levels (low, medium, high)
  ...
══════════════════════════════════════════════════════════════

Is this specification correct? (yes / no / type your edits): yes
  ✅ Specification approved!

──────────────────────────────────────────────────────────────
  Phase 2: PRD Generation  
──────────────────────────────────────────────────────────────

[PRD Agent] 📋 Task received
[PRD Agent] ✅ Task complete!

──────────────────────────────────────────────────────────────
  Phase 3: Task Planning & Code Generation
──────────────────────────────────────────────────────────────

[Planner] 📋 Task received
[Planner] 📌 Task 1: Project Setup
[Coder]   🔧 create_directory(path='output/todo_app')
[Coder]   🔧 write_file(path='output/todo_app/requirements.txt', ...)
[Coder]   ✅ Task complete!
[Planner] ✅ Task 1 completed by Coder

[Planner] 📌 Task 2: Database Models
[Coder]   🔧 write_file(path='output/todo_app/models.py', ...)
[Coder]   ✅ Task complete!
[Planner] ✅ Task 2 completed by Coder

...

══════════════════════════════════════════════════════════════
  ALL PHASES COMPLETE
══════════════════════════════════════════════════════════════

📁 Output files written to: .../output
```

---

## Concepts Progression Map

```
Chapter 1         Chapter 2         Chapter 3         Chapter 4
───────────       ───────────       ───────────       ───────────
Single call  ──►  Multi-turn   ──►  Tool calling  ──► Chat + Tools
                  + Streaming       (single-shot)     (multi-turn)
    │                 │                  │                  │
    │                 │                  │                  │
    ▼                 ▼                  ▼                  ▼
messages=[]     conversation        tool schemas      inner tool loop
                  history           function map
                                                           │
                                                           │
Chapter 5         Chapter 6         Chapter 7              │
───────────       ───────────       ───────────            │
Agent class  ──►  Agentic Loop ──►  Multi-Agent   ◄────────┘
                  + Safety          System
    │                 │                  │
    ▼                 ▼                  ▼
encapsulation    max iterations     4 agents
run(task)        task_complete      framework
autonomy         error recovery    tools (from scratch)
                                   orchestrator
```

---

## What's Next?

Once you understand this system, you can extend it:

1. **Add memory** — Store conversation history across sessions using a database
2. **Add RAG** — Give agents access to documentation via embeddings and vector search
3. **Add more agents** — Tester agent, reviewer agent, documentation agent
4. **Add more tools** — Git operations, HTTP requests, database queries
5. **Add parallelism** — Run independent coding tasks in parallel
6. **Add a web UI** — Replace the CLI with a real-time web dashboard
7. **Use better models** — Switch from `gpt-4o-mini` to `gpt-4o` or `o1` for complex reasoning

---

*Built with ❤️ as a learning resource. Every line of code is meant to be read, understood, and modified.*
