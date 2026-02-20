# Day 1 – LLM Fundamentals & Chat Implementations

## 📚 Purpose of Day 1

This folder introduces **core Large Language Model (LLM) concepts** through **progressively more advanced chat examples**. Each script builds upon the previous one, introducing new concepts and capabilities.

By the end of Day 1, you will understand:

* How LLMs receive and generate messages
* How conversations are represented as message arrays
* How "memory" is simulated in chat applications
* What tokens, context windows, and hallucinations are
* How chat history can be persisted and resumed
* How to implement practical features like summarization and knowledge graphs

---

## 🎯 Learning Objectives

### Conceptual Understanding
- [ ] Understand LLM statelessness
- [ ] Grasp the message array structure
- [ ] Recognize the difference between real and simulated memory
- [ ] Identify token limitations and their implications

### Technical Skills
- [ ] Create basic LLM API calls
- [ ] Build interactive chat applications
- [ ] Implement persistent storage
- [ ] Resume previous conversations
- [ ] Apply advanced features (summarization, knowledge graphs)

---

## 🛠️ Prerequisites & Setup

### Global Environment (Required)

All examples in `day1/` assume that **dependencies are installed in the global repository environment**.

From the **repository root**:

```bash
python -m venv .venv
source .venv/bin/activate   # mac
Windows: .venv\Scripts\Activate #windows
pip install -r requirements.txt
```

### Required Environment Variables

Create a `.env` file at the repository root and copy the .env.example file into it or :

```env
OPENAI_API_KEY="<PASTE_YOUR_API_KEY_HERE>"
OPENAI_MODEL="mistralai/devstral-2512:free"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
```

> **Security Note:** Never commit `.env` files to version control. Add `.env` to your `.gitignore` file.

---

## 📁 Folder Structure (Day 1)

```text
day1/
├── README.md          # This file
├── test1.py           # Single prompt, single response
├── test2.py           # Interactive chat (in-memory)
├── test3.py           # Interactive chat with persistence
├── test4.py           # Resume previous chat sessions
├── exercises/         # Practice exercises
│   ├── exercise1.py   # Chat summarization
│   ├── exercise2.py   # Token counter
│   └── exercise3.py   # Knowledge graph builder
└── chats/             # Auto-created chat history (JSON)
    ├── 1.json
    ├── 2.json
    └── ...
```

---

## 🧠 Core Concept: Messages Array

All examples revolve around this fundamental structure:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you today?"},
    {"role": "user", "content": "Tell me about Python."}
]
```

### Roles Explained

| Role        | Purpose                                      | Required? |
|-------------|----------------------------------------------|-----------|
| `system`    | Sets behavior, tone, rules, and personality  | Optional but recommended |
| `user`      | Human input (questions, commands, prompts)   | Required |
| `assistant` | Model-generated responses                    | Added after each response |

### Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Your Application                                           │
│                                                             │
│  messages = [                                               │
│    {"role": "system", "content": "..."},                    │
│    {"role": "user", "content": "Hello"}                     │
│  ]                                                          │
│                                                             │
│  ↓ Send entire messages array                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  OpenAI API                                                 │
│  - Processes all messages                                   │
│  - Generates response based on full context                 │
│  - Returns assistant message                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Your Application                                           │
│                                                             │
│  messages.append({                                          │
│    "role": "assistant",                                     │
│    "content": "Hi! How can I help?"                         │
│  })                                                         │
│                                                             │
│  Next turn: send updated messages array ↻                   │
└─────────────────────────────────────────────────────────────┘
```

> **Critical Insight:**
> The LLM does **not** remember anything by itself.
> The *entire messages array* is sent on **every request**.
> You are manually creating the illusion of memory.

---

## 📝 Script Breakdown

### test1.py — Single Prompt, No Memory

**Complexity Level:** ⭐ Beginner

#### What It Does

* Sends a **single request** to the LLM
* No conversation state
* No persistence
* Demonstrates the most basic interaction

#### Code Structure

