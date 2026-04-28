# Arize Observe 2026: Updated Session Descriptions

**Focus:** Problem-first framing; agent feedback loops as the connective tissue; specific learning outcomes

---

## HERO SESSIONS (4 major talks)

### Session 1: Agent Reliability at Scale (Keynote)

**Speaker:** Aayush Garg, Head of AI at Cursor  
**Duration:** 45 min + 15 min Q&A  
**Format:** Keynote presentation + live demo  
**Time slot:** 9:30am - 10:30am  

**OLD DESCRIPTION:**
> Join Aayush Garg from Cursor for a talk on building reliable agents at scale. Discuss strategies, real-world examples, and best practices.

**NEW DESCRIPTION:**
> **"Closing the Feedback Loop: Why Code-Generating Agents Fail in Production"**
> 
> Your agent passed evals. It works in testing. Then it went to production and started generating broken code.
> 
> Here's what happened: You were missing the feedback loop.
> 
> At Cursor, we generate code with agents. And we learned the hard way that evals aren't enough. Production is messier. Users find edge cases you didn't test. Hallucinations slip through.
> 
> In this talk, Aayush walks through:
> - Why evals don't predict production failures (the distribution shift problem)
> - The feedback loop framework that catches failures before they reach users (observability → eval → retrain → deploy → measure)
> - How Cursor automated this loop so agents can improve continuously
> - Real metrics: Time-to-fix broken agents dropped from 3 hours to 15 minutes
> 
> If you're shipping agents, this is how you stop losing customers to hallucinations and edge cases.

**Learning outcomes:**
- Understand why evals fail in production and how feedback loops fix it
- See a real example (code generation) of a production loop
- Learn how to measure agent reliability operationally
- Get concrete tools for implementing this at your org

---

### Session 2: Agent Memory Architecture for Learning in Production (Technical Deep-Dive)

**Speaker:** Chi Zhang  
**Duration:** 50 min + 10 min Q&A  
**Format:** Technical talk + interactive examples  
**Time slot:** 11:00am - 12:00pm

**OLD DESCRIPTION:**
> Explore agent memory architectures and how they impact agent behavior. Best practices for production deployments.

**NEW DESCRIPTION:**
> **"Why Stateless Agents Can't Learn (And How to Build Agents That Do)"**
> 
> Most agents are stateless. They make the same mistake repeatedly because they have no memory of what went wrong before.
> 
> That's a broken feedback loop.
> 
> At its core, a feedback loop requires memory: The agent needs to remember what happened last time, learn from it, and behave differently next time.
> 
> In this talk, Chi dives into:
> - What "memory" means for agents (not just persistence; actual learning)
> - Why stateless agents degrade in production (they repeat failures because they have no feedback)
> - Memory architectures that enable learning (session state, feature stores, retrieval-augmented context)
> - How to integrate memory into your feedback loop (observe → remember → evaluate → retrain)
> - Real examples: Multi-turn agents that learn from user corrections
> 
> By the end, you'll understand why memory isn't optional — it's the foundation of agents that improve.

**Learning outcomes:**
- Understand the connection between memory and feedback loops
- Design memory architectures for agents that learn in production
- Implement session-level and cross-session memory patterns
- Measure agent improvement over time (proof that memory works)

---

### Session 3: Beyond Evals: Continuous Evaluation at Scale (Framework)

**Speaker:** Eno Oziel  
**Duration:** 50 min + 10 min Q&A  
**Format:** Technical talk + live examples  
**Time slot:** 1:30pm - 2:30pm

**OLD DESCRIPTION:**
> Best practices for building evaluations for LLM systems. Learn evaluation frameworks and how to test agents at scale.

**NEW DESCRIPTION:**
> **"Why Point-in-Time Evals Lie (And How Continuous Loops Tell the Truth)"**
> 
> You write evals. You test your agent. It passes. You ship.
> 
> Then you find out your agent fails on edge cases users discovered after deployment.
> 
> Here's why: Evals are snapshots. Production is continuous. Your agent sees 1,000 new inputs every hour. Those are better test cases than anything you wrote.
> 
> In this talk, Eno walks through:
> - Why static evals don't scale (distribution shift, adversarial users, emergent failures)
> - The feedback loop approach: Production as the test bed
> - Continuous evaluation: Automatically evaluating every production output
> - Building eval pipelines that run in prod (performance, cost, latency trade-offs)
> - Turning failures into training signals (so failures become improvements)
> - Measuring impact: Did the loop actually make the agent better?
> 
> If you're serious about agents in production, continuous evals are non-negotiable.

