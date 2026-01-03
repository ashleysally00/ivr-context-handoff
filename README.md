# Insurance IVR Context Handoff System

**Live demo:**  
https://huggingface.co/spaces/ashleysally00/ivr-context-handoff

A conversational AI system that preserves customer context across IVR interactions and generates structured agent handoff summaries, reducing repetitive questions and average handle time by an estimated 30–40% in simulated scenarios.

> **Note**: This is a demonstration project inspired by common insurance contact center workflows. It is not affiliated with any insurance provider.

## The Problem

Traditional IVR systems lose context during transfers. A customer calling about an auto claim typically:

1. Enters their policy number in the IVR menu
2. Selects "Claims"
3. Gets transferred to a live agent
4. **Is asked for the policy number again**
5. **Is asked "How can I help?" — already answered**

**Result**: Frustrated customers, longer handle times (8+ minutes average), and lower satisfaction scores.

## The Solution

This system maintains persistent session state throughout the conversation and automatically generates a comprehensive handoff summary for agents — so customers don't repeat themselves.

**Agents receive full context before engaging**, including:
- Verification status
- Customer intent and issue description
- All details already collected
- Relevant knowledge base articles retrieved
- Steps the customer has already tried

### Key Features

**Persistent Session State**  
Stores all customer inputs in a structured state object across the entire conversation flow

**Intent-Based Routing**  
Automatically classifies customer needs (claims, billing, roadside assistance, policy changes)

**Knowledge Base Retrieval (RAG)**  
Surfaces relevant policy or support articles based on detected intent

**Caller Verification**  
Validates identity and clearly flags unverified callers for agent review

**Context-Aware Follow-Ups**  
Dynamically asks only relevant questions (e.g., incident details for claims, location for roadside)

**Structured Agent Handoff**  
Generates a formatted summary including intent, verification status, collected details, sentiment, and recommended next actions

## Sample Agent Handoff Output

```
========================================
AGENT HANDOFF SUMMARY
========================================
Session ID: CALL-20250102-143022
Caller: POL123456
Verified: ✓ YES

CUSTOMER GOAL:
file_claim

ISSUE DESCRIPTION:
Rear-ended at stoplight

INCIDENT DETAILS:
  when: This morning
  where: Highway 101 San Jose
  damage: Rear bumper crumpled
  photos_available: yes

STEPS ATTEMPTED:
  - Took photos of damage

RETRIEVED KNOWLEDGE BASE ARTICLES:
  - claim-filing.md

CONVERSATION TURNS: 9
SENTIMENT: needs_agent

RECOMMENDED NEXT ACTION:
[Agent to determine based on above context]
========================================
```

**Business Impact**: Agent immediately knows the customer has photos, is verified, and is ready to file. No repeated questions. Estimated time savings: 2-3 minutes per call.

## Demo

[Screen recording coming soon - showing full claim filing flow with handoff]

## Architecture

```
Customer Input
     ↓
Intent Classification
     ↓
Session State Update (persistent)
     ↓
Knowledge Base Retrieval (RAG)
     ↓
Context-Aware Follow-up Questions
     ↓
Agent Handoff Summary Generation
```

### Tech Stack
- Python 3.x
- Keyword-based retrieval (expandable to semantic search with embeddings)
- Markdown knowledge base
- JSON state management

## Metrics

Based on test scenarios (see `eval/test-scenarios.md`):

- **Context Retention**: 100% - All user-provided information captured in handoff
- **Turn Efficiency**: 7-10 turns for standard cases, 4-6 for urgent escalations  
- **Routing Accuracy**: 100% for defined intents (claims, billing, roadside)
- **Information Re-request Rate**: 0% - No repeated questions due to persistent state
- **Estimated Handle Time Reduction**: 30-40% (based on eliminating repeated verification and issue description)

*Note: Estimates are based on controlled test scenarios and industry benchmarks, not production data.*

## Project Structure

```
ivr-context-handoff/
├── main.py                 # Core conversation logic
├── kb/                     # Knowledge base articles
│   ├── claim-filing.md
│   ├── billing-payment.md
│   └── roadside-assistance.md
├── eval/                   # Test scenarios and evaluation
│   └── test-scenarios.md
├── requirements.txt
└── README.md
```

## Running Locally

```bash
# Clone and setup
git clone [your-repo-url]
cd ivr-context-handoff
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python main.py
```

## Test Scenarios

See `eval/test-scenarios.md` for 8 documented test cases covering:
- Standard claim filing (happy path)
- Urgent roadside assistance (escalation priority)
- Billing payment arrangements (financial hardship)
- Unverified callers (security handling)
- Multi-vehicle claims (complex scenarios)

Each scenario includes expected outcomes and evaluation criteria.

## Design Decisions

### Why Persistent State?
Real contact center systems need to maintain context across transfers, channels, and agent handoffs. This demonstrates "conversation memory" that follows the customer throughout their journey.

### Why Structured Handoff Summaries?
Providing full context upfront can meaningfully reduce average handle time by eliminating repeated verification and issue restatement. The structured format ensures agents have actionable information immediately.

### Why Intent-Specific Follow-ups?
Generic chatbots ask the same questions regardless of context. This system asks relevant questions based on the customer's stated goal (e.g., safety location for roadside, incident timeline for claims), improving efficiency and customer experience.

### Why Simple Retrieval First?
Started with keyword-based retrieval to prove the concept quickly. The architecture supports upgrading to semantic search with embeddings without changing the conversation flow.

## Conversation Design Principles

- **Progressive disclosure**: Only ask for information when needed
- **Explicit confirmation**: Verify intent before deep-diving into details
- **Graceful degradation**: Unverified callers can still proceed (with appropriate flagging)
- **Urgency detection**: Safety-related scenarios (unsafe roadside location) trigger immediate escalation
- **Empathetic language**: Financial hardship scenarios use supportive tone

## Future Enhancements

- [ ] Semantic search with embeddings (upgrade from keyword matching)
- [ ] Multi-turn conversation repair (handling user corrections: "wait, I meant billing")
- [ ] Voice integration (Twilio/Amazon Connect/Asterisk)
- [ ] CRM integration for real customer data lookup
- [ ] Advanced sentiment analysis for proactive escalation
- [ ] A/B testing framework for conversation flow optimization
- [ ] PII masking in handoff summaries for compliance

## Non-Goals

This is a demonstration system focused on conversation design patterns. It does **not** include:
- Actual claims processing or adjudication
- Real payment processing
- Live telephony integration
- Production-grade security/authentication
- HIPAA/PCI compliance measures

## About This Project

Built to demonstrate conversational AI design for contact center applications, with focus on:
- State management across multi-turn conversations
- RAG (Retrieval-Augmented Generation) for knowledge lookup
- Production-ready handoff patterns
- Evaluation methodology for conversation systems

**Use case**: Insurance and telecom customer service workflows requiring context preservation and agent handoff optimization.
