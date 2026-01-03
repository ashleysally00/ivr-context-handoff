import gradio as gr
import json
from datetime import datetime
import os

# Import your existing classes
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
        self.current_step = "verification"
        self.intent_selected = False
        
    def update(self, key, value):
        self.state[key] = value
    
    def add_message(self, role, content):
        self.state["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_handoff_summary(self):
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


class KnowledgeBase:
    def __init__(self, kb_dir="kb"):
        self.kb_dir = kb_dir
        self.docs = {}
        self.load_documents()
    
    def load_documents(self):
        if not os.path.exists(self.kb_dir):
            return
        
        for filename in os.listdir(self.kb_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.kb_dir, filename)
                with open(filepath, 'r') as f:
                    self.docs[filename] = f.read()
    
    def retrieve(self, intent):
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
    
    def get_snippet(self, doc_name, max_lines=10):
        if doc_name not in self.docs:
            return None
        
        lines = self.docs[doc_name].split('\n')
        snippet = '\n'.join(lines[:max_lines])
        if len(lines) > max_lines:
            snippet += "\n\n[... see full article for more details ...]"
        return snippet


# Global variables
kb = KnowledgeBase()

def process_message(message, history, session_state):
    """Process user message and return bot response"""
    
    if session_state is None:
        session_state = {
            "session": CallSession(),
            "step": "verification",
            "intent_details": {}
        }
    
    session = session_state["session"]
    step = session_state["step"]
    
    # Add user message to history
    session.add_message("user", message)
    
    # Process based on current step
    if step == "verification":
        # Verify policy number
        if len(message.strip()) >= 6:
            session.update("caller_id", message.strip())
            session.update("verified", True)
            bot_response = "✓ Verified. Thank you!\n\nPlease select an option:\n1. File a claim\n2. Billing and payments\n3. Roadside assistance\n4. Policy changes"
            session_state["step"] = "intent_selection"
        else:
            bot_response = "✗ Invalid policy number. Continuing without verification.\n\nPlease select an option:\n1. File a claim\n2. Billing and payments\n3. Roadside assistance\n4. Policy changes"
            session_state["step"] = "intent_selection"
    
    elif step == "intent_selection":
        # Map user input to intent
        intent_map = {"1": "file_claim", "2": "billing", "3": "roadside", "4": "policy_change"}
        intent = intent_map.get(message.strip(), None)
        
        if intent:
            session.update("intent", intent)
            
            # Retrieve KB article
            doc_info = kb.retrieve(intent)
            if doc_info:
                session.state["retrieved_docs"].append(doc_info["doc_name"])
                snippet = kb.get_snippet(doc_info["doc_name"])
                kb_text = f"\n\n📄 Retrieved: {doc_info['doc_name']}\n{'─'*40}\n{snippet}\n{'─'*40}\n\n"
            else:
                kb_text = ""
            
            # Set up next prompt based on intent
            if intent == "file_claim":
                bot_response = kb_text + "I'll help you file a claim. Briefly, what happened?"
                session_state["step"] = "claim_description"
            elif intent == "billing":
                bot_response = kb_text + "What billing issue can I help with?\n1. Make a payment\n2. Payment arrangement/extension\n3. Question about my bill"
                session_state["step"] = "billing_type"
            elif intent == "roadside":
                bot_response = kb_text + "I'll get you roadside help. What's your situation?"
                session_state["step"] = "roadside_description"
            else:
                bot_response = kb_text + "What would you like to change about your policy?"
                session_state["step"] = "general_description"
        else:
            bot_response = "Please enter 1, 2, 3, or 4 to select an option."
    
    elif step == "claim_description":
        session.update("issue_description", message)
        bot_response = "When did this happen? (e.g., 'yesterday', 'this morning')"
        session_state["step"] = "claim_when"
    
    elif step == "claim_when":
        session.state["incident_details"]["when"] = message
        bot_response = "Where did this occur? (city/location)"
        session_state["step"] = "claim_where"
    
    elif step == "claim_where":
        session.state["incident_details"]["where"] = message
        bot_response = "What damage occurred? (brief description)"
        session_state["step"] = "claim_damage"
    
    elif step == "claim_damage":
        session.state["incident_details"]["damage"] = message
        bot_response = "Do you have photos of the damage? (yes/no)"
        session_state["step"] = "claim_photos"
    
    elif step == "claim_photos":
        session.state["incident_details"]["photos_available"] = message.lower()
        if message.lower() == 'yes':
            session.state["steps_tried"].append("Took photos of damage")
        bot_response = "Based on the information you've provided:\n1. Continue and complete this on your own\n2. Transfer to a specialist agent\n\nYour choice (1 or 2):"
        session_state["step"] = "final_choice"
    
    elif step == "billing_type":
        billing_map = {"1": "make_payment", "2": "payment_arrangement", "3": "billing_question"}
        billing_type = billing_map.get(message.strip())
        if billing_type:
            session.state["incident_details"]["billing_type"] = billing_type
            if message.strip() == "2":
                bot_response = "Can you briefly explain why you need an arrangement?"
                session_state["step"] = "billing_reason"
            else:
                bot_response = "Based on the information you've provided:\n1. Continue and complete this on your own\n2. Transfer to a specialist agent\n\nYour choice (1 or 2):"
                session_state["step"] = "final_choice"
        else:
            bot_response = "Please enter 1, 2, or 3."
    
    elif step == "billing_reason":
        session.state["incident_details"]["arrangement_reason"] = message
        bot_response = "Based on the information you've provided:\n1. Continue and complete this on your own\n2. Transfer to a specialist agent\n\nYour choice (1 or 2):"
        session_state["step"] = "final_choice"
    
    elif step == "roadside_description":
        session.update("issue_description", message)
        bot_response = "What's your current location?"
        session_state["step"] = "roadside_location"
    
    elif step == "roadside_location":
        session.state["incident_details"]["location"] = message
        bot_response = "What's wrong with your vehicle? (e.g., flat tire, won't start)"
        session_state["step"] = "roadside_issue"
    
    elif step == "roadside_issue":
        session.state["incident_details"]["vehicle_issue"] = message
        bot_response = "Are you in a safe location? (yes/no)"
        session_state["step"] = "roadside_safety"
    
    elif step == "roadside_safety":
        session.state["incident_details"]["safe"] = message.lower()
        if message.lower() == "no":
            session.update("sentiment", "urgent")
        bot_response = "Based on the information you've provided:\n1. Continue and complete this on your own\n2. Transfer to a specialist agent\n\nYour choice (1 or 2):"
        session_state["step"] = "final_choice"
    
    elif step == "general_description":
        session.update("issue_description", message)
        bot_response = "Based on the information you've provided:\n1. Continue and complete this on your own\n2. Transfer to a specialist agent\n\nYour choice (1 or 2):"
        session_state["step"] = "final_choice"
    
    elif step == "final_choice":
        if message.strip() == "2":
            if session.state["sentiment"] != "urgent":
                session.update("sentiment", "needs_agent")
            bot_response = "🔄 Transferring to agent...\n\n" + session.generate_handoff_summary()
            session_state["step"] = "complete"
        else:
            session.state["steps_tried"].append("Attempted self-service completion")
            bot_response = "✓ Proceeding with self-service...\n\n" + session.generate_handoff_summary()
            session_state["step"] = "complete"
    
    elif step == "complete":
        bot_response = "This session is complete. Refresh the page to start a new conversation."
    
    else:
        bot_response = "I'm not sure how to help with that. Please try again."
    
    session.add_message("assistant", bot_response)
    
    return bot_response, session_state


def chat_interface(message, history, session_state):
    """Gradio chat interface handler"""
    bot_response, updated_state = process_message(message, history, session_state)
    return bot_response, updated_state



    # Create Gradio interface
with gr.Blocks(title="Insurance IVR Demo") as demo:
    gr.Markdown("# Insurance IVR Context Handoff Demo")
    
    session_state = gr.State(None)
    
    # 1. THE WORDS (Instruction) - Sits at the top
    instruction_display = gr.Markdown("### Welcome to Insurance IVR Simulator.\n\nPlease enter your policy number to begin:")
    
    # 2. YOUR RESPONSE (Input Box) - Sits right under the words
    with gr.Row():
        msg = gr.Textbox(
            label="Your Response",
            placeholder="Type here...",
            scale=4,
            autofocus=True
        )
        submit = gr.Button("Send", scale=1)
    
    # 3. HISTORY LOG (The Chatbot) - Sits at the bottom
    chatbot = gr.Chatbot(
        value=[], 
        label="History Log",
        height=400
    )
    
    gr.Markdown("### How to use:\n1. Enter a policy number (6+ characters)\n2. Select an option (1-4)\n3. Answer the questions")
    
    def respond(message, chat_history, state):
        # Business logic
        bot_message, new_state = chat_interface(message, chat_history, state)
        
        # Update history with dictionaries (Required for Gradio 6.x)
        new_history = list(chat_history) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": bot_message}
        ]
        
        # Return outputs: Clear box, update history, update state, update instruction text
        return "", new_history, new_state, gr.update(value=f"### {bot_message}")

    # Bindings
    msg.submit(respond, [msg, chatbot, session_state], [msg, chatbot, session_state, instruction_display])
    submit.click(respond, [msg, chatbot, session_state], [msg, chatbot, session_state, instruction_display])
    
    gr.Markdown("---")
    gr.Markdown("**Note**: This is a demonstration system. Not affiliated with any insurance provider.")

if __name__ == "__main__":
    demo.launch()