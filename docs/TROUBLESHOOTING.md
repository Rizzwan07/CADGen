# Troubleshooting

## Setup Issues

| Problem | Solution |
|---------|----------|
| `python --version` not found | Install Python from https://www.python.org/downloads/ and add to PATH |
| `node --version` not found | Install Node.js from https://nodejs.org/ |
| `pip install` fails with errors | Make sure virtual environment is activated (you see `(venv)` in terminal) |
| `npm install` fails | Delete `node_modules` folder and run `npm install` again |
| `ModuleNotFoundError: cadquery` | You're not in the virtual environment. Run `source venv/bin/activate` or `.\venv\Scripts\activate` |
| `.env` file not working | Make sure it's named exactly `.env` (not `.env.txt`) and is inside the `backend/` folder |
| Port 8001 already in use | Another process is using it. Kill it or change port in `main.py` |
| Port 5173 already in use | Vite auto-picks another port — check terminal output |

## Runtime Issues

| Problem | Solution |
|---------|----------|
| "Cannot reach backend" | Make sure `python main.py` is running in a separate terminal |
| 429 rate limit error | You're sending too many requests. Wait 10-30 seconds, auto-retry handles this |
| Model looks wrong | Rephrase with more specific dimensions |
| Blank 3D viewer | Refresh the page |
| Model disappears after edit | The edit failed — check for error messages below the input |
| "No edits remaining" | Click "New Design" to start a fresh session |
| Very slow generation | Cerebras may be under load. Wait and retry |
| Backend crashes | Check terminal for error. Usually a missing dependency — run `pip install -r requirements.txt` again |

## Common Generation Errors

| Error message | What it means | Fix |
|---------------|--------------|-----|
| "Fillet/chamfer too large" | Your fillet radius is bigger than the edge allows | Use smaller fillet values (1-2mm for small parts) |
| "newS" or "BRep" error | A geometry operation failed | Simplify the part, avoid overlapping features |
| "has no attribute" | LLM used a CadQuery method that doesn't exist | Retry — the self-healing should fix it |
| "result variable not found" | Generated code didn't assign to `result` | Retry with a clearer prompt |

## Platform-Specific Issues

### Windows

| Problem | Solution |
|---------|----------|
| `.\venv\Scripts\activate` fails in PowerShell | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first |
| Python not found after install | Check "Add to PATH" during Python installation, or add manually |

### Mac

| Problem | Solution |
|---------|----------|
| `python` command not found | Use `python3` instead |
| Permission denied on install | Use `pip3 install --user -r requirements.txt` |

### Linux

| Problem | Solution |
|---------|----------|
| `python3-venv` not installed | Run `sudo apt install python3-venv` (Ubuntu/Debian) |
| Permission errors | Don't use `sudo` with pip inside a venv |

## Still Stuck?

1. Make sure both terminals are running (backend on 8001, frontend on 5173)
2. Check the backend terminal for error messages
3. Try a simple prompt first: `A cube 40mm`
4. If that works, the issue is with your specific prompt — simplify it