```python
# 1. Load environment variables
load_dotenv()

# 2. Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 3. Send a single request
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about Python."}
    ]
)

# 4. Print the response
print(response.choices[0].message.content)
```

#### Key Takeaway

> Each request is **completely stateless** unless you provide history.

#### When to Use This Pattern
- One-off text generation
- Batch processing of independent prompts
- Testing API connectivity
- Simple text transformations

---

### test2.py — Interactive Chat (In-Memory Memory)

**Complexity Level:** ⭐⭐ Intermediate

#### What It Does

* Creates a command-line chat interface
* Maintains conversation **in RAM only**
* Conversation is lost when the program exits
* Demonstrates manual memory management

#### How Memory Works Here

```python
# Start with system message
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# In the loop:
# 1. User sends message
messages.append({"role": "user", "content": user_input})

# 2. Send ENTIRE history to API
response = client.chat.completions.create(
    model=...,
    messages=messages  # Full conversation sent every time
)

# 3. Store assistant's response
messages.append({"role": "assistant", "content": assistant_message})
```

#### Memory Growth Pattern

```
Turn 1: [system]
Turn 2: [system, user1, assistant1]
Turn 3: [system, user1, assistant1, user2, assistant2]
Turn 4: [system, user1, assistant1, user2, assistant2, user3, assistant3]
...
```

#### Important Insights

1. **The LLM has no memory** — it only sees what you send in `messages`
2. **You simulate memory** by re-sending the entire conversation history
3. **Token cost grows** with each turn (more messages = more tokens)
4. **Context limits matter** — eventually the conversation will be too long

#### When to Use This Pattern
- Quick testing
- Short conversations
- Prototyping chat interfaces
- When persistence isn't needed

---

### test3.py — Persistent Chat (Saved to Disk)

**Complexity Level:** ⭐⭐⭐ Intermediate-Advanced

#### What It Does

* Same interactive chat as `test2.py`
* **Automatically saves** conversation to JSON after each turn
* Each session gets a unique file (`1.json`, `2.json`, etc.)
* Conversation survives program restarts

#### New Concepts Introduced

1. **File System Operations**
   ```python
   # Create chats directory if it doesn't exist
   os.makedirs(CHAT_DIR, exist_ok=True)
   ```

2. **Automatic File Naming**
   ```python
   # Find highest numbered file and increment
   next_index = max([int(f.split(".")[0]) for f in existing_files], default=0) + 1
   chat_file_path = os.path.join(CHAT_DIR, f"{next_index}.json")
   ```

3. **Incremental Persistence**
   ```python
   # Save after EVERY turn
   with open(chat_file_path, "w", encoding="utf-8") as f:
       json.dump(messages, f, indent=2, ensure_ascii=False)
   ```

#### Why JSON?

- **Human-readable** — you can open and inspect conversations
- **Structured** — matches the LLM message format directly
- **Portable** — easy to share, backup, or process
- **Flexible** — supports nested data for future enhancements

#### Example JSON Structure

```json
[
  {
    "role": "system",
    "content": "You are a helpful assistant."
  },
  {
    "role": "user",
    "content": "What is Python?"
  },
  {
    "role": "assistant",
    "content": "Python is a high-level programming language..."
  }
]
```

#### Key Takeaway

> "Memory" is an **application-level feature**, not a model capability.
> LLMs are stateless; persistence is your responsibility.

---

### test4.py — Resume Existing Chat Sessions

**Complexity Level:** ⭐⭐⭐ Advanced

#### What It Does

* Lists all saved chat sessions
* Allows user to select a specific session
* Loads that conversation from disk
* Continues chatting from that exact context
* Saves updates back to the same file

#### New Concepts Introduced

1. **Session Discovery**
   ```python
   # Find all numbered JSON files
   chat_files = sorted(
       f for f in os.listdir(CHAT_DIR)
       if f.endswith(".json") and f.split(".")[0].isdigit()
   )
   ```

