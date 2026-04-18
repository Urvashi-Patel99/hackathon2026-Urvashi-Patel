🧠 AI Support Agent (LLM + Tool-Using System)

An intelligent AI-powered customer support agent that can automatically classify tickets, reason step-by-step, and execute tools like order lookup, refunds, and escalation using an LLM + rule-based hybrid system.

🚀 Features
🧾 Automatic ticket classification (refund, cancel, return, order status)
🧠 Hybrid reasoning (Rule-based + LLM ReAct loop)
🔧 Tool execution system (function calling style)
🧠 Memory per ticket (conversation + reasoning history)
🔁 Multi-step agent loop (LLM can iterate up to 3 steps)
📊 Structured logging for audit and debugging
⚡ Safe JSON parsing with fallback handling
🛑 Automatic escalation on failure or missing data


🏗️ Architecture

Ticket Input
     ↓
Rule-based Classifier
     ↓
Confidence Check
     ↓
 ┌───────────────┐
 │  High Confidence│ → Direct tool execution
 └───────────────┘
     ↓ (else)
LLM Reasoning Loop (ReAct)
     ↓
Tool Selection → Execution → Observation Loop
     ↓
Final Response + Logging


🧰 Available Tools

The agent can use the following tools:

get_order(order_id) → Fetch order details
check_refund_eligibility(order_id) → Check refund eligibility
issue_refund(order_id, amount) → Process refund
send_reply(ticket_id, message) → Send response to customer
search_knowledge_base(query) → Retrieve help articles
escalate(ticket_id, summary, priority) → Escalate to human agent

📦 Project Structure

project/
│
├── agent.py              # Main SupportAgent logic
├── tools.py             # External tool implementations
├── llm.py               # LLM wrapper (ask_llm)
├── audit_log.json       # Logs generated after execution
└── README.md


project/
│
├── agent.py              # Main SupportAgent logic
├── tools.py             # External tool implementations
├── llm.py               # LLM wrapper (ask_llm)
├── audit_log.json       # Logs generated after execution
└── README.md

project/
│
├── agent.py              # Main SupportAgent logic
├── tools.py             # External tool implementations
├── llm.py               # LLM wrapper (ask_llm)
├── audit_log.json       # Logs generated after execution
└── README.md

⚙️ How It Works

1. Rule-Based Classification

The system first classifies the ticket:

refund
return
cancel
order_status
unknown
2. Confidence Scoring
High confidence → direct execution
Low confidence → LLM reasoning loop
3. LLM ReAct Loop

The LLM:

Thinks
Chooses a tool
Observes result
Repeats (max 3 steps)

4. Tool Execution

Selected tools are executed dynamically using:
TOOLS[action](**params)

🧠 Memory System

Each ticket maintains memory:

User input
Classification result
Tool execution history
Observations from each step

This improves reasoning across multi-step tasks.

📊 Logging

All actions are stored in:

audit_log.json

Includes:

Ticket ID
Category
Action taken
Confidence score
Reasoning steps
Status (success/failure)

🧪 Example Flow

Input:

"I want a refund for order ORD-12345"

Agent Flow:

Classify → refund
Extract order ID → ORD-12345
Check eligibility
Issue refund
Send reply

⚠️ Error Handling
Missing order ID → Escalation
Invalid LLM JSON → fallback parser
Tool failure → captured in logs
Unknown intent → knowledge base lookup
🔮 Future Improvements
Persistent long-term memory (customer-level)
Function-calling API (no prompt parsing)
Real-time dashboard (agent visualization)
Multi-agent system (specialized agents per task)
Vector DB knowledge base integration

🛠️ Requirements
pip install openai

▶️ Run
python test.py