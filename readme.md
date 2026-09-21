```markdown
# Decentralized AMR Swarm Simulator

An end-to-end, full-stack simulation of a decentralized Multi-Agent System (MAS) for Autonomous Mobile Robots (AMRs) operating in a 100x100 warehouse environment. 

This project solves traditional centralized warehouse routing problems by utilizing edge-compute decision making, peer-to-peer (P2P) mesh networking for Wi-Fi dead zones, and the Contract Net Protocol for task auctioning.

## 🚀 Core Features

* **Decentralized Task Allocation:** Implements the Contract Net Protocol (CNP). Bots autonomously calculate bids for incoming tasks based on A* distance and battery depletion penalties. The lowest bid wins, eliminating the need for a central orchestrator.
* **P2P Mesh "Gossip" Protocol:** The warehouse features simulated "Dead Zones" where central Wi-Fi drops. Bots within a 15-meter radius automatically share state vectors (claimed tasks, completed tasks, and telemetry) via P2P connections to prevent duplicate task assignments.
* **Collision Avoidance (Time-Space Reservation):** Bots broadcast their intended next coordinate. If two bots attempt to occupy the same space or swap spaces, a deterministic priority system forces the lower-priority bot to yield/wait for a clock cycle.
* **Autonomous Recharging:** Bots monitor their own telemetry. If battery drops below 20%, they automatically reject new task auctions, switch their state to `RETURNING_TO_CHARGE`, and pathfind to the nearest corner charging pad.
* **High-Performance Dashboard:** A React frontend using HTML5 `<canvas>` handles the 10,000-cell grid visualization at a buttery smooth 4 Hz tick rate via WebSockets.

## 🏗️ Architecture & Tech Stack

**Backend (The Swarm Engine)**
* **Python 3.11** - Core simulation physics, pathfinding, and auction logic.
* **FastAPI** - REST endpoints for task ingestion and WebSocket broadcasting.
* **Uvicorn** - ASGI web server.

**Frontend (The Control Center)**
* **React + Vite** - Lightning-fast UI rendering.
* **HTML5 Canvas API** - O(1) rendering complexity for the 100x100 warehouse grid.
* **Tailwind CSS v4** - Styling and layout.

## 📂 Project Structure

```text
warehouse-amr-swarm/
├── backend/                  
│   ├── main.py                 # FastAPI server & WebSocket broadcaster
│   ├── requirements.txt        
│   └── swarm_engine/
│       ├── environment.py      # 100x100 Grid, 10 Shelves, Dead Zones, Charging Pads
│       ├── pathfinding.py      # Manhattan-distance A* Navigation
│       ├── agent.py            # AMR State Machine (Battery, Telemetry, Intent)
│       ├── auction.py          # Contract Net Protocol Bidding Logic
│       └── mesh.py             # 15m P2P Radius & Gossip State Sync
│
└── frontend/                   
    ├── package.json
    ├── vite.config.js
    ├── src/
    │   ├── App.jsx             # Main layout & WebSocket listener
    │   ├── index.css
    │   └── components/
    │       ├── WarehouseGrid.jsx  # HTML5 Canvas 2D Grid
    │       ├── FleetStatus.jsx    # Live Telemetry Cards
    │       └── TaskManager.jsx    # CSV Upload & Manual Dispatch
    └── public/
        └── sample_orders.csv   # Test data

```

## ⚙️ Installation & Setup

### 1. Backend Setup

Requires Python 3.11+.

```bash
# Navigate to the backend directory
cd backend

# Create and activate the virtual environment
python -m venv swarm
# Windows: .\swarm\Scripts\activate
# Mac/Linux: source swarm/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the simulation engine
python -m uvicorn main:app --reload --port 8000

```

### 2. Frontend Setup

Requires Node.js 18+. Open a **new terminal window** while the backend is running.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev

```

## 🧪 Testing the Simulation

Once both servers are running, open `http://localhost:5173` in your browser.

1. **Test Autonomous Dispatching:** In the Task Dispatcher panel, input a coordinate (e.g., `X: 45`, `Y: 20`) and click `+`. Watch the "Mesh Gossip & Auctions" panel to see which bot wins the bid and tracks its A* path on the canvas.
2. **Test Dead Zones:** Dispatch a task to `X: 50`, `Y: 50`. The center of the map is a Wi-Fi dead zone (red tint). The bot will enter the zone, its status will drop, but it will continue working. It flushes its local logs back to the server once it exits.
3. **Test Swarm Behavior:** Click **Batch Upload CSV** and upload `sample_orders.csv`. All 4 bots will rapidly bid on tasks and scatter into the aisles.
4. **Test Collision Yielding:** Dispatch tasks that force two bots down the same narrow aisle from opposite directions. Watch one bot pause to let the other pass based on ID priority.

## 🛣️ Future Production Roadmap

To transition this prototype to physical hardware:

1. Wrap the Python `AMR` class inside a **ROS 2 Node** (`rclpy`).
2. Replace local memory buffers with **SQLite** on the edge (the bots) and **PostgreSQL** on the central server.
3. Swap Manhattan A* for a continuous-space local planner like **TEB Local Planner** to account for physical turning radii.

```

```