2. **User Selection Interface**
   ```python
   # Validate user input
   while True:
       choice = input("Enter session number: ").strip()
       if choice.isdigit() and f"{choice}.json" in chat_files:
           break
       print("Invalid selection.")
   ```

3. **State Restoration**
   ```python
   # Load previous conversation
   with open(chat_file_path, "r", encoding="utf-8") as f:
       messages = json.load(f)
   ```

#### Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scan chats/ directory                                    │
│    ├── 1.json (about Python)                                │
│    ├── 2.json (recipe discussion)                           │
│    └── 3.json (code debugging)                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. User selects session 2                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Load 2.json → messages array                             │
│    [system, user1, assistant1, user2, assistant2]           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Continue conversation                                    │
│    User: "Can you add chocolate to that recipe?"            │
│    (LLM has full context from previous turns)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Save updated messages back to 2.json                     │
└─────────────────────────────────────────────────────────────┘
```

#### Key Concept Demonstrated

> The **illusion of long-term memory** is achieved by:
> 1. Saving conversations externally
> 2. Replaying previous messages when resuming
> 
> The model itself stores **nothing** between requests.

---

## 🎓 LLM Concepts Explained

### 1. Tokens

**Tokens are the fundamental units** LLMs process.

#### What Counts as a Token?

| Text | Tokens | Explanation |
|------|--------|-------------|
| "hello" | 1 | Common word |
| "ChatGPT" | 1 | Recognizable term |
| "unbelievable" | 3 | un + believ + able |
| "🎉" | 1-2 | Emojis vary |
| " " (space) | Often included with adjacent words | Whitespace handling varies |

#### Why Tokens Matter

1. **Cost**
   - APIs charge per token (input + output)
   - Example: gpt-4o-mini costs $0.15 per 1M input tokens

2. **Speed**
   - More tokens = longer processing time
   - Output tokens are generated sequentially

3. **Context Limits**
   - Models have maximum token capacity
   - Example: gpt-4o-mini supports 128K tokens

#### Practical Implications

```python
# Short conversation
messages = [
    {"role": "system", "content": "Be concise."},  # ~5 tokens
    {"role": "user", "content": "Hi"}              # ~2 tokens
]
# Total: ~7 tokens (very cheap, very fast)

# Long conversation
messages = [
    {"role": "system", "content": "..."},  # 100 tokens
    # ... 50 previous turns ...
    {"role": "user", "content": "..."}     # 200 tokens
]
# Total: ~5000+ tokens (more expensive, slower)
```

#### Token Estimation Tool

```python
# Rough estimation: 1 token ≈ 4 characters in English
def estimate_tokens(text):
    return len(text) // 4
```

For accurate counting, use the `tiktoken` library:

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")
tokens = encoding.encode("Your text here")
print(f"Token count: {len(tokens)}")
```

---

### 2. Context Window

The **context window** is the maximum number of tokens the model can process **in a single request**.

#### Context Window Sizes (Examples)

| Model | Context Window | Equivalent Text |
|-------|----------------|-----------------|
| gpt-4o-mini | 128,000 tokens | ~96,000 words / ~192 pages |
| gpt-4o | 128,000 tokens | ~96,000 words / ~192 pages |
| claude-sonnet-4 | 200,000 tokens | ~150,000 words / ~300 pages |

#### What's Included?

```
Total Tokens = System Prompt + User Messages + Assistant Responses + Current Input
```

#### What Happens When You Exceed It?

1. **Request fails** — API returns an error
2. **Automatic truncation** — Some APIs drop old messages (rare)
3. **You must handle it** — Most common approach

#### Managing Long Conversations

**Strategy 1: Message Pruning**
```python
# Keep only last N turns
MAX_TURNS = 10
if len(messages) > MAX_TURNS * 2 + 1:  # +1 for system message
    messages = [messages[0]] + messages[-(MAX_TURNS * 2):]
```

**Strategy 2: Summarization** (see Exercise 1)
```python
# Periodically summarize old messages
if len(messages) > 20:
    summary = summarize_conversation(messages[1:10])
    messages = [messages[0], {"role": "system", "content": summary}] + messages[10:]
```

