# Arize Observe 2026: Agent Feedback Loops Messaging Playbook

**Event:** Arize Observe 2026 | June 4, 2026 | Shack15, San Francisco  
**Theme:** Agent Feedback Loops — The Missing Piece Between Test and Production  
**Audience:** AI builders, Heads of AI, AI/ML engineering leads  
**Goal:** Drive 1,100 registrations (currently 126; need 26 registrations/day for 38 days)

---

## CORE POSITIONING: "Agent Feedback Loops"

### The Problem We're Solving

Agents work in testing. They break in production. Teams don't know why until customers complain.

**The gap:** Evals catch some problems. Logging catches some problems. User feedback catches some problems. But **none of them together form the loop that actually prevents failures.**

### The Message Architecture

Every piece of content across every channel should ladder up to this:

> **Agents need feedback loops to learn and improve in production. At Arize Observe, you'll see how the best teams build them.**

This message:
- ✅ Leads with the **problem** (agents fail when loops are broken)
- ✅ Specifies the **solution** (feedback loops)
- ✅ Explains the **value** (learning and improvement)
- ✅ Positions the **event** (where you learn HOW)

---

## MESSAGE VARIANTS BY AUDIENCE SEGMENT

### For AI/ML Engineering Leaders (Target: "Why should my team care?")

**Core message:**
> Your agents are broken more often than you know. The feedback loop between production observability, evals, and retraining is the difference between shipping confidently and losing customers.

**Supporting points:**
- Most teams lack visibility into *why* agents fail
- Evals don't match production; production doesn't loop back to training
- You're flying blind without a feedback loop system
- At Observe: See how 5 AI teams at scale close this gap

**Example hooks:**
- "Your agent passed evals. Then it broke in prod. Here's why."
- "The missing loop: Why your evals don't predict failures"
- "From traces to evals to retraining — the loop that works"

---

### For Builders / Individual Developers (Target: "Will this help me ship better?")

**Core message:**
> Ship agents faster without losing your mind. The feedback loop is how you catch problems before they reach users.

**Supporting points:**
- You ship an agent; it works 90% of the time
- The remaining 10% breaks production; you scramble to fix it
- A good feedback loop catches that 10% in staging
- At Observe: See how teams built feedback loops that actually catch issues

**Example hooks:**
- "The 2am debug session your agents will save you from"
- "Catch agent failures before your users do"
- "Sessions, traces, evals: The feedback loop framework"

---

### For Heads of AI / Technical Executives (Target: "Is this a business problem?")

**Core message:**
> Agent reliability is the new blocker for autonomous systems at scale. Feedback loops are how you operationalize reliability.

**Supporting points:**
- Broken agents = lost trust, lost revenue, lost users
- You need operational systems that detect and fix problems automatically
- That system is the feedback loop (observability → evals → retraining)
- At Observe: Hear how Cursor, Uber, DeepMind operationalize reliability

**Example hooks:**
- "Why your autonomous agent initiative is stalled (and how to unstall it)"
- "Reliability at scale: The feedback loop framework"
- "Hear from the teams building production-grade agents"

---

## MESSAGING BY CONTENT ANCHOR

### 1. Speaker Spotlights

**Old:** "Meet Aayush Garg, Head of AI at Cursor"  
**New:** "Aayush on closing the feedback loop: Why most agents fail in production and how Cursor measures reliability"

**Why:** Moves from credential to insight. The hook is the problem + specific company + the answer.

#### Speaker Spotlight Formula

```
[Speaker Name] on [specific feedback loop problem]:
Why [common failure mode] and how [their company] [solved/measured/operationalized] [the solution]
```

**Examples:**

- "Chi on agent memory architecture: Why stateless agents fail and how to build feedback loops that persist learning"
- "Stuart on autonomous engineering: Catching code-gen failures before they ship — the feedback loop for agents writing code"
- "Eno on evals at scale: Why point-in-time evals lie and how continuous loops catch drift"
- "Aayush on reliability: Building agents Cursor customers trust — the observability stack that matters"

**Asset:** Include in speaker amplification kit with pre-written social posts using this framing.

---

### 2. Session Content & Workshops

**Old:** "Agent Reliability Workshop" or "Evals, Agent Reliability, Autonomous Engineering"  
**New:** Problem-first, feedback loops focused

#### Updated Session Descriptions

