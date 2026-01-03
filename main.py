import json
import os
from datetime import datetime
from random import choice

class CallSession:
    def __init__(self):
        self.state = {
            "session_id": f"CALL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "caller_id": None,
            "verified": False,
            "intent": None,
            "issue_description": "",
            "steps_tried": [],
            "sentiment": "neutral",
            "conversation_history": [],
            "retrieved_docs": [],
            "incident_details": {}
        }
    
    def update(self, key, value):
        """Update a state field and log it"""
        self.state[key] = value
        print(f"[STATE UPDATE] {key}: {value}")
    
    def add_message(self, role, content):
        """Add to conversation history"""
        self.state["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_handoff_summary(self):
        """Generate the agent handoff summary"""
        incident_info = ""
        if self.state["incident_details"]:
            incident_info = "\nINCIDENT DETAILS:\n"
            for key, value in self.state["incident_details"].items():
                incident_info += f"  {key}: {value}\n"
        
        summary = f"""
========================================
AGENT HANDOFF SUMMARY
========================================
Session ID: {self.state['session_id']}
Caller: {self.state['caller_id'] or 'Unknown'}
Verified: {'✓ YES' if self.state['verified'] else '✗ NO'}

CUSTOMER GOAL:
{self.state['intent'] or 'Not determined'}

ISSUE DESCRIPTION:
{self.state['issue_description'] or 'No details provided'}
{incident_info}
STEPS ATTEMPTED:
{chr(10).join(f'  - {step}' for step in self.state['steps_tried']) if self.state['steps_tried'] else '  None'}

RETRIEVED KNOWLEDGE BASE ARTICLES:
{chr(10).join(f'  - {doc}' for doc in self.state['retrieved_docs']) if self.state['retrieved_docs'] else '  None'}

CONVERSATION TURNS: {len(self.state['conversation_history'])}
SENTIMENT: {self.state['sentiment']}

RECOMMENDED NEXT ACTION:
[Agent to determine based on above context]
========================================
"""
        return summary
    
    def display_state(self):
        """Pretty print current state"""
        print("\n--- Current Session State ---")
        print(json.dumps(self.state, indent=2, default=str))
        print("-----------------------------\n")


class KnowledgeBase:
    def __init__(self, kb_dir="kb"):
        self.kb_dir = kb_dir
        self.docs = {}
        self.load_documents()
    
    def load_documents(self):
        """Load all markdown files from kb directory"""
        if not os.path.exists(self.kb_dir):
            print(f"Warning: {self.kb_dir} directory not found")
            return
        
        for filename in os.listdir(self.kb_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.kb_dir, filename)
                with open(filepath, 'r') as f:
                    self.docs[filename] = f.read()
        
        print(f"[KB] Loaded {len(self.docs)} documents\n")
    
    def retrieve(self, intent, issue_description=""):
        """Simple keyword-based retrieval"""
        intent_to_doc = {
            "file_claim": "claim-filing.md",
            "billing": "billing-payment.md",
            "roadside": "roadside-assistance.md",
            "policy_change": "billing-payment.md"
        }
        
        doc_name = intent_to_doc.get(intent)
        
        if doc_name and doc_name in self.docs:
            return {
                "doc_name": doc_name,
                "content": self.docs[doc_name],
                "relevance": "high"
            }
        
        return None
    
    def get_snippet(self, doc_name, max_lines=15):
        """Get a snippet of a document for display"""
        if doc_name not in self.docs:
            return None
        
        lines = self.docs[doc_name].split('\n')
        snippet = '\n'.join(lines[:max_lines])
        if len(lines) > max_lines:
            snippet += "\n\n[... see full article for more details ...]"
        return snippet


def verify_caller(session):
    """Simulate caller verification"""
    print("\n--- CALLER VERIFICATION ---")
    policy_num = input("Please enter your policy number: ")
    
    # Simulate verification (any input with 6+ chars = valid)
    if len(policy_num) >= 6:
        session.update("caller_id", policy_num)
        session.update("verified", True)
        session.add_message("user", f"Provided policy number: {policy_num}")
        session.add_message("system", "Caller verified successfully")
        print("✓ Verified. Thank you.\n")
        return True
    else:
        print("✗ Invalid policy number. Continuing without verification.\n")
        session.add_message("system", "Verification failed")
        return False


def collect_claim_details(session):
    """Collect specific claim information"""
    print("\nI'll need a few details to help with your claim:\n")
    
    when = input("When did this happen? (e.g., 'yesterday', 'this morning'): ")
    session.state["incident_details"]["when"] = when
    session.add_message("user", f"Incident occurred: {when}")
    
    where = input("Where did this occur? (city/location): ")
    session.state["incident_details"]["where"] = where
    session.add_message("user", f"Location: {where}")
    
    damage = input("What damage occurred? (brief description): ")
    session.state["incident_details"]["damage"] = damage
    session.add_message("user", f"Damage: {damage}")
    
    photos = input("Do you have photos of the damage? (yes/no): ")
    session.state["incident_details"]["photos_available"] = photos.lower()
    session.add_message("user", f"Photos available: {photos}")
    
    if photos.lower() == 'yes':
        session.state["steps_tried"].append("Took photos of damage")


def collect_billing_details(session):
    """Collect billing issue details"""
    print("\nWhat billing issue can I help with?\n")
    print("1. Make a payment")
    print("2. Payment arrangement/extension")
    print("3. Question about my bill")
    
    choice = input("Selection (1-3): ")
    
    billing_map = {
        "1": "make_payment",
        "2": "payment_arrangement",
        "3": "billing_question"
    }
    
    session.state["incident_details"]["billing_type"] = billing_map.get(choice, "other")
    session.add_message("user", f"Billing issue type: {billing_map.get(choice, 'other')}")
    
    if choice == "2":
        reason = input("Can you briefly explain why you need an arrangement? ")
        session.state["incident_details"]["arrangement_reason"] = reason
        session.add_message("user", f"Reason: {reason}")


def collect_roadside_details(session):
    """Collect roadside assistance details"""
    print("\nLet me get details about your situation:\n")
    
    location = input("What's your current location? ")
    session.state["incident_details"]["location"] = location
    session.add_message("user", f"Location: {location}")
    
    issue = input("What's wrong with your vehicle? (e.g., flat tire, won't start): ")
    session.state["incident_details"]["vehicle_issue"] = issue
    session.add_message("user", f"Issue: {issue}")
    
    safety = input("Are you in a safe location? (yes/no): ")
    session.state["incident_details"]["safe"] = safety.lower()
    session.add_message("user", f"Safe location: {safety}")
    
    if safety.lower() == "no":
        session.update("sentiment", "urgent")
    

def main():
    """Enhanced IVR simulator"""
    session = CallSession()
    kb = KnowledgeBase()
    
    print("=== GEICO IVR Simulator ===\n")
    
    # Step 1: Verify caller
    verify_caller(session)
    
    # Step 2: Intent selection
    print("Please select an option:")
    print("1. File a claim")
    print("2. Billing and payments")
    print("3. Roadside assistance")
    print("4. Policy changes")
    
    choice = input("\nYour selection (1-4): ")
    choice = choice.strip()   

    intent_map = {
        "1": "file_claim",
        "2": "billing",
        "3": "roadside",
        "4": "policy_change"
    }
    
    intent = intent_map.get(choice, "unknown")
    session.update("intent", intent)
    session.add_message("user", f"Selected option {choice}")
    
    # Step 3: Get initial description
    
    intent_prompts = {
    "file_claim": "\nI'll help you file a claim. Briefly, what happened?",
    "billing": "\nI can help with billing.",
    "roadside": "\nI'll get you roadside help. What's your situation?",
    "policy_change": "\nWhat would you like to change about your policy?"
    }


    if intent in intent_prompts:
        if intent != "billing":  # billing has its own flow
            issue = input(intent_prompts[intent] + " ")
            session.update("issue_description", issue)
            session.add_message("user", issue)
    
    # Step 4: Retrieve KB document
    print("\n[SYSTEM] Retrieving relevant information...")
    doc_info = kb.retrieve(intent)
    
    if doc_info:
        session.state["retrieved_docs"].append(doc_info["doc_name"])
        print(f"\n📄 Retrieved: {doc_info['doc_name']}")
        snippet = kb.get_snippet(doc_info["doc_name"])
        if snippet:
            print("\n" + "─" * 60)
            print(snippet)
            print("─" * 60)
    
    # Step 5: Collect intent-specific details
    print()
    if intent == "file_claim":
        collect_claim_details(session)
    elif intent == "billing":
        collect_billing_details(session)
    elif intent == "roadside":
        collect_roadside_details(session)
    
    # Step 6: Next action
    print("\n" + "="*60)
    print("Based on the information you've provided:")
    print("1. Continue and complete this on your own")
    print("2. Transfer to a specialist agent")
    
    next_action = input("\nYour choice (1-2): ")
    session.add_message("user", f"Selected option {next_action}")

    if next_action == "2":
        print("\n[SYSTEM] Transferring to agent...")
        print("[SYSTEM] Preparing handoff summary...\n")
        if session.state["sentiment"] != "urgent":
            session.update("sentiment", "needs_agent")
    else:
        print("\n[SYSTEM] Proceeding with self-service...\n")
        session.state["steps_tried"].append("Attempted self-service completion")
    
    # Show handoff
    print(session.generate_handoff_summary())


if __name__ == "__main__":
    main()