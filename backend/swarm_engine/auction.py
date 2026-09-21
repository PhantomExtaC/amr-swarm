from swarm_engine.pathfinding import a_star_search

def run_decentralized_auction(task, bots, warehouse):
    """
    Broadcasts a task to all bots. The bot with the lowest bid wins,
    calculates its path, and marks the task as claimed.
    """
    task_id = task['id']
    task_pos = (task['x'], task['y'])

    best_bid = float('inf')
    winner = None

    for bot in bots:
        bid = bot.calculate_bid(task_pos, task_id)
        if bid < best_bid:
            best_bid = bid
            winner = bot
        # Tie-breaker logic (lowest ID string wins)
        elif bid == best_bid and bid != float('inf'):
            if winner and bot.id < winner.id:
                winner = bot

    if winner:
        winner.current_task = task
        winner.claimed_tasks.add(task_id)
        
        # Calculate A* path to the target
        winner.path = a_star_search(warehouse, winner.pos, task_pos)
        if winner.path:
            winner.state = "MOVING"
            return winner.id
            
    return None  # No bot could take the task