| Session | Old | New | Key Hook |
|---------|-----|-----|----------|
| **Evals Workshop** | "Deep dive into evaluation frameworks" | "Why your agent evals don't predict production failures — and what to do about it" | Problem identification |
| **Agent Reliability Panel** | "Hear from teams building reliable agents" | "The feedback loop framework: How 5 AI teams detect and fix broken agents faster than they break" | Operational framework |
| **Autonomous Engineering Talk** | "Autonomous code generation and agents" | "Shipping autonomous agents without losing your mind: The observability stack that catches problems before users do" | Success criteria |
| **Observability Deep Dive** | "Traces, logs, and agent observability" | "From chaos to clarity: Building feedback loops with sessions, traces, and evals" | Problem solution |
| **Multi-Agent Workshop** | "Designing multi-agent systems" | "Coordinating agents at scale: The feedback loops that keep orchestration from breaking" | Orchestration problem |

---

### 3. Founder POVs (Aparna & Jason)

**Position:** Authority-building; earns the right to invite.

#### Suggested Topics (All Feedback Loops-Focused)

**Option 1: "Agent Feedback Loops: Why Evals Alone Aren't Enough"**

*Thesis:* Most teams over-invest in evals (test-time) and under-invest in production loops (runtime). Production observability is the missing piece.

*Structure:*
- The lie we tell ourselves: "If it passes evals, it works in prod"
- Why this fails (deployment gap, distribution shift, adversarial users)
- What a real feedback loop looks like (observability → evals → retraining)
- Why this matters now (agents at scale require this; without it, you're bleeding money)

**Option 2: "Production Observability for Agents: The Year of Visibility"**

*Thesis:* 2025 was about building agents. 2026 is about knowing when they're broken. That's observability.

*Structure:*
- The agent reliability crisis (every company is shipping broken agents)
- Why traditional logging doesn't work (agents are non-deterministic; you can't log your way to reliability)
- The feedback loop as the solution (session traces → eval on failures → retrain → loop)
- What we're seeing at Arize (patterns from thousands of agents; the loops that work)

**Option 3: "The Hidden Cost of Unreliable Agents"**

*Thesis:* Every broken agent in production is a data point. Most teams treat it as a support ticket. Great teams treat it as a signal.

*Structure:*
- Cost of an outage (support load, customer churn, reputational damage)
- Why agents are harder to debug than code (non-determinism, emergence, LLM variance)
- The feedback loop as the operational solution (detect → diagnose → fix → deploy → measure)
- Building a culture of agent reliability (observable, tested, looped)

---

### 4. Builder Community Messaging

**Old:** "'Teams from Uber, IBM, Cursor, DeepMind, OpenAI in the room.' Peer FOMO, networking value."  
**New:** Connect community to feedback loops problem + solution

#### Revised Community Hooks

**Social post (LinkedIn):**
> The teams building reliable agents at scale will be in a room together on June 4. Hear how Cursor, Uber, DeepMind, and OpenAI close the feedback loop between production and training. Get your comp ticket — builder seats only.

**In-product banner:**
> "Teams from Cursor, Uber, DeepMind are sharing how they catch agent failures before users do. You?"

**Discord/Community:**
> "Real talk: How does your team catch broken agents? Hear solutions from Cursor, Uber, DeepMind, OpenAI at Observe June 4. We're keeping it builder-focused, problem-focused, solution-focused."

---

## MESSAGING BY CHANNEL

### LinkedIn (Org + Employee Posts)

**Volume:** ~3 posts/week at peak (May 1 - June 3)

#### Week-by-Week Messaging Arc

**Week 1 (May 1-7): Problem Awareness — "Agent Feedback Loops Matter"**

Post 1: "Your agent works in testing. Production is different."
- Lead with problem
- Introduce term "feedback loop"
- CTA: "Save your seat"

Post 2: Speaker spotlight — "Aayush on closing the feedback loop"
- Credential + problem
- Specific company insight
- CTA: "Hear from Cursor"

Post 3: "Why evals don't predict production failures"
- Deep problem articulation
- Lead into observability
- CTA: "Learn how to fix it"

---

**Week 2 (May 8-14): Authority Building — "Here's What Works"**

Post 1: Founder POV excerpt — "Why evals alone aren't enough"
- Authority positioning
- Framework introduction
- CTA: "Full talk at Observe"

Post 2: Speaker spotlight — "Chi on agent memory and feedback loops"
- Technical depth
- How memory = learning
- CTA: "Attend the workshop"

Post 3: "The 5 teams shipping reliable agents — here's their secret"
- Social proof
- Framework teaser
- CTA: "See what they're doing"

---

**Week 3+ (May 15-31): Momentum + Specificity — "Here Are Your Options"**

Post 1: "Agent feedback loops: From traces to evals to retraining"
- Framework deep-dive
- Content anchors
- CTA: "Pick your workshop"

Post 2: "Why autonomous engineering requires feedback loops"
- Stuart spotlight
- New use case
- CTA: "See the talk"

