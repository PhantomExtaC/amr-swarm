from swarm_engine.pathfinding import manhattan_distance

class MeshNetwork:
    def __init__(self, radio_range=15):
        self.radio_range = radio_range

    def gossip_sync(self, bots: list):
        """
        O(N^2) comparison of all bots. If two bots are within radio_range,
        they merge their claimed and completed task sets.
        """
        n = len(bots)
        for i in range(n):
            for j in range(i + 1, n):
                bot_a = bots[i]
                bot_b = bots[j]

                # Check physical distance
                if manhattan_distance(bot_a.pos, bot_b.pos) <= self.radio_range:
                    # Sync Claimed Tasks
                    merged_claims = bot_a.claimed_tasks.union(bot_b.claimed_tasks)
                    bot_a.claimed_tasks = merged_claims
                    bot_b.claimed_tasks = merged_claims

                    # Sync Completed Tasks
                    merged_completed = bot_a.completed_tasks.union(bot_b.completed_tasks)
                    bot_a.completed_tasks = merged_completed
                    bot_b.completed_tasks = merged_completed