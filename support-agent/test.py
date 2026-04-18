import json
from agent import SupportAgent
from concurrent.futures import ThreadPoolExecutor

agent = SupportAgent()

with open("data/tickets.json") as f:
    tickets = json.load(f)

# 🚀 CONCURRENT PROCESSING
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(agent.process_ticket, tickets)

# Save logs after all
agent.save_logs()

print("✅ All tickets processed with concurrency")