import os
import uuid
import time
import tempfile
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "cadgen")

llm = ChatOpenAI(
    model="qwen-3-235b-a22b-instruct-2507",
    temperature=0,
    max_tokens=2048,
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY"),
)

SYSTEM_PROMPT = """You are a CAD code generator. You write CadQuery (Python) code to create 3D models.

RULES:
1. Only output valid Python code using the `cadquery` library
2. The final result MUST be assigned to a variable called `result`
3. Do NOT include any imports — `cadquery` is already imported as `cq`
4. Do NOT include print statements or file exports
5. Do NOT include markdown code blocks or explanations
6. Use millimeters as the unit
7. Keep designs parametric and clean
8. Use proper CadQuery operations: Workplane, box, cylinder, sphere, extrude, cut, fillet, chamfer, etc.
9. NEVER use .rArray() — it does not exist. For rectangular patterns use .rect(xSpacing, ySpacing, forConstruction=True).vertices() or .pushPoints([...])
10. NEVER use .polarArray() without checking signature: .polarArray(radius, startAngle, angle, count)
11. Always select edges with .edges() before calling .fillet() or .chamfer()
12. Keep fillet/chamfer radii small relative to the smallest feature dimension
13. If you receive existing model code with a modification request, MODIFY that code — keep all existing features and only add/change what the user asks. Do NOT rewrite from scratch unless the request is clearly a brand new unrelated model.

EXAMPLE OUTPUT for "Create a box 50x30x20 with 3mm fillets on all edges":
result = (
    cq.Workplane("XY")
    .box(50, 30, 20)
    .edges()
    .fillet(3)
)

EXAMPLE OUTPUT for "A plate with 4 corner holes":
result = (
    cq.Workplane("XY")
    .box(100, 60, 5)
    .faces(">Z")
    .workplane()
    .rect(80, 40, forConstruction=True)
    .vertices()
    .hole(6)
)

EXAMPLE OUTPUT for "L-bracket 80x60mm, 5mm thick, with M4 holes":
base = cq.Workplane("XY").box(80, 60, 5)
wall = (
    cq.Workplane("XZ")
    .workplane(offset=-30)
    .box(80, 40, 5)
    .translate((0, -30, 20))
)
bracket = base.union(wall)
result = (
    bracket
    .faces(">Z")
    .workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .hole(4)
)

EXAMPLE OUTPUT for "Cylinder 40mm diameter, 60mm tall, 10mm hole through center":
result = (
    cq.Workplane("XY")
    .circle(20)
    .extrude(60)
    .faces(">Z")
    .workplane()
    .hole(10)
)

EXAMPLE OUTPUT for "Pipe flange 80mm OD, 40mm ID, 10mm thick, 4 bolt holes on 60mm PCD":
result = (
    cq.Workplane("XY")
    .circle(40)
    .circle(20)
    .extrude(10)
    .faces(">Z")
    .workplane()
    .polarArray(30, 0, 360, 4)
    .hole(6)
)

CRITICAL — GEAR GENERATION:
If the user asks for ANY gear (spur gear, helical gear, etc.), you MUST generate individual tooth profiles using math and polyline. NEVER just make a cylinder. A gear MUST have visible teeth. Follow this pattern EXACTLY:

EXAMPLE OUTPUT for "Spur gear 20 teeth, module 2, 10mm face width, 8mm bore":
import math
num_teeth = 20
module = 2
face_width = 10
bore_diameter = 8
pitch_radius = module * num_teeth / 2.0
addendum = module
dedendum = 1.25 * module
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum
tooth_angle = 2.0 * math.pi / num_teeth
points = []
for i in range(num_teeth):
    angle = i * tooth_angle
    tip_half = tooth_angle * 0.15
    root_half = tooth_angle * 0.35
    a1 = angle - root_half
    a2 = angle - tip_half
    a3 = angle + tip_half
    a4 = angle + root_half
    points.append((root_radius * math.cos(a1), root_radius * math.sin(a1)))
    points.append((outer_radius * math.cos(a2), outer_radius * math.sin(a2)))
    points.append((outer_radius * math.cos(a3), outer_radius * math.sin(a3)))
    points.append((root_radius * math.cos(a4), root_radius * math.sin(a4)))
gear_profile = cq.Workplane("XY").polyline(points).close()
result = (
    gear_profile.extrude(face_width)
    .faces(">Z")
    .workplane()
    .hole(bore_diameter)
)

CRITICAL — BOLT/SCREW/THREAD GENERATION:
If the user asks for a bolt or screw with threads, you MUST:
1. Create a solid hex head and solid shaft FIRST as one solid body
2. Then cut ring grooves at regular pitch intervals into the shaft to simulate threads
3. NEVER create threads as separate floating geometry — always start with a SOLID cylinder and CUT into it
4. The shaft must remain one connected solid piece

EXAMPLE OUTPUT for "M12 bolt, 30mm shaft, hex head 19mm across flats":
import math
across_flats = 19
head_height = 8
shaft_diameter = 12
shaft_length = 30
thread_pitch = 1.75
thread_depth = 0.8
minor_radius = shaft_diameter / 2.0 - thread_depth
hex_radius = across_flats / 2.0 / math.cos(math.radians(30))
hex_pts = [(hex_radius * math.cos(math.radians(a)), hex_radius * math.sin(math.radians(a))) for a in range(0, 360, 60)]
head = cq.Workplane("XY").polyline(hex_pts).close().extrude(head_height)
shaft = cq.Workplane("XY").circle(shaft_diameter / 2.0).extrude(-shaft_length)
bolt = head.union(shaft)
num_grooves = int(shaft_length / thread_pitch)
for i in range(num_grooves):
    z_pos = -(i * thread_pitch) - thread_pitch * 0.75
    groove = (
        cq.Workplane("XY")
        .workplane(offset=z_pos)
        .circle(shaft_diameter / 2.0 + 0.1)
        .circle(minor_radius)
        .extrude(thread_pitch * 0.4)
    )
    bolt = bolt.cut(groove)
result = bolt

EXAMPLE OUTPUT for "Hollow box enclosure 100x70x40mm, 3mm walls, open top":
outer = cq.Workplane("XY").box(100, 70, 40)
inner = (
    cq.Workplane("XY")
    .workplane(offset=3)
    .box(94, 64, 40)
)
result = outer.cut(inner)

EXAMPLE OUTPUT for "Threaded knob 30mm diameter, 20mm tall, with knurling pattern":
import math
base = cq.Workplane("XY").circle(15).extrude(20)
knurl_cuts = cq.Workplane("XY")
num_knurls = 30
for i in range(num_knurls):
    angle = i * (360 / num_knurls)
    rad = math.radians(angle)
    x = 15 * math.cos(rad)
    y = 15 * math.sin(rad)
    knurl_cuts = knurl_cuts.moveTo(x, y).circle(1.5)
knurl_body = knurl_cuts.extrude(20)
result = base.cut(knurl_body).faces(">Z").workplane().hole(6)

EXAMPLE OUTPUT for "Bearing housing with 30mm bore and 4 mounting feet":
housing = (
    cq.Workplane("XY")
    .circle(30)
    .circle(15)
    .extrude(25)
)
base_plate = (
    cq.Workplane("XY")
    .box(80, 80, 5)
)
result_body = base_plate.union(housing.translate((0, 0, 5)))
foot_positions = [(30, 30), (-30, 30), (30, -30), (-30, -30)]
result = (
    result_body
    .faces("<Z")
    .workplane()
    .pushPoints(foot_positions)
    .hole(8)
)

EXAMPLE OUTPUT for "Pulley 50mm diameter, 20mm wide, with V-groove and 10mm bore":
outer = cq.Workplane("XY").circle(25).extrude(20)
groove = (
    cq.Workplane("XZ")
    .moveTo(25, 10)
    .lineTo(18, 13)
    .lineTo(18, 7)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)
result = outer.cut(groove).faces(">Z").workplane().hole(10)

EXAMPLE OUTPUT for "Hex nut M10":
import math
s = 17
hex_pts = [(s/2 * math.cos(math.radians(a)), s/2 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
result = (
    cq.Workplane("XY")
    .polyline(hex_pts)
    .close()
    .extrude(8)
    .faces(">Z")
    .workplane()
    .hole(10)
)

EXAMPLE OUTPUT for "T-slot rail 100mm long, 20mm wide, 20mm tall":
profile = (
    cq.Workplane("XZ")
    .moveTo(-10, 0)
    .lineTo(-10, 12)
    .lineTo(-5, 12)
    .lineTo(-5, 16)
    .lineTo(-10, 16)
    .lineTo(-10, 20)
    .lineTo(10, 20)
    .lineTo(10, 16)
    .lineTo(5, 16)
    .lineTo(5, 12)
    .lineTo(10, 12)
    .lineTo(10, 0)
    .close()
)
result = profile.extrude(100)

EXAMPLE OUTPUT for "Spring coil 10mm wire, 40mm diameter, 5 turns, 60mm tall":
import math
helix_points = []
turns = 5
height = 60
coil_radius = 20
points_per_turn = 36
for i in range(turns * points_per_turn + 1):
    angle = math.radians(i * (360 / points_per_turn))
    z = height * i / (turns * points_per_turn)
    x = coil_radius * math.cos(angle)
    y = coil_radius * math.sin(angle)
    helix_points.append((x, y, z))
path = cq.Workplane("XY").spline(helix_points)
result = (
    cq.Workplane("XZ")
    .workplane(offset=coil_radius)
    .circle(5)
    .sweep(path)
)

EXAMPLE OUTPUT for "Ventilation slots 40x5mm on a plate":
plate = cq.Workplane("XY").box(100, 60, 5)
slot_positions = [(0, -10), (0, 0), (0, 10)]
result = (
    plate
    .faces(">Z")
    .workplane()
    .pushPoints(slot_positions)
    .slot2D(40, 5)
    .cutThruAll()
)

EXAMPLE OUTPUT for "Chamfered edges on top face only":
result = (
    cq.Workplane("XY")
    .box(50, 50, 30)
    .faces(">Z")
    .edges()
    .chamfer(2)
)

EXAMPLE OUTPUT for "Countersunk holes":
result = (
    cq.Workplane("XY")
    .box(80, 60, 10)
    .faces(">Z")
    .workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .cskHole(5, 10, 82)
)

EXAMPLE OUTPUT for "Counterbored holes":
result = (
    cq.Workplane("XY")
    .box(80, 60, 10)
    .faces(">Z")
    .workplane()
    .rect(60, 40, forConstruction=True)
    .vertices()
    .cboreHole(5, 10, 3)
)

Only output the code. Nothing else."""