**Strategy 3: Sliding Window**
```python
# Keep system + recent context
CONTEXT_SIZE = 4000  # tokens
current_tokens = count_tokens(messages)
while current_tokens > CONTEXT_SIZE:
    messages.pop(1)  # Remove oldest user/assistant message
    current_tokens = count_tokens(messages)
```

---

### 3. LLM Memory (What It Is NOT)

#### Common Misconception

❌ "The AI remembers our previous conversations"

#### Reality

✅ The application sends previous messages

✅ The LLM processes them like they're brand new

✅ No learning or retention occurs

#### Proof

```python
# Conversation 1
messages1 = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Nice to meet you, Alice!"}
]

# New conversation (fresh start)
messages2 = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What's my name?"}
]

# The LLM will NOT know your name in messages2
# It only sees what you send THIS time
```

#### What LLMs Cannot Do

- ❌ Remember past sessions (unless you provide the history)
- ❌ Learn from corrections during a conversation
- ❌ Store personal preferences across requests
- ❌ Access external databases or files (unless via tools/functions)

#### What Looks Like Memory

| Feature | How It Actually Works |
|---------|----------------------|
| "Remembers context" | You resend previous messages |
| "Knows my preferences" | You include preferences in system prompt |
| "Learned from feedback" | You update the message history |
| "Recalls earlier conversation" | Earlier messages are in the array |

---

### 4. Hallucinations

A **hallucination** occurs when the model generates **plausible-sounding but incorrect** information.

#### Examples

1. **Fake Citations**
   ```
   User: "Give me research on topic X"
   LLM: "According to Smith et al. (2023) in the Journal of..."
   Reality: Paper doesn't exist
   ```

2. **Invented APIs**
   ```
   User: "How do I use the XYZ library?"
   LLM: "Use the get_data() method"
   Reality: No such method exists
   ```

3. **Confident Errors**
   ```
   User: "What's the capital of Australia?"
   LLM: "Sydney" (Incorrect, it's Canberra)
   ```

#### Why Hallucinations Happen

1. **Prediction, Not Retrieval**
   - LLMs predict the next token based on patterns
   - They don't "look up" facts in a database

2. **Training Data Patterns**
   - Model learned "papers are cited this way"
   - Generates citation-like text without verifying truth

3. **Insufficient Context**
   - Missing information → model fills gaps with plausible guesses

#### Mitigation Strategies

**1. Clear Instructions**
```python
{
    "role": "system", 
    "content": "If you don't know something, say  'Idon't   know' instead of guessing."
}
```

**2. Request Citations**
```python
{
    "role": "user", 
    "content": "Provide sources for all factual claims."
}
```

**3. Verification Prompts**
```python
{
    "role": "user", 
    "content": "Are you certain about that? Double-check your answer."
}
```

**4. External Validation**
```python
# In your code
if response.contains_factual_claim():
    verified = verify_with_external_source(response)
```

**5. Temperature Control**
```python
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    messages=messages,
    temperature=0.0  # Lower = more deterministic, less creative
)
```

---

### 5. System Prompt Importance

The **system message** is your primary tool for controlling LLM behavior.

#### Basic Example

```python
{"role": "system", "content": "You are a helpful assistant."}
```

#### Advanced Examples

**Tone Control**
```python
{"role": "system", "content": "You are a professional technical writer. Use formal language, avoid slang, and structure responses with clear headings."}
```

**Safety Boundaries**
```python
{"role": "system", "content": "You are a math tutor for children. Never provide direct answers. Instead, guide students with hints and questions."}
```

**Output Format**
```python
{"role": "system", "content": "Always respond in JSON format with keys: 'answer', 'confidence', 'sources'."}
```

**Role-Playing**
```python
{"role": "system", "content": "You are Socrates. Respond to questions by asking counter-questions that encourage critical thinking."}
```

#### System Prompt Best Practices

1. **Be Specific**
   - ❌ "Be helpful"
   - ✅ "Provide step-by-step debugging help for Python code errors"