Post 3: "3 patterns from teams at scale on catching agent failures"
- Actionable insights
- Multiple audience angles
- CTA: "Attend sessions"

---

**Week 4 (Jun 1-3): Urgency — "It's Happening Soon"**

Post 1: "Last chance: Hear from Cursor, Uber, DeepMind on agent reliability"
- FOMO
- Peer authority
- CTA: "Comp ticket"

Post 2: "$50 community ticket — your on-ramp to the feedback loops conversation"
- Price emphasis
- Accessibility
- CTA: "Register now"

Post 3: "June 4. SF. Agents. Feedback loops. Here's what you'll learn."
- Event recap overview
- Session highlights
- CTA: "Get your ticket"

---

### X / Twitter

**Volume:** 2-3 posts/week; speaker drops, quote cards, builder community

#### Thread Ideas (Feedback Loops Focused)

**Thread 1: "Why Agents Break in Production"**
```
1/ Your agent passed evals with 95% accuracy. 
   Then it went to production and talked to 1,000 users.
   Now you're debugging at 2am.
   
   Here's why: Evals don't capture feedback loops.

2/ Evals test agent behavior in isolation.
   But in production, agents:
   - Talk to real users (not test cases)
   - Make mistakes users catch and report
   - Don't learn from those mistakes unless you build the loop

3/ The feedback loop:
   - Observability: See what the agent actually did
   - Evaluation: Automatically test failures
   - Retraining: Fix the gap
   - Deploy: Test again
   - Repeat
   
   Without this? You're guessing.

4/ At Arize Observe June 4, hear how teams at Cursor, Uber, DeepMind built this loop.
   Because broken agents in prod = customers lost = revenue gone.
   
   Comp tickets: [link]
```

**Thread 2: "The Cost of a Broken Agent"**
```
1/ Last week, a customer's agent hallucinated badly.
   Cost:
   - 2 hours of your time debugging
   - 4 support emails
   - 1 angry customer
   - Probably more broken agents you didn't catch
   
   How do you fix this systematically?

2/ Most teams:
   - Log every call (helpful but not actionable)
   - Run evals every sprint (good but delayed)
   - Wait for customers to complain (reactive)
   
   None of this is a loop. It's random.

3/ Real teams build feedback loops:
   1. Every failure is automatically logged with context
   2. Failures are automatically evaluated
   3. Patterns trigger retraining
   4. New version is deployed
   5. You measure if it worked
   
   That's a loop.

4/ At Observe June 4, Stuart Stuart will show how [team] automated this.
   Because doing this manually doesn't scale.
   
   Hear from Cursor, Uber, DeepMind on their loops.
```

**Quote Cards:**
- "Your agent works in testing. Production is different. That's why you need feedback loops." — Aparna, Arize
- "Evals don't predict production failures. But feedback loops do." — [Speaker to be confirmed]
- "Broken agents = lost customers. Feedback loops = caught problems." — [Speaker]

---

### Email Campaigns

**Volume:** 1/week during build phase; 2 in final week; 6 sends total

#### Email Segmentation & Copy

**Segment 1: Existing Arize/Phoenix Users (Warmest)**

**Subject Line (Week 1-2):**
> "Why your traces don't catch everything (and what to do about it)"

**Body opening:**
> You're using Arize to trace your agents. Smart.
> 
> But here's what we're seeing: Traces tell you WHAT happened. They don't automatically tell you what went wrong or how to prevent it next time.
> 
> That's feedback loops.
> 
> [CTA: "See how teams close the loop"]

**Subject Line (Week 3-4):**
> "Feedback loops: The missing piece you didn't know you needed"

**Body opening:**
> You know observability. You're tracing your agents.
> 
> Now it's time to go deeper: How do you turn traces into automatic improvements?
> 
> Hear from Cursor, Uber, DeepMind on the feedback loop framework that works.

**Subject Line (Final week):**
> "Last chance: Agent feedback loops at Observe, June 4"

---

**Segment 2: AI Engineering Job Titles (Cold, from LinkedIn)**

**Subject Line (Week 1-2):**
> "Your agent broke in production. Here's what happened."

**Body opening:**
> You shipped an agent. It worked 90% of the time.
> 
> The other 10% broke in production, and you spent 3 hours debugging.
> 
> That's not bad luck. That's what happens without feedback loops.
> 
> At Arize Observe June 4, we'll show you how to build them.

**Subject Line (Week 3-4):**
> "Hear from Cursor: How they catch broken agents before users do"

**Body opening:**
> Most teams find agent bugs the hard way: A customer complains.
> 
> Cursor finds them faster.
> 
> They built a feedback loop that automatically detects when agents fail in production, evaluates the failure, and flags it for retraining.
> 
> Hear how at Observe June 4.

