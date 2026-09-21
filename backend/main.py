import asyncio
import csv
import io
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from swarm_engine.environment import WarehouseMap
from swarm_engine.agent import AMR
from swarm_engine.mesh import MeshNetwork
from swarm_engine.auction import run_decentralized_auction

app = FastAPI(title="AMR Swarm Engine")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global System State
warehouse = WarehouseMap(100, 100)
mesh = MeshNetwork(radio_range=15)

# Initialize 4 Agents at four warehouse corners
bots = [
    AMR("Bot-Alpha", (0, 0)),
    AMR("Bot-Bravo", (0, 99)),
    AMR("Bot-Charlie", (99, 0)),
    AMR("Bot-Delta", (99, 99)),
]

pending_tasks = []
completed_tasks = []
task_auction_logs = []

# Active WebSocket Connections
active_websockets: list[WebSocket] = []


class TaskModel(BaseModel):
    id: str
    x: int
    y: int
    type: str = "LOAD"


@app.on_event("startup")
async def start_simulation_loop():
    asyncio.create_task(simulation_tick_loop())

async def simulation_tick_loop():
    global pending_tasks
    while True:
        # 1. Run Decentralized Auctions for Pending Tasks
        unassigned_tasks = []
        for task in pending_tasks:
            winner_id = run_decentralized_auction(task, bots, warehouse)
            if winner_id:
                task_auction_logs.append({
                    "task_id": task['id'],
                    "winner": winner_id,
                    "pos": (task['x'], task['y'])
                })
            else:
                unassigned_tasks.append(task)
        pending_tasks = unassigned_tasks

        # 2. P2P Mesh Gossip Sync
        mesh.gossip_sync(bots)

        # 3. Decentralized Collision Resolution (Time-Space Reservation)
        intents = {bot.id: bot.get_intent() for bot in bots}
        approved_moves = {}

        for bot in bots:
            intended = intents[bot.id]
            conflict = False
            
            for other in bots:
                if bot.id == other.id: continue
                
                # Rule 1: Someone is already in that spot and isn't moving
                if other.pos == intended and intents[other.id] == other.pos:
                    conflict = True
                
                # Rule 2: Head-on collision (Bots trying to swap spaces)
                if intended == other.pos and intents[other.id] == bot.pos:
                    if bot.id > other.id:  # ID Tie-breaker yields
                        conflict = True
                        
                # Rule 3: Two bots want the exact same empty spot
                if intended == intents[other.id] and intended != bot.pos:
                    if bot.id > other.id:  # ID Tie-breaker yields
                        conflict = True

            # If conflict detected, bot must stay at current pos
            approved_moves[bot.id] = bot.pos if conflict else intended

        # 4. Tick each bot state machine with their approved move
        bot_telemetry = []
        for bot in bots:
            telemetry = bot.tick(warehouse, approved_next_pos=approved_moves[bot.id])
            if telemetry:
                bot_telemetry.append(telemetry)

        # 5. Broadcast live state to all connected UI clients
        payload = {
            "bots": bot_telemetry,
            "pending_tasks_count": len(pending_tasks),
            "completed_tasks_count": sum(len(b.completed_tasks) for b in bots),
            "latest_auction_logs": task_auction_logs[-5:]
        }

        disconnected = []
        for ws in active_websockets:
            try:
                await ws.send_json(payload)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            active_websockets.remove(ws)

        await asyncio.sleep(0.25)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_websockets.remove(websocket)


@app.post("/api/add-task")
async def add_single_task(task: TaskModel):
    if not warehouse.is_valid(task.x, task.y):
        raise HTTPException(status_code=400, detail="Target coordinate lands on a shelf obstacle or out of bounds.")
    
    task_dict = task.dict()
    pending_tasks.append(task_dict)
    return {"status": "QUEUED", "task": task_dict}


@app.post("/api/upload-tasks")
async def upload_csv_tasks(file: UploadFile = File(...)):
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    count = 0
    for row in reader:
        x, y = int(row['x_coord']), int(row['y_coord'])
        if warehouse.is_valid(x, y):
            pending_tasks.append({
                "id": row['task_id'],
                "x": x,
                "y": y,
                "type": row.get('task_type', 'LOAD')
            })
            count += 1

    return {"status": "SUCCESS", "tasks_imported": count}