# Architecture

## High-Level Pipeline

```
User prompt → Frontend (React) → Backend (FastAPI) → Cerebras LLM
                                                          ↓
                                                  CadQuery Python code
                                                          ↓
                                                  Execute in sandbox
                                                          ↓
                                                  Export STL/STEP/DXF
                                                          ↓
                                              Return to browser + store in session
```

---

## Detailed Request Flow

```
User types prompt
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND                                                     │
│  • Sends {prompt, session_id} to backend                    │
│  • Shows loading animation                                   │
│  • On response: render 3D model, show edit counter           │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /generate
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND                                                      │
│                                                              │
│  1. Check session_id                                         │
│     ├── Exists? Get previous code, increment edit count     │
│     └── New? Create session, edit count = 0                  │
│                                                              │
│  2. Build LLM prompt                                         │
│     ├── Has previous code? "Current model: {code}            │
│     │                       Modify it to: {user prompt}"     │
│     └── No previous code? Just send user prompt              │
│                                                              │
│  3. Call Cerebras LLM (Qwen-3-235B)                         │
│     ├── 429 error? Retry with backoff (up to 5x)            │
│     └── Success? Get generated CadQuery Python code          │
│                                                              │
│  4. Execute code in sandbox                                  │
│     ├── Success? Export STL + STEP + DXF                     │
│     │            Store code in session                        │
│     │            Return files + session_id + edits_remaining │
│     └── Error? Feed error back to LLM (up to 3 retries)     │
│                ├── Fixed? Export and return                   │
│                └── Still broken? Return friendly error msg    │
└─────────────────────────────────────────────────────────────┘
```

---

## Session & Iterative Editing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ REQUEST 1: "Make a box 50x30x20mm"                              │
│                                                                  │
│  • No session_id → create session "abc123"                      │
│  • LLM generates: result = cq.Workplane("XY").box(50,30,20)    │
│  • Store code in session                                         │
│  • Response: {files, session_id: "abc123", edits_remaining: 3}  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ REQUEST 2: "Add 4 holes" + session_id: "abc123"                 │
│                                                                  │
│  • Lookup session → get previous box code                       │
│  • LLM prompt: "Current model: {code}. Modify: add 4 holes"    │
│  • LLM modifies code → execute → export                         │
│  • Update session with new code                                  │
│  • Response: {files, edits_remaining: 2}                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                      (repeat up to 3 edits)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ EDITS EXHAUSTED                                                  │
│  • Frontend disables input                                       │
│  • Shows "New Design" button                                     │
│  • Click → clears session → starts fresh                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Self-Healing

```
LLM generates code
        │
        ▼
   Execute code
        │
   ┌────┴────┐
   ▼         ▼
SUCCESS    FAILED
   │         │
   │         ▼
   │    Feed error back to LLM:
   │    "Code failed with: {error}. Fix it."
   │         │
   │         ▼
   │    Execute again
   │         │
   │    ┌────┴────┐
   │    ▼         ▼
   │ SUCCESS    FAILED (retry up to 3x)
   │    │         │
   │    │         ▼ (after 3 failures)
   │    │    LLM explains error in plain English
   │    │    (user never sees Python tracebacks)
   │    │
   ▼    ▼
Export STL/STEP/DXF → Store in session → Return to user
```

---

## System Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                           │
│  • Types prompts / edits                                        │
│  • Views 3D model (rotate/zoom)                                 │
│  • Downloads files                                               │
│  • Sees edit counter                                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                FRONTEND — http://localhost:5173                   │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  App.tsx       │  │  Viewer.tsx    │  │  State:        │   │
│  │  • Input       │  │  • Three.js   │  │  • sessionId   │   │
│  │  • Edit counter│  │  • STL render │  │  • editsLeft   │   │
│  │  • Downloads   │  │  • Orbit ctrl │  │  • result      │   │
│  │  • New Design  │  │               │  │                │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                BACKEND — http://localhost:8001                    │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  main.py       │  │  generator.py  │  │  sessions{}    │   │
│  │  • /generate   │  │  • LLM call    │  │  (in-memory)   │   │
│  │  • /download   │  │  • Sandbox exec│  │  • code        │   │
│  │  • CORS        │  │  • Self-heal   │  │  • edit count  │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │  Cerebras AI        │         │  LangSmith          │       │
│  │  (Qwen-3-235B)      │         │  (Monitoring)       │       │
│  │  Generates code     │         │  Traces LLM calls   │       │
│  └─────────────────────┘         └─────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Decisions

| Decision | Why |
|----------|-----|
| **Cerebras over OpenAI/Groq** | Free tier, higher rate limits, fast inference |
| **CadQuery over OpenSCAD** | Produces STEP files for real manufacturing |
| **LangChain wrapper** | Easy to swap LLM providers, built-in monitoring |
| **Self-healing retries** | LLMs make small errors — feeding error back lets it self-correct |
| **In-memory sessions (dict)** | Zero dependencies, no database. Sessions lost on restart (fine for MVP) |
| **3 edit limit** | After 4+ edits, code complexity causes LLM mistakes |
| **LLM auto-detects new vs edit** | User doesn't need to explicitly signal "new model" |
| **Sandboxed exec()** | Prevents AI-generated code from harming the system |
| **STL + STEP + DXF** | Covers 3D printing, CAD software, laser cutting |
| **Three.js viewer** | Real-time 3D preview, no plugins needed |

---

## Security: Sandboxed Execution

Generated code runs in a restricted context:

```python
exec_globals = {"cq": cq, "math": math}
exec(code, exec_globals)
```

| Allowed | Blocked |
|---------|---------|
| `cq` (CadQuery) | `os`, `subprocess`, `sys` |
| `math` | `open()`, `requests` |
| | `__import__` |

For production: use Docker container isolation.

---

## Token Usage

| Request type | Approx tokens |
|-------------|---------------|
| First prompt (no session) | ~2,000 (system prompt) + ~30 (user) = **~2,030** |
| Edit (with previous code) | ~2,000 + ~400 (prev code) + ~30 = **~2,430** |
| After 3 edits | Same ~2,430 (doesn't grow — only last code stored) |

Cost of iterative editing: ~400 extra tokens per request (fixed, doesn't accumulate).

---

## Production Deployment

| Concern | Solution |
|---------|----------|
| Sessions lost on restart | Use Redis |
| Code execution safety | Docker container per execution |
| Multiple users | Add rate limiting per user |
| Frontend hosting | `npm run build` → serve with Nginx |
| Backend scaling | gunicorn/uvicorn with multiple workers |