**Subject Line (Final week):**
> "$50 community ticket: Learn agent feedback loops from Cursor, Uber, DeepMind"

---

**Segment 3: Past Observe Attendees (Medium)**

**Subject Line (Week 1-2):**
> "Observe 2026: From observability to feedback loops"

**Body opening:**
> Last year you learned to trace agents.
> 
> This year: Close the loop.
> 
> Feedback loops are how you turn observability into continuous improvement.
> 
> See what's new at Observe 2026.

**Subject Line (Final week):**
> "See you June 4 — agent feedback loops are the story"

---

### In-Product Banner (Phoenix Logged-In Users)

**Narrative Arc (May 1 - June 3)**

**May 1-10: Problem Awareness**
> Agents work in testing. Production is different. Learn how to build feedback loops that close the gap. [Observe June 4]

**May 11-20: Solution Introduction**
> Feedback loops: From observability to evals to retraining. Hear how Cursor, Uber, DeepMind do it. [Get ticket]

**May 21-31: Social Proof**
> Teams at Cursor, Uber, DeepMind, OpenAI are building feedback loops for reliable agents. You? [Join them June 4]

**Jun 1-4: Urgency**
> Comp tickets available for the last 48 hours. Feedback loops for agents. June 4. San Francisco. [Register now]

---

## MESSAGING BY TACTIC

### Comp Ticket Direct Outreach

**Email Hook:**
> "Feedback loops" is how the best teams keep agents reliable in production.
> 
> At Arize Observe June 4, Cursor, Uber, DeepMind, and OpenAI are sharing theirs.
> 
> **[Your company]** is building agents too. You should hear from the teams doing it right.
> 
> **Comp ticket:** [Link with code]
> 
> Come build the loop.

---

### $50 Community Ticket Promotion

**Messaging:**
> "Builder seat, community price. $50 gets you into the room with teams from Cursor, Uber, DeepMind, and OpenAI — all there to talk about feedback loops for agents."

**Why this works:**
- Price removes friction
- "Builder seat" signals it's technical, not marketing
- Community signals peer-to-peer
- Feedback loops is the connective theme

---

### Partner Co-Promotion

**Ask to partners:** "Help us close feedback loops for agents."

**Value prop for partner:**
> Your users are building agents. At Arize Observe June 4, we're hosting the conversation on feedback loops — the missing piece between test and production.
> 
> Co-promote one speaker from Observe to your community. We'll show your users how [your tool] integrates with the feedback loop framework.

**Examples:**

- **CrewAI / Mastra:** "Multi-agent orchestration requires feedback loops"
- **Daytona / Anyscale:** "Scaling agents without feedback loops = disaster"
- **Cursor:** "Autonomous code gen requires feedback loops"
- **Factory:** "Agent factories need feedback loops"

---

## SUMMARY: The Feedback Loops Messaging Strategy

| Element | Message |
|---------|---------|
| **Core problem** | Agents work in testing; production is different |
| **Core solution** | Feedback loops (observability → evals → retraining → deploy → measure) |
| **Why now** | Agents are everywhere; feedback loops are the operational answer |
| **Why Observe** | See how Cursor, Uber, DeepMind, OpenAI do it |
| **Call to action** | Come learn; bring your team; build with builders |

---

## IMPLEMENTATION CHECKLIST

- [ ] **Speakers:** Brief each speaker on feedback loops positioning; provide updated spotlight copy
- [ ] **Session descriptions:** Update all 5+ sessions with problem-first, feedback loops framing
- [ ] **Social calendar:** Populate LinkedIn/X schedule with week-by-week messaging arc
- [ ] **Email campaigns:** Create 6 email sends with segmented copy
- [ ] **Paid creative:** Build 4 ad variants with feedback loops angle (see PAID-CREATIVE.md)
- [ ] **In-product banner:** Create rotating copy for 4 phases (May 1-10, 11-20, 21-31, Jun 1-4)
- [ ] **Speaker amplification kit:** Update with feedback loops positioning + pre-written posts
- [ ] **Partner outreach:** Send co-promotion asks with feedback loops value prop

---

## SUCCESS METRICS

**Goal:** 1,100 registrations by June 4 (38 days from Apr 28; 26 registrations/day)

**Feedback loops messaging impact:**
- Higher engagement on LinkedIn posts (specificity + trend)
- Better paid ad CTR (problem-driven creative)
- Improved email open rates (problem-first subject lines)
- More community sign-ups (peer authority + social proof)

**Target:** Lift velocity from 26/day to 28-30/day → fill the room faster → create urgency early

---

**Last Updated:** April 28, 2026  
**Owned by:** DevRel / Marketing  
**Review:** Weekly during May; daily in final week
