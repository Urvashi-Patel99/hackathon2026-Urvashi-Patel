from tools import *
from llm import ask_llm
import json
import re

# -------------------------
# SAFE JSON PARSER
# -------------------------
def parse_llm_output(output):
    try:
        return json.loads(output)
    except:
        return {
            "thought": "invalid json fallback",
            "action": "search_knowledge_base",
            "input": {}
        }

# -------------------------
# TOOL REGISTRY
# -------------------------
TOOLS = {
    "get_order": get_order,
    "check_refund_eligibility": check_refund_eligibility,
    "issue_refund": issue_refund,
    "send_reply": send_reply,
    "search_knowledge_base": search_knowledge_base,
    "escalate": escalate
}

class SupportAgent:

    def __init__(self):
        self.logs = []
        self.memory = {}   # 🧠 MEMORY STORE (ticket-wise)

    def extract_order_id(self, text):
        match = re.search(r"ORD-\d+", text)
        return match.group(0) if match else None

    def classify(self, text):
        text = text.lower()

        if "refund" in text:
            return "refund"
        elif "return" in text:
            return "return"
        elif "cancel" in text:
            return "cancel"
        elif "order" in text:
            return "order_status"
        else:
            return "unknown"

    # -------------------------
    # MEMORY HELPER
    # -------------------------
    def get_memory(self, ticket_id):
        if ticket_id not in self.memory:
            self.memory[ticket_id] = []
        return self.memory[ticket_id]

    def add_memory(self, ticket_id, data):
        self.get_memory(ticket_id).append(data)

    # -------------------------
    # MAIN ENGINE
    # -------------------------
    def process_ticket(self, ticket):
        try:
            text = ticket["subject"] + " " + ticket["body"]
            ticket_id = ticket["ticket_id"]

            reasoning = []
            memory = self.get_memory(ticket_id)

            # -------------------------
            # STEP 1: CLASSIFICATION
            # -------------------------
            category = self.classify(text)
            confidence = 0.9 if category != "unknown" else 0.3
            order_id = self.extract_order_id(text)

            reasoning.append(f"Classified: {category}")
            reasoning.append(f"Confidence: {confidence}")

            # 🧠 store memory
            self.add_memory(ticket_id, {
                "user_input": text,
                "category": category,
                "confidence": confidence
            })

            action = None

            # -------------------------
            # STEP 2: RULE PATH
            # -------------------------
            if confidence >= 0.5:
                action = category

            # -------------------------
            # STEP 3: LLM + REACT + MEMORY
            # -------------------------
            else:
                context = f"Ticket: {text}\n"

                # 🧠 inject past memory
                context += f"\nPrevious Memory: {json.dumps(memory)}\n"

                reasoning_steps = []

                for step in range(3):

                    prompt = f"""
You are an AI support agent.

Use past memory + context to decide best tool.

Context:
{context}

Available tools:
{list(TOOLS.keys())}

Return ONLY valid JSON:

{{
  "thought": "reasoning",
  "action": "tool_name",
  "input": {{
    "order_id": "{order_id if order_id else ''}",
    "query": "optional",
    "message": "optional",
    "amount": 100
  }}
}}
"""

                    output = ask_llm(prompt)
                    parsed = parse_llm_output(output)

                    selected_tool = parsed.get("action")
                    tool_input = parsed.get("input", {})
                    thought = parsed.get("thought", "")

                    reasoning.append(f"LLM: {thought}")
                    reasoning.append(f"Tool: {selected_tool}")

                    reasoning_steps.append(parsed)

                    if selected_tool not in TOOLS:
                        break

                    try:
                        if selected_tool == "send_reply":
                            result = TOOLS[selected_tool](
                                ticket_id,
                                tool_input.get("message", "Processed")
                            )
                            action = "llm_reply"
                            break

                        elif selected_tool == "escalate":
                            result = TOOLS[selected_tool](
                                ticket_id,
                                tool_input.get("message", "Escalated"),
                                tool_input.get("priority", "medium")
                            )
                            action = "llm_escalated"
                            break

                        elif selected_tool == "get_order":
                            result = TOOLS[selected_tool](order_id)

                        elif selected_tool == "check_refund_eligibility":
                            result = TOOLS[selected_tool](order_id)

                        elif selected_tool == "issue_refund":
                            result = TOOLS[selected_tool](order_id, 100)

                        elif selected_tool == "search_knowledge_base":
                            result = TOOLS[selected_tool](text)

                        else:
                            result = "invalid tool"

                    except Exception as e:
                        result = str(e)

                    # -------------------------
                    # 🧠 STORE MEMORY PER STEP
                    # -------------------------
                    self.add_memory(ticket_id, {
                        "step": step,
                        "tool": selected_tool,
                        "result": str(result)
                    })

                    context += f"\nObservation: {result}"

                reasoning.append({"react_steps": reasoning_steps})
                action = action or "llm_handled"

            # -------------------------
            # STEP 4: RULE EXECUTION
            # -------------------------
            if action == "refund":
                if not order_id:
                    escalate(ticket_id, "Missing order ID", "medium")
                    return "no_order_id"

                try:
                    eligibility = check_refund_eligibility(order_id)
                except:
                    eligibility = {"eligible": False}

                if eligibility["eligible"]:
                    issue_refund(order_id, 100)
                    send_reply(ticket_id, "Refund processed successfully.")
                    action_taken = "refund_success"
                else:
                    send_reply(ticket_id, "Refund not eligible.")
                    action_taken = "refund_denied"

            elif action == "order_status":
                order = get_order(order_id)
                send_reply(ticket_id, f"Order status: {order['status']}")
                action_taken = "order_checked"

            elif action == "cancel":
                send_reply(ticket_id, "Order cancelled successfully.")
                action_taken = "cancelled"

            elif action == "return":
                send_reply(ticket_id, "Return initiated.")
                action_taken = "return_initiated"

            else:
                kb = search_knowledge_base(text)
                send_reply(ticket_id, kb)
                action_taken = "kb_response"

            # -------------------------
            # FINAL LOG
            # -------------------------
            self.logs.append({
                "ticket_id": ticket_id,
                "category": category,
                "action": action_taken,
                "confidence": confidence,
                "memory": memory,
                "reasoning": reasoning,
                "status": "success"
            })

            return action_taken

        except Exception as e:
            escalate(ticket["ticket_id"], str(e), "high")

            self.logs.append({
                "ticket_id": ticket["ticket_id"],
                "error": str(e),
                "status": "failed"
            })

            return "error"

    # -------------------------
    # SAVE LOGS
    # -------------------------
    def save_logs(self):
        with open("audit_log.json", "w") as f:
            json.dump(self.logs, f, indent=2)