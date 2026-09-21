import time
from swarm_engine.pathfinding import a_star_search, manhattan_distance

class AMR:
    def __init__(self, bot_id: str, start_pos: tuple[int, int]):
        self.id = bot_id
        self.pos = start_pos
        self.battery = 100.0
        self.state = "IDLE"  # IDLE, MOVING, CHARGING, RETURNING_TO_CHARGE, OFFLINE
        
        self.current_task = None
        self.path = []
        
        self.local_log_buffer = []
        self.claimed_tasks = set()
        self.completed_tasks = set()

    def calculate_bid(self, task_pos: tuple[int, int], task_id: str) -> float:
        if self.state != "IDLE" or self.battery < 20 or task_id in self.claimed_tasks or task_id in self.completed_tasks:
            return float('inf')

        distance = manhattan_distance(self.pos, task_pos)
        battery_penalty = (100 - self.battery) * 0.5 
        return distance + battery_penalty

    def get_intent(self) -> tuple[int, int]:
        """Returns the coordinate the bot wants to move to next."""
        if self.state in ["MOVING", "RETURNING_TO_CHARGE"] and self.path:
            return self.path[0]
        return self.pos

    def tick(self, warehouse, approved_next_pos: tuple[int, int] | None = None):
        if self.state == "OFFLINE":
            return self._generate_telemetry(warehouse)

        # --- AUTONOMOUS RECHARGING LOGIC ---
        if self.state == "IDLE" and self.battery < 20.0:
            self.state = "RETURNING_TO_CHARGE"
            # Pathfind to the mathematically closest charging pad
            best_station = min(warehouse.charging_stations, key=lambda c: manhattan_distance(self.pos, c))
            self.path = a_star_search(warehouse, self.pos, best_station)
        
        if self.state == "CHARGING":
            self.battery = min(100.0, self.battery + 2.5) # Fast charge rate
            if self.battery == 100.0:
                self.state = "IDLE"
        else:
            # Drain battery normally
            drain = 0.05 if self.state in ["MOVING", "RETURNING_TO_CHARGE"] else 0.01
            self.battery = max(0.0, self.battery - drain)

        if self.battery == 0:
            self.state = "OFFLINE"
            return self._generate_telemetry(warehouse)

        # --- COLLISION-AWARE MOVEMENT ---
        if self.state in ["MOVING", "RETURNING_TO_CHARGE"] and self.path:
            intended = self.path[0]
            # Only step forward if the P2P Mesh approved the move
            if approved_next_pos == intended:
                self.pos = self.path.pop(0)
                
                if not self.path:
                    if self.state == "RETURNING_TO_CHARGE":
                        self.state = "CHARGING"
                    elif self.state == "MOVING":
                        self.state = "IDLE"
                        if self.current_task:
                            self.completed_tasks.add(self.current_task['id'])
                            self.current_task = None
            else:
                pass # YIELDING: Path is blocked, bot waits in place this tick

        return self._generate_telemetry(warehouse)

    def _generate_telemetry(self, warehouse):
        telemetry = {
            "id": self.id,
            "pos": self.pos,
            "battery": round(self.battery, 1),
            "state": self.state,
            "timestamp": time.time()
        }

        if warehouse.is_dead_zone(self.pos[0], self.pos[1]):
            self.local_log_buffer.append(telemetry)
        else:
            if self.local_log_buffer:
                self.local_log_buffer.clear()
        
        return telemetry