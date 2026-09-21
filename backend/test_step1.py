from swarm_engine.environment import WarehouseMap
from swarm_engine.pathfinding import a_star_search

warehouse = WarehouseMap(100, 100)

# Start at Dock (0,0) and target a position behind shelf row 1 at (15, 12)
start = (0, 0)
goal = (15, 12)

path = a_star_search(warehouse, start, goal)

print(f"Warehouse obstacles initialized: {len(warehouse.obstacles)} cells")
print(f"Dead zone cells initialized: {len(warehouse.dead_zones)} cells")
print(f"Path calculated from {start} to {goal}: {len(path)} steps")
print(f"First 5 steps: {path[:5]}")
print(f"Last 5 steps: {path[-5:]}")