2. **Set Constraints**
   ```python
   "Responses must be under 100 words. Use bullet points for lists."
   ```

3. **Define Expertise**
   ```python
   "You are an expert in machine learning with 10 years of experience in computer vision."
   ```

4. **Handle Edge Cases**
   ```python
   "If asked about medical advice, respond: 'I cannot provide medical advice. Please consult a healthcare professional.'"
   ```

---

## 🏆 Exercises & Assignments

### Exercise 1: Chat Summarization (Intermediate)

**Goal:** Prevent context overflow by summarizing old messages.

**Requirements:**
1. Monitor conversation length
2. When messages exceed 15 turns, summarize the oldest 10
3. Replace summarized messages with a single summary message
4. Continue conversation with reduced context

**Starter Code:**

```python
def summarize_conversation(messages_to_summarize):
    """
    Uses the LLM to create a concise summary of old messages.
    """
    summary_prompt = [
        {"role": "system", "content": "Summarize the following conversation in 2-3 sentences."},
        {"role": "user", "content": json.dumps(messages_to_summarize)}
    ]
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=summary_prompt
    )
    
    return response.choices[0].message.content

# Implement in test3.py:
# - Check if len(messages) > 15
# - Summarize messages[1:11]
# - Replace with summary
# - Save updated messages
```

**Expected Output:**
```json
[
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "system", "content": "Previous conversation summary: User asked about Python basics, discussed loops and functions, then moved to file handling concepts."},
  {"role": "user", "content": "Tell me about classes"},
  ...
]
```

**Bonus Challenges:**
- Add a command `/summarize` to manually trigger summarization
- Calculate token savings
- Allow users to configure summary threshold

---

### Exercise 2: Token Counter & Budget Manager (Intermediate)

**Goal:** Track token usage and enforce conversation budgets.

**Requirements:**
1. Count tokens before each API call
2. Display running total to user
3. Warn when approaching token limit
4. Prevent requests that exceed budget

**Implementation Steps:**

```python
import tiktoken

# Initialize encoder
encoding = tiktoken.encoding_for_model("<specify the model>")

def count_tokens(messages):
    """Count total tokens in messages array."""
    total = 0
    for msg in messages:
        # Tokens per message: role + content + formatting
        total += len(encoding.encode(msg["content"]))
        total += 4  # Overhead per message
    total += 2  # Conversation formatting
    return total

# Usage in chat loop:
MAX_TOKENS = 4000
current_tokens = count_tokens(messages)

print(f"[Tokens: {current_tokens}/{MAX_TOKENS}]")

if current_tokens > MAX_TOKENS * 0.9:
    print("⚠️  Warning: Approaching token limit!")

if current_tokens > MAX_TOKENS:
    print("❌ Token limit exceeded. Please start a new conversation.")
    break
```

**Bonus Challenges:**
- Track cost (tokens × price per token)
- Show per-turn token usage
- Implement automatic pruning when limit reached
- Add `/tokens` command to show detailed breakdown

---

### Exercise 3: Knowledge Graph Builder (Advanced)

**Goal:** Extract and visualize relationships between topics discussed.

**Requirements:**
1. Parse conversations to identify entities (people, places, concepts)
2. Extract relationships between entities
3. Store graph in JSON format
4. Visualize connections

**Data Structure:**

```python
knowledge_graph = {
    "entities": [
        {"id": "python", "type": "language", "mentions": 5},
        {"id": "loops", "type": "concept", "mentions": 3},
        {"id": "django", "type": "framework", "mentions": 2}
    ],
    "relationships": [
        {"from": "python", "to": "loops", "type": "contains", "strength": 3},
        {"from": "django", "to": "python", "type": "built_with", "strength": 2}
    ]
}
```

**Implementation Approach:**

