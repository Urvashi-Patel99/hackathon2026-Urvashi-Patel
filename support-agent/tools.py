import random

def get_customer(email):
    return {"email": email, "tier": "standard"}

def get_order(order_id):
    return {"order_id": order_id, "status": "shipped"}

def check_refund_eligibility(order_id):
    if random.random() < 0.2:
        raise Exception("Refund service timeout")
    return {"eligible": True}

def issue_refund(order_id, amount):
    return {"status": "success"}

def send_reply(ticket_id, message):
    print(f"[REPLY] {ticket_id}: {message}")

def escalate(ticket_id, summary, priority):
    print(f"[ESCALATE] {ticket_id} | {priority} | {summary}")

def search_knowledge_base(query):
    return f"Policy result for: {query}"    