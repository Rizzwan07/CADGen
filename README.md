# CadGen - Text to 3D CAD Model Generator

Turn plain English descriptions into downloadable 3D CAD models (STEP, STL, DXF) with a live 3D preview in your browser.

---

## What Does This Do?

You type something like:

> "A box 50x30x20mm with 3mm fillets on all edges"

And it generates a real 3D model you can download and open in any CAD software (Fusion 360, SolidWorks, FreeCAD, etc.)

---

## Prerequisites (What You Need Installed)

Before starting, make sure you have these installed on your computer:

| Tool | Download Link | Check if installed |
|------|--------------|-------------------|
| Python 3.10+ | https://www.python.org/downloads/ | `python --version` |
| Node.js 18+ | https://nodejs.org/ | `node --version` |
| Git | https://git-scm.com/downloads | `git --version` |

---

## Step-by-Step Setup Guide

### Step 1: Clone the Repository

Open your terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
git clone https://github.com/Rizzwan07/CADGen.git
cd CADGen
```

---

### Step 2: Set Up the Backend (Python Server)

#### 2.1 Go to the backend folder

```bash
cd backend
```

#### 2.2 Create a virtual environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\Activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line. This means it worked.

#### 2.3 Install the required packages

```bash
pip install -r requirements.txt
```

This will install FastAPI, CadQuery, LangChain, and other dependencies. It may take a few minutes.

#### 2.4 Get Your API Keys

You need two API keys (both are free):

**Cerebras API Key** (for the AI model):
1. Go to https://cloud.cerebras.ai/
2. Sign up for a free account
3. Go to API Keys section
4. Create a new key and copy it

**LangSmith API Key** (for monitoring, optional):
1. Go to https://smith.langchain.com/
2. Sign up for a free account
3. Go to Settings > API Keys
4. Create a new key and copy it

#### 2.5 Create the .env file

Create a new file called `.env` inside the `backend` folder with this content:

```
CEREBRAS_API_KEY=paste_your_cerebras_key_here
LANGCHAIN_API_KEY=paste_your_langsmith_key_here
```

Replace the placeholder text with your actual keys.

#### 2.6 Start the backend server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this terminal open and running.

---

### Step 3: Set Up the Frontend (Web Interface)

Open a **new terminal window** (keep the backend running in the first one).

#### 3.1 Go to the frontend folder

```bash
cd CADGen/frontend
```

#### 3.2 Install the required packages

```bash
npm install
```

#### 3.3 Start the frontend

```bash
npm run dev
```

You should see:
```
Local: http://localhost:5173/
```

#### 3.4 Open in your browser

Go to http://localhost:5173 in your browser. You should see the CadGen interface.

---

## How to Use

1. Type a description of a 3D part in the text box
2. Press Enter or click the send button
3. Wait for the model to generate (you'll see a loading animation)
4. View the 3D model in the preview panel (rotate with mouse, scroll to zoom)
5. Download the model as STEP, STL, or DXF

---

## Example Prompts (60+)

### Basic Shapes (Start Here)
1. `A cube 40mm with 2mm fillets on all edges`
2. `Cylinder 30mm diameter, 50mm tall`
3. `Sphere 25mm radius`
4. `A box 80x50x20mm`
5. `A tube 50mm outer diameter, 40mm inner diameter, 80mm long`
6. `A cone 30mm base diameter, 50mm tall`
7. `A rectangular block 100x60x15mm with 5mm chamfers on top edges`

### Plates and Brackets
8. `A flat plate 100x60x5mm with 4 mounting holes in the corners`
9. `L-bracket 80x60mm, 5mm thick, with M4 holes`
10. `T-bracket 100mm wide, 60mm tall, 5mm thick, with 3 holes on each arm`
11. `A wall mounting plate 120x80x4mm with 6 countersunk holes evenly spaced`
12. `A corner bracket with two 50mm arms, 4mm thick, with reinforcement rib`
13. `A U-bracket 80mm wide, 40mm deep, 5mm thick, with holes on each side`

### Fasteners and Hardware
14. `Hex bolt M12, 30mm shaft length, hex head 19mm across flats, with thread grooves`
15. `Hex nut M10`
16. `A washer 20mm OD, 10mm ID, 2mm thick`
17. `A wing nut M8, with two wings 20mm wide`
18. `A socket head cap screw M8, 25mm long`
19. `A T-nut for 10mm T-slot, M6 thread`

### Gears
20. `Spur gear 24 teeth, module 2, 15mm face width, 12mm bore`
21. `Spur gear 32 teeth, module 2.5, 12mm face width, 10mm bore`
22. `Spur gear 16 teeth, module 3, 10mm face width, 8mm bore`
23. `A sprocket with 18 teeth, 100mm pitch diameter, 8mm thick, 15mm bore`
24. `A simple pulley 50mm diameter, 20mm wide, with V-groove and 10mm bore`
25. `A timing belt pulley 20 teeth, 5mm pitch, 10mm wide, 8mm bore`

### Enclosures and Boxes
26. `A rectangular enclosure 120x80x40mm, 4mm walls, open top`
27. `Enclosure box 100x70x35mm with 3mm wall thickness, open top, 4 screw bosses in corners`
28. `A round housing 60mm diameter, 30mm tall, 3mm walls, with a lid flange`
29. `Electronics enclosure 80x50x25mm, 2mm walls, with ventilation slots on sides`
30. `A battery box 70x40x20mm with snap-fit lid slots`

### Flanges and Pipe Fittings
31. `Pipe flange 80mm OD, 40mm ID, 10mm thick, 4 bolt holes on 60mm PCD`
32. `A blind flange 100mm diameter, 12mm thick, with 8 M6 bolt holes on 80mm PCD`
33. `A reducing flange from 60mm to 40mm bore, 15mm thick`
34. `A pipe coupling 50mm OD, 30mm ID, 40mm long, with grooves for O-rings`

### Heat Sinks
35. `A heat sink 60x40x30mm with 8 thin fins 1.5mm thick spaced 4mm apart on top`
36. `A round heat sink 50mm diameter, 10mm base, 12 radial fins 1mm thick, 20mm tall`
37. `A CPU cooler base plate 40x40x5mm with 6 fins 1mm thick on top`

### Structural Profiles
38. `T-slot rail 100mm long, 20mm wide, 20mm tall`
39. `An I-beam cross section 50mm tall, 30mm wide, 5mm thick, extruded 150mm`
40. `A C-channel 40mm tall, 20mm wide, 3mm thick, 120mm long`
41. `A step block: 60x40mm base 20mm tall, with a 40x40mm step 10mm tall on top`

### Knobs and Handles
42. `A knurled knob 30mm diameter, 15mm tall, with 6mm through hole`
43. `A star knob with 5 lobes, 40mm diameter, 12mm tall, M6 center hole`
44. `A cylindrical handle 20mm diameter, 80mm long, with M8 insert hole on one end`

### Bearings and Housings
45. `A bearing housing with 30mm bore, 4 mounting feet`
46. `A pillow block bearing housing 40mm bore, 120mm long base, 2 bolt holes`
47. `A flange bearing mount 35mm bore, 80mm flange OD, 4 bolt holes`

### Shafts
48. `A stepped shaft: 20mm diameter x 30mm, then 15mm diameter x 40mm, then 10mm diameter x 20mm`
49. `A shaft collar 25mm bore, 40mm OD, 15mm wide, with M5 clamping screw hole`
50. `A shaft coupler 10mm bore on both ends, 30mm OD, 40mm long`

### Everyday Objects
51. `A phone stand 70mm wide, 80mm tall, angled 70 degrees, with 10mm lip`
52. `A cable clip for 8mm cable, screw-mount base with 4mm hole`
53. `A hook with 30mm opening, 5mm thick, mounting plate 40x30mm with 2 holes`
54. `A cam with 20mm base circle, 8mm lift, 10mm thick, 6mm bore`

### Complex Parts
55. `A motor mounting plate 150x100x8mm with central bore 40mm, 4 bolt holes on 60mm circle`
56. `A rectangular housing 140x90x50mm, 4mm walls, hollow, 4 M5 mounting holes at bottom corners, ventilation slots on sides`
57. `A sensor mount bracket: L-shape 40x30mm, 3mm thick, with 20mm ring clamp on one end`
58. `A PCB standoff 5mm diameter, 10mm tall, M3 hole on top, 8mm base with 2.5mm mounting hole`
59. `A spring coil 10mm wire, 40mm diameter, 5 turns, 60mm tall`
60. `A DIN rail clip 35mm wide, snap-fit profile, with mounting plate 45x30mm`

---

## Tips for Best Results

- **Always include dimensions** in millimeters (e.g., "50mm wide" not just "wide")
- **Be specific about hole positions** (e.g., "4 holes spaced 60mm apart" not just "some holes")
- **For gears**, always specify: number of teeth, module, face width, and bore diameter
- **For bolts**, say "with thread grooves" instead of "with actual threads"
- **Keep fillets/chamfers small** relative to the part (e.g., 2mm fillet on a 20mm part)
- **If it fails**, try simplifying — remove fillets/chamfers and add fewer features
- **Separate features with commas** for clarity

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot reach backend" | Make sure the backend is running on port 8000 |
| Model looks wrong | Try rephrasing with more specific dimensions |
| 429 rate limit error | Wait a few seconds, it will auto-retry |
| "pip install" fails | Make sure your virtual environment is activated |
| "npm install" fails | Make sure Node.js is installed (check with `node --version`) |
| Blank 3D viewer | Try refreshing the page |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Qwen-3-235B on Cerebras |
| Backend | Python, FastAPI, CadQuery, LangChain |
| Frontend | React, TypeScript, Three.js, Tailwind CSS, Framer Motion |
| 3D Viewer | react-three-fiber |
| Monitoring | LangSmith |

---

## Project Structure

```
CADGen/
├── backend/
│   ├── main.py              # API server (FastAPI)
│   ├── generator.py         # AI code generation + CadQuery execution
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Your API keys (create this yourself)
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main UI with input and controls
│   │   ├── Viewer.tsx       # 3D model viewer (Three.js)
│   │   └── main.tsx         # App entry point
│   ├── package.json         # JavaScript dependencies
│   └── index.html
└── README.md
```

---

## License

MIT