```python
def extract_entities(messages):
    """Use LLM to extract entities from conversation."""
    extraction_prompt = [
        {
            "role": "system",
            "content": "Extract key entities (topics, concepts, technologies) from this conversation. Return JSON with format: {\"entities\": [{\"name\": \"...\", \"type\": \"...\"}]}"
        },
        {
            "role": "user",
            "content": json.dumps(messages)
        }
    ]
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=extraction_prompt,
        response_format={"type": "json_object"}  # Force JSON output
    )
    
    return json.loads(response.choices[0].message.content)

def build_knowledge_graph(chat_file_path):
    """Build graph from saved conversation."""
    with open(chat_file_path, 'r') as f:
        messages = json.load(f)
    
    entities = extract_entities(messages)
    # TODO: Extract relationships
    # TODO: Count mentions
    # TODO: Calculate relationship strength
    
    return knowledge_graph
```

**Visualization (Simple Text-Based):**

```
Knowledge Graph for Session 1:
==============================

Entities:
  🐍 python (language) - 5 mentions
  🔄 loops (concept) - 3 mentions  
  🌐 django (framework) - 2 mentions

Relationships:
  python → loops (contains) ███
  django → python (built_with) ██
```

**Bonus Challenges:**
- Generate visual graph with networkx/matplotlib
- Link multiple conversations (cross-session knowledge)
- Implement graph search (`/search python`)
- Auto-suggest related topics

---

### Exercise 4: Conversation Interlinking (Advanced)

**Goal:** Create connections between related conversations.

**Requirements:**
1. Analyze all saved chats
2. Identify thematic similarities
3. Create reference links between related sessions
4. Build a conversation index

**Data Structure:**

```python
conversation_index = {
    "conversations": [
        {
            "id": 1,
            "summary": "Discussion about Python basics",
            "topics": ["python", "loops", "functions"],
            "related": [2, 5]  # IDs of related conversations
        },
        {
            "id": 2,
            "summary": "Advanced Python: decorators and generators",
            "topics": ["python", "decorators", "generators"],
            "related": [1, 3]
        }
    ]
}
```

**Implementation:**

```python
def analyze_conversation(messages):
    """Extract topics and generate summary."""
    analysis_prompt = [
        {
            "role": "system",
            "content": "Analyze this conversation. Return JSON: {\"summary\": \"...\", \"topics\": [\"...\"]}"
        },
        {"role": "user", "content": json.dumps(messages)}
    ]
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=analysis_prompt,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def find_related_conversations(current_topics, all_conversations):
    """Find conversations with overlapping topics."""
    related = []
    for conv in all_conversations:
        overlap = set(current_topics) & set(conv["topics"])
        if overlap:
            related.append({
                "id": conv["id"],
                "shared_topics": list(overlap),
                "score": len(overlap)
            })
    
    # Sort by relevance
    return sorted(related, key=lambda x: x["score"], reverse=True)
```

**User Interface:**

```
Session 2: Advanced Python Topics
==================================
Summary: Discussion of decorators, generators, and context managers

Related Conversations:
  📌 Session 1: Python Basics (shared: python, functions)
  📌 Session 5: Design Patterns (shared: python, decorators)

[C]ontinue | [V]iew Related | [N]ew Session
```

**Bonus Challenges:**
- Semantic similarity using embeddings (not just keyword matching)
- Auto-suggest related sessions when starting new chat
- Merge related conversations
- Generate cross-session summaries

---

## 🎯 Key Takeaways

### Technical Insights

1. **LLMs are stateless** — Every request is independent
2. **Memory is simulated** — By replaying message history
3. **Tokens define costs** — And operational limits
4. **Context window is finite** — Requires active management
5. **Persistence is your job** — LLMs don't save anything
6. **Hallucinations are inherent** — Validation is essential

### Architectural Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Message   │  │   Token    │  │ Knowledge  │             │
│  │ Management │  │  Tracking  │  │   Graph    │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Persistence Layer                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │   JSON     │  │   Index    │  │   Graph    │             │
│  │   Files    │  │   Files    │  │   Files    │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      LLM API                                │
│              (Stateless Request/Response)                   │
└─────────────────────────────────────────────────────────────┘
```

---

