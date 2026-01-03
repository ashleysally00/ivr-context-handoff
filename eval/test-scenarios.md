# Test Scenarios for IVR Context Handoff System

## Purpose
These scenarios test the system's ability to maintain context, retrieve relevant information, and generate useful agent handoff summaries across different customer intents and complexity levels.

---

## Scenario 1: Simple Claim Filing (Happy Path)
**Customer Type:** Verified policyholder  
**Intent:** File auto claim  
**Complexity:** Low

**User Journey:**
1. Enters valid policy number → Verified
2. Selects "File a claim"
3. Describes: "Rear-ended at a stoplight"
4. Provides incident details:
   - When: This morning
   - Where: Highway 101, San Jose
   - Damage: Rear bumper crumpled
   - Photos: Yes
5. Chooses to transfer to agent

**Expected Outcomes:**
- ✓ Intent correctly identified: `file_claim`
- ✓ Verification status: `true`
- ✓ KB retrieved: `claim-filing.md`
- ✓ Steps tried: "Took photos of damage"
- ✓ All incident details captured
- ✓ Conversation turns: 8-10
- ✓ Sentiment: `needs_agent`

---

## Scenario 2: Urgent Roadside Assistance
**Customer Type:** Verified policyholder  
**Intent:** Emergency roadside help  
**Complexity:** High (urgent)

**User Journey:**
1. Enters policy number → Verified
2. Selects "Roadside assistance"
3. Describes: "Car won't start, stuck on highway"
4. Location: "I-280 southbound, mile marker 15"
5. Issue: "Engine won't turn over, clicking sound"
6. Safe location: "No, I'm on the shoulder with traffic"
7. Immediately requests agent

**Expected Outcomes:**
- ✓ Intent: `roadside`
- ✓ KB retrieved: `roadside-assistance.md`
- ✓ Sentiment: `urgent` (triggered by unsafe location)
- ✓ Location captured in incident details
- ✓ Quick escalation to human agent
- ✓ Handoff summary emphasizes urgency

---

## Scenario 3: Billing Payment Arrangement
**Customer Type:** Verified policyholder  
**Intent:** Request payment extension  
**Complexity:** Medium

**User Journey:**
1. Enters policy number → Verified
2. Selects "Billing and payments"
3. Selects "Payment arrangement/extension"
4. Reason: "Lost my job last week, need a few extra days"
5. Requests agent to discuss options

**Expected Outcomes:**
- ✓ Intent: `billing`
- ✓ KB retrieved: `billing-payment.md`
- ✓ Billing type: `payment_arrangement`
- ✓ Reason captured in incident details
- ✓ Empathetic sentiment tracking
- ✓ Agent handoff includes financial hardship context

---

## Scenario 4: Unverified Caller - Claim Filing
**Customer Type:** Cannot verify identity  
**Intent:** File claim  
**Complexity:** Medium (security concern)

**User Journey:**
1. Enters invalid/short policy number → Not verified
2. System continues but flags verification failure
3. Selects "File a claim"
4. Describes incident
5. Provides details but system notes verification issue

**Expected Outcomes:**
- ✓ Verification status: `false`
- ✓ System continues but flags security concern
- ✓ Handoff summary clearly shows "✗ NO" verification
- ✓ Agent knows to re-verify before proceeding

---

## Scenario 5: Multi-vehicle Claim with Photos
**Customer Type:** Verified policyholder  
**Intent:** Complex claim filing  
**Complexity:** High

**User Journey:**
1. Verified successfully
2. Selects "File a claim"
3. Describes: "Three-car accident on freeway"
4. Details:
   - When: Yesterday evening, around 6pm
   - Where: I-880 near Oakland
   - Damage: Front and rear damage, airbags deployed
   - Photos: Yes, multiple angles
5. Transfers to agent

**Expected Outcomes:**
- ✓ Intent: `file_claim`
- ✓ Complex damage description captured
- ✓ Multiple indicators suggest serious claim
- ✓ Steps tried: Photos taken
- ✓ Agent handoff includes all critical safety details

---

## Scenario 6: Billing Question - Simple Inquiry
**Customer Type:** Verified policyholder  
**Intent:** Billing inquiry  
**Complexity:** Low

**User Journey:**
1. Verified
2. Selects "Billing and payments"
3. Selects "Question about my bill"
4. Brief question about charge
5. Attempts self-service first, then escalates

**Expected Outcomes:**
- ✓ Intent: `billing`
- ✓ Billing type: `billing_question`
- ✓ KB snippet shown helps customer understand
- ✓ Self-service attempt tracked in steps_tried
- ✓ Clean escalation if needed

---

## Scenario 7: Roadside - Tire Change
**Customer Type:** Verified policyholder  
**Intent:** Roadside assistance  
**Complexity:** Low-Medium

**User Journey:**
1. Verified
2. Selects "Roadside assistance"
3. Issue: "Flat tire"
4. Location: "Parking lot at 123 Main St, Sunnyvale"
5. Safe location: "Yes, in a parking lot"
6. Chooses to continue self-service after seeing KB info

**Expected Outcomes:**
- ✓ Intent: `roadside`
- ✓ Non-urgent sentiment (safe location)
- ✓ KB shows tire change coverage details
- ✓ Customer opts for self-service (calls provider directly)
- ✓ Successful containment without agent transfer

---

## Scenario 8: Policy Change - Coverage Update
**Customer Type:** Verified policyholder  
**Intent:** Modify policy coverage  
**Complexity:** Medium

**User Journey:**
1. Verified
2. Selects "Policy changes"
3. Wants to add comprehensive coverage
4. Needs agent to discuss pricing

**Expected Outcomes:**
- ✓ Intent: `policy_change`
- ✓ KB retrieved (current: billing-payment as placeholder)
- ✓ Change type captured
- ✓ Agent handoff includes coverage change request

---

## Evaluation Metrics

For each scenario, measure:

1. **Context Retention Rate:** Did all user-provided info appear in handoff summary?
2. **Correct KB Retrieval:** Was the right knowledge base article retrieved?
3. **Turn Efficiency:** Was the conversation appropriately concise?
4. **Routing Accuracy:** Did urgent cases escalate quickly? Did simple cases offer self-service?
5. **Handoff Quality:** Does the agent have everything needed to continue?

### Target Benchmarks
- Context retention: 100% (all provided info captured)
- Correct KB retrieval: 100% for defined intents
- Average turns to handoff: 7-10 for standard cases, 4-6 for urgent
- Routing accuracy: 100% (urgent → fast escalation, simple → self-service option)

---

## Testing Notes

**How to test:**
1. Run `python3 main.py` for each scenario
2. Follow the user journey exactly as written
3. Save the final handoff summary
4. Check against expected outcomes

**Future enhancements to test:**
- Conversation repair (user corrects themselves)
- Multiple verification attempts
- Ambiguous intents requiring clarification
- Knowledge base gaps (missing articles)