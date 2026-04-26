# Excellent blog example

*An example of a strong blog post opening on AI observability. Use to calibrate voice, structure, and specificity.*

---

## Why most teams are debugging agents wrong

When an agent returns a bad result, most teams do the same thing: they look at the output and try to reverse-engineer what went wrong.

That is the hard way.

The output tells you that something went wrong. The trace tells you what actually happened.

A trace is a record of everything the agent did: the tools it called, the inputs it received, the outputs it produced at each step, and the latency of every operation. When an agent misbehaves, the trace is where the answer lives.

Most teams know they should be looking at traces. Fewer teams have built the habit of starting there. And almost no teams have a systematic process for inspecting traces across sessions to find patterns in agent failure.

This post covers how to change that.

### What a trace actually contains

Before you can use traces effectively, it helps to understand what is in them.

A trace is made up of spans. Each span represents one operation in the agent's execution: a call to the language model, a tool invocation, a retrieval step, a function call. Spans are nested, so you can see the full sequence of what the agent did and in what order.

For each span, you typically have:
- The input (what was sent)
- The output (what was returned)
- The latency (how long it took)
- Status (success or error)
- Any metadata the instrumentation captures

When you look at a span for a tool call that failed, you can see exactly what the agent sent, what the tool returned, and how the agent handled the response. That is information you cannot get from the final output alone.

### The three most common failure modes traces reveal

**Tool-calling errors.** The agent called a tool with the wrong parameters, or called a tool that was not appropriate for the task. This is almost invisible in the final output but obvious in the trace.

**Context window drift.** The model received a different prompt than expected because the context was constructed incorrectly. The trace shows you exactly what was in the system prompt and user message at the time of the call.

**Cascading failures.** One step in the chain failed silently, and the agent continued with bad state. The trace shows you the exact point of failure and every step that followed.

---

*[Blog continues with sections on how to set up trace inspection, how to build a debugging workflow, and how to connect trace analysis to evaluation.]*

---

## What makes this strong

- Opens with a specific, debatable observation ("most teams are debugging agents wrong")
- Gets to the technical substance quickly
- Uses precise terminology (trace, span, tool call, context window)
- Names real failure modes with specific examples
- Respects the reader's technical intelligence
- No hype language
- Structure follows the blog template: problem, why it matters, technical concept, workflow, failure modes
