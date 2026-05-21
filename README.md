# CadGen — Text to 3D CAD Model Generator

Describe a part in plain English, get a downloadable 3D model (STEP, STL, DXF) with a live preview in your browser. Refine your model with follow-up prompts — up to 3 edits per design.

---

## Quick Start

### Prerequisites

- Python 3.10+ → [python.org](https://www.python.org/downloads/)
- Node.js 18+ → [nodejs.org](https://nodejs.org/)

### 1. Clone & run backend

```bash
git clone https://github.com/Rizzwan07/CADGen.git
cd CADGen/backend
python -m venv venv
```

Activate virtual environment:
- **Windows:** `.\venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
CEREBRAS_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_key_here
```

Get keys: [Cerebras](https://cloud.cerebras.ai/) (free) | [LangSmith](https://smith.langchain.com/) (optional)

Start the server:
```bash
python main.py
# → Uvicorn running on http://0.0.0.0:8001
```

### 2. Run frontend (new terminal)

```bash
cd CADGen/frontend
npm install
npm run dev
# → http://localhost:5173
```

Open http://localhost:5173 in your browser. Done.

---

## How to Use

1. Type a description: *"A box 80x50x20mm with 3mm fillets"*
2. Get a 3D model in 5-15 seconds
3. Edit it: *"Add 4 holes in the corners"* (3 edits per design)
4. Download as STEP, STL, or DXF
5. Click **"New Design"** to start fresh

### Iterative Editing

```
You:   "Make a plate 100x60x5mm"                   → 3 edits remaining
You:   "Add 4 mounting holes in corners"            → 2 edits remaining
You:   "Fillet all edges 2mm"                       → 1 edit remaining
You:   "Add a slot in the center"                   → 0 edits remaining → "New Design"
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Qwen-3-235B on Cerebras |
| Backend | Python, FastAPI, CadQuery, LangChain |
| Frontend | React, TypeScript, Three.js, Tailwind CSS |
| 3D Viewer | react-three-fiber |

---

## Project Structure

```
CADGen/
├── backend/
│   ├── main.py           # API server
│   ├── generator.py      # AI generation + sessions
│   └── .env              # API keys (you create this)
├── frontend/
│   └── src/
│       ├── App.tsx       # UI + edit counter
│       └── Viewer.tsx    # 3D preview
├── docs/
│   ├── ARCHITECTURE.md   # Diagrams, pipelines, flowcharts
│   ├── EXAMPLES.md       # 45+ example prompts
│   └── TROUBLESHOOTING.md
└── README.md
```

---

## Documentation

- [Architecture & Flowcharts](docs/ARCHITECTURE.md) — How it works under the hood
- [Example Prompts](docs/EXAMPLES.md) — 45+ prompts with editing sessions
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues & fixes

---

## License

MIT