**Learning outcomes:**
- Understand the limitations of static evals for production agents
- Design continuous evaluation pipelines that run in production
- Implement automated eval + retrain loops
- Measure agent improvement statistically (prove the loop is working)

---

### Session 4: Autonomous Engineering Without Losing Your Mind (Technical Talk)

**Speaker:** Stuart Larson  
**Duration:** 50 min + 10 min Q&A  
**Format:** Technical talk + code walkthrough  
**Time slot:** 3:00pm - 4:00pm

**OLD DESCRIPTION:**
> Building systems with autonomous agents. Challenges, patterns, and lessons learned from shipping autonomous systems.

**NEW DESCRIPTION:**
> **"Shipping Autonomous Code Generation: The Feedback Loop That Catches Failures Before They Deploy"**
> 
> Autonomous agents are writing production code now. That's incredible. That's also terrifying.
> 
> Because when an agent generates bad code, it doesn't just break — it breaks at scale. One broken function multiplied across 1,000 deployments.
> 
> Here's how you prevent that: Feedback loops.
> 
> In this talk, Stuart walks through:
> - The specific risks of autonomous code generation (hallucinations, logic errors, edge cases)
> - The feedback loop that catches failures before they ship (observability of generated code → automatic testing → eval → reject if wrong → flag for review → retrain)
> - How to set confidence thresholds (some code ships without review; risky code gets human review)
> - Measuring reliability: Metrics that matter for autonomous systems
> - Real example: A major company's autonomous engineering pipeline and how they achieved 99.2% correctness
> 
> If you're building autonomous systems, this feedback loop is the difference between shipping with confidence and losing your job.

**Learning outcomes:**
- Understand the unique risks of autonomous code generation
- Design feedback loops specifically for autonomous systems
- Implement automated testing + human review gates
- Build confidence thresholds and quality metrics

---

## WORKSHOPS (Half-day, hands-on, small groups)

### Workshop 1: Building Evals That Predict Production Failures

**Duration:** 3 hours (morning or afternoon)  
**Format:** Hands-on; bring your laptop  
**Group size:** 30 max  
**Prerequisites:** Basic familiarity with agents

**OLD DESCRIPTION:**
> Learn to build evaluation frameworks for your agents. Practical hands-on session on eval methodology.

**NEW DESCRIPTION:**
> **"From Static Tests to Feedback Loops: Building Evals That Actually Catch Bugs"**
> 
> You've written evals. But they don't predict production failures.
> 
> Why? Because you're testing in isolation. Production is messy.
> 
> In this hands-on workshop, you'll learn to:
> - Understand why your current evals are missing failures
> - Design evals that test against production scenarios (not just happy paths)
> - Build automated eval pipelines that run continuously
> - Use production data to improve your evals (failures become test cases)
> - Implement a basic feedback loop: observe → eval → flag → retrain
> 
> **We'll walk through a real agent codebase** (code generation agent) and:
> 1. Write static evals that pass ✓
> 2. Deploy the agent ✓
> 3. See it fail in production 💥
> 4. Build a feedback loop to catch those failures 🔁
> 5. Watch the agent improve
> 
> You'll leave with templates and code you can use on day 1 at your org.

**What to bring:**
- Laptop with Python 3.9+
- Git
- Your favorite text editor or IDE

**Learning outcomes:**
- Design evals that predict production failures (not just test passing code)
- Build continuous evaluation pipelines
- Implement the first step of a feedback loop
- Know the tools and libraries that make this easy

---

### Workshop 2: Setting Up Agent Observability From Zero

**Duration:** 3 hours (morning or afternoon)  
**Format:** Hands-on; we'll build a system step-by-step  
**Group size:** 30 max  
**Prerequisites:** Basic familiarity with Python; agents a plus