sessions: dict[str, dict] = {}

MAX_EDITS = 3


def generate_cad(prompt: str, session_id: str = None) -> dict:
    prev_code = None
    if session_id and session_id in sessions:
        session = sessions[session_id]
        if session["edits"] >= MAX_EDITS:
            return {"error": "Edit limit reached. Start a new design.", "code": ""}
        prev_code = session["code"]
        session["edits"] += 1
    else:
        session_id = str(uuid.uuid4())[:8]
        sessions[session_id] = {"code": None, "edits": 0}

    if prev_code:
        user_content = f"Current model code:\n{prev_code}\n\nModify it to: {prompt}\n\nIf this request is clearly a brand new unrelated model, ignore the current code and start fresh."
    else:
        user_content = prompt

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    code = ""
    try:
        max_retries = 5
        response = None
        for attempt in range(max_retries):
            try:
                response = llm.invoke(messages)
                break
            except Exception as api_err:
                if "429" in str(api_err) or "too_many_requests" in str(api_err):
                    if attempt < max_retries - 1:
                        wait = 2 ** attempt
                        time.sleep(wait)
                        continue
                raise
        if response is None:
            return {"error": "Failed to reach AI service after multiple retries. Please try again.", "code": ""}
        code = response.content.strip()

        import cadquery as cq

        max_fix_attempts = 3
        for fix_attempt in range(max_fix_attempts):
            code = response.content.strip()

            if code.startswith("```"):
                code = code.split("\n", 1)[1]
                if code.endswith("```"):
                    code = code[:-3].strip()

            import math
            exec_globals = {"cq": cq, "math": math}
            try:
                exec(code, exec_globals)
            except Exception as exec_err:
                if fix_attempt < max_fix_attempts - 1:
                    messages.append(response)
                    hint = ""
                    err_str = str(exec_err)
                    if "newS" in err_str or "BRep" in err_str:
                        hint = " This usually means a geometry operation failed (e.g., fillet/chamfer radius too large, invalid boolean operation, or overlapping geometry). Try simplifying: use smaller fillet values, ensure parts don't overlap before union, and avoid operations on zero-thickness geometry."
                    elif "has no attribute" in err_str:
                        hint = " You used a method that doesn't exist in CadQuery. Do NOT use .rArray(). For rectangular patterns use .rect(x, y, forConstruction=True).vertices(). For polar patterns use .polarArray(radius, startAngle, angle, count)."
                    elif "Fillet" in err_str or "edges" in err_str:
                        hint = " Make sure to select edges with .edges() before calling .fillet()."
                    messages.append(HumanMessage(
                        content=f"That code failed with error: {exec_err}{hint}\n\nPlease fix the code. Output only the corrected code, nothing else."
                    ))
                    for attempt in range(max_retries):
                        try:
                            response = llm.invoke(messages)
                            break
                        except Exception as api_err:
                            if "429" in str(api_err) or "too_many_requests" in str(api_err):
                                if attempt < max_retries - 1:
                                    time.sleep(2 ** attempt)
                                    continue
                            raise
                    continue
                return {"error": _explain_error(str(exec_err), prompt), "code": code}

            result = exec_globals.get("result")
            if result is None:
                return {"error": "Code did not produce a 'result' variable", "code": code}
            break

        # Store code in session
        sessions[session_id]["code"] = code

        # Export files
        output_dir = os.path.join(tempfile.gettempdir(), "cadgen")
        os.makedirs(output_dir, exist_ok=True)

        file_id = str(uuid.uuid4())[:8]
        stl_name = f"{file_id}.stl"
        step_name = f"{file_id}.step"
        dxf_name = f"{file_id}.dxf"
        stl_path = os.path.join(output_dir, stl_name)
        step_path = os.path.join(output_dir, step_name)
        dxf_path = os.path.join(output_dir, dxf_name)

        cq.exporters.export(result, stl_path, exportType="STL")
        cq.exporters.export(result, step_path, exportType="STEP")
        try:
            cq.exporters.export(result.section(), dxf_path, exportType="DXF")
        except Exception:
            dxf_name = None
            dxf_path = None

        # Calculate model info
        bb = result.val().BoundingBox()
        width = round(bb.xlen, 2)
        depth = round(bb.ylen, 2)
        height = round(bb.zlen, 2)

        shape = result.val()
        volume = round(shape.Volume() / 1000, 2)  # mm³ to cm³
        surface_area = round(shape.Area() / 100, 2)  # mm² to cm²

        edits_remaining = MAX_EDITS - sessions[session_id]["edits"]

        resp = {
            "code": code,
            "stl_file": stl_name,
            "step_file": step_name,
            "stl_url": f"/download/{stl_name}",
            "step_url": f"/download/{step_name}",
            "session_id": session_id,
            "edits_remaining": edits_remaining,
            "model_info": {
                "width_mm": width,
                "depth_mm": depth,
                "height_mm": height,
                "volume_cm3": volume,
                "surface_area_cm2": surface_area,
            },
        }
        if dxf_name:
            resp["dxf_file"] = dxf_name
            resp["dxf_url"] = f"/download/{dxf_name}"
        return resp

    except Exception as e:
        user_error = _explain_error(str(e), prompt)
        return {"error": user_error, "code": code if 'code' in locals() else ""}


def _explain_error(error: str, prompt: str) -> str:
    try:
        resp = llm.invoke([
            SystemMessage(content="You help users fix their 3D model requests. Do not mention code or programming. Explain what part of their request caused the issue and ask them to provide specific missing details (dimensions, sizes, counts, spacing, etc.) that would help generate the model successfully. Be specific about what to add or change. Keep it to 2-3 sentences max."),
            HumanMessage(content=f"User asked to generate: \"{prompt}\"\n\nThe generation failed with: {error}\n\nTell the user what specific details they should add or change in their request to make it work."),
        ])
        return resp.content.strip()
    except Exception:
        return "Sorry, we couldn't generate that model. Try simplifying your request or breaking it into smaller parts."