**OLD DESCRIPTION:**
> Learn how to instrument agents with observability. Best practices for logging, tracing, and monitoring.

**NEW DESCRIPTION:**
> **"From Blind to Visible: Setting Up Observability That Enables Feedback Loops"**
> 
> You have an agent in production. You have no idea what it's doing wrong.
> 
> That's because you skipped observability.
> 
> Observability isn't just logging. It's structured visibility into agent behavior: What did it decide? Why? What went wrong? Can you reproduce it?
> 
> In this hands-on workshop, we'll build observability from scratch:
> 
> **Part 1: Observability Fundamentals** (45 min)
> - What to observe in an agent (inputs, decisions, outputs, reasoning, errors)
> - Sessions vs traces (when to use each)
> - What makes observability "complete" (you can reproduce any failure)
> 
> **Part 2: Building It** (60 min)
> - Instrumenting an agent with proper logging (you'll code this)
> - Collecting structured data (decisions, reasoning, scores)
> - Sampling strategies for high-volume agents (can't log everything; what matters?)
> 
> **Part 3: Making It Actionable** (45 min)
> - Querying your observability data to find failures
> - Setting up alerts for anomalies
> - Connecting observability to your feedback loop (this failure data → eval → retrain)
> 
> You'll walk out with a working system you can deploy Monday morning.

**What to bring:**
- Laptop with Python 3.9+
- Git + your favorite editor
- Optional: An agent of your own to instrument (or we'll provide one)

**Learning outcomes:**
- Understand what makes observability "complete" for agents
- Design logging/tracing systems that support feedback loops
- Implement structured observability (not just string logs)
- Know how to connect observability to evals and retraining

---

### Workshop 3: Multi-Agent Orchestration: Preventing Failures at Scale

**Duration:** 3 hours (morning or afternoon)  
**Format:** Hands-on; case study of a multi-agent system  
**Group size:** 30 max  
**Prerequisites:** Familiarity with agents; multi-agent bonus

**OLD DESCRIPTION:**
> Design patterns for multi-agent systems. Building reliable workflows with multiple agents.

**NEW DESCRIPTION:**
> **"When Agents Coordinate, Failures Multiply: Feedback Loops for Multi-Agent Systems"**
> 
> One agent fails 5% of the time. Two agents coordinating fail 10% of the time (failures compound).
> 
> Three agents? Closer to 15%. And debugging is 10x harder because you don't know which agent broke.
> 
> That's why multi-agent systems need feedback loops.
> 
> In this hands-on workshop, we'll build a multi-agent system and its feedback loop:
> 
> **Part 1: The Coordination Problem** (45 min)
> - Where failures happen in multi-agent systems (agent A breaks; agent B doesn't notice)
> - Observability for multi-agent workflows (you need to trace across agents)
> - Detecting failures in coordination (not just in individual agents)
> 
> **Part 2: Building the Loop** (60 min)
> - Instrument a 3-agent workflow (we provide code; you instrument it)
> - Build evals that test coordination, not just individual agents
> - Implement failure detection across the workflow
> - Create a recovery mechanism (if agent A fails, how does agent B know? What's the fallback?)
> 
> **Part 3: Measuring Reliability** (45 min)
> - Metrics that matter for multi-agent systems (latency, correctness, cost, partial failures)
> - Setting up continuous monitoring
> - Connecting failures to retraining (which agent should we retrain to fix this?)
> 
> You'll walk out understanding how to prevent cascading failures in your multi-agent systems.

**What to bring:**
- Laptop with Python 3.9+
- Your favorite editor
- Curiosity about where multi-agent systems break

**Learning outcomes:**
- Design observability for multi-agent workflows
- Implement failure detection across agent boundaries
- Build recovery mechanisms for cascading failures
- Measure reliability of complex agent systems

---

### Workshop 4: From Traces to Retraining: Closing the Feedback Loop

**Duration:** 3 hours (morning or afternoon)  
**Format:** Hands-on; real retraining pipeline  
**Group size:** 20 max (most technical; small group)  
**Prerequisites:** Python; familiarity with ML training

**OLD DESCRIPTION:**
> End-to-end workflow for capturing data, building evals, and retraining agents.

**NEW DESCRIPTION:**
> **"The Complete Loop: Observability → Evals → Retrain → Deploy → Measure"**
> 
> You've observed a failure. You've evaluated it. Now what?
> 
> Retraining is where the loop closes. Where the agent actually improves.
> 
> In this hands-on workshop, you'll build the complete feedback loop from scratch:
> 
> **Part 1: From Failures to Training Data** (40 min)
> - Collecting training data from production failures
> - Labeling strategies (human labels vs automated)
> - Avoiding data leakage and feedback loops (yes, there's a meta-level feedback loop)
> - Cost: When is retraining worth it vs just fixing in code?
> 
> **Part 2: Retraining Pipeline** (50 min)
> - Fine-tuning your agent on failure data
> - Versioning models and evaluating before deployment
> - A/B testing: Deploying new version to 10% of traffic first
> - Rollback mechanisms (if the new version is worse, rollback automatically)
> 
> **Part 3: Measuring Impact** (30 min)
> - Did retraining actually fix the problem? (Statistical testing)
> - Side effects: Did you fix failures while introducing new ones?
> - Cost-benefit: Is this improvement worth the retraining cost?
> - Deciding: Should we do this again? What to improve?
> 
> You'll have code for a complete feedback loop by the end.

**What to bring:**
- Laptop with Python 3.9+
- `pip` and familiarity with ML libraries (PyTorch, HuggingFace, etc.)
- Optional: Your own agent model to retrain

**Learning outcomes:**
- Build data pipelines from production to training
- Implement retraining with proper versioning and rollback
- Set up A/B testing for new agent versions
- Measure improvement statistically and decide on deployment

---

## SUPPORTING SESSIONS (2-3 more talks, brief descriptions)

### Session 5: Agents in Enterprise: The Observability Case Study

**Speaker:** [Enterprise AI Lead]  
**Duration:** 40 min + 10 min Q&A  

**Description:**
> "We tried deploying agents in enterprise without feedback loops. Six weeks and three production failures later, we built the loop. This is what we learned (and how much it cost us to learn it the hard way)."

---

### Session 6: Real-Time Evals at Scale (How Uber Does It)

**Speaker:** [Uber Engineer]  
**Duration:** 40 min + 10 min Q&A

**Description:**
> "Evaluating millions of agent outputs every day. Here's the infrastructure, the cost trade-offs, and the metrics that matter."

---

### Session 7: The Roadmap: Where Agent Feedback Loops Are Going

**Speaker:** [Arize Founder]  
**Duration:** 30 min + 10 min Q&A

**Description:**
> "The feedback loop is the foundation. Where does it go from here? Agent autonomy, multi-agent systems, and why observability is the infrastructure of autonomous systems."

---

## SCHEDULE LAYOUT

| Time | Main Track | Track 2 | Track 3 | Track 4 |
|------|-----------|---------|---------|---------|
| **9:00am** | Registration + coffee | | | |
| **9:30am** | Aayush — Agent Reliability (KEYNOTE) | | | |
| **10:30am** | Break + networking | | | |
| **11:00am** | Chi — Agent Memory | Enterprise Case Study | Observability WS (PM group) | TBD |
| **12:00pm** | Lunch | | | |
| **1:30pm** | Eno — Continuous Evals | Real-Time Evals @ Uber | Evals WS (afternoon group) | TBD |
| **2:30pm** | Break + networking | | | |
| **3:00pm** | Stuart — Autonomous Engineering | Roadmap Talk | Orchestration WS (afternoon) | Retraining WS (small) |
| **4:00pm** | Wrap-up + closing remarks | | | |
| **4:30pm** | Venue closes | | | |

---

## MARKETING MATERIALS NEEDED

For each session:
- [ ] Hero image (speaker + session topic)
- [ ] Social media quote (one standout insight from the talk)
- [ ] LinkedIn event description (in event posting)
- [ ] Email description (for promotional emails)
- [ ] Website session card (title + description + speaker)
- [ ] Signage for day-of (in each room)

---

**Last Updated:** April 28, 2026  
**Created by:** DevRel / Events  
**Approval needed from:** Speakers (confirm descriptions align with their intent)
