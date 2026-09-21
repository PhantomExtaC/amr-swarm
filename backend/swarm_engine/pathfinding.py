import heapq

def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(warehouse, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Calculates the shortest path avoiding shelf obstacles.
    Returns a list of (x, y) coordinate tuples from start to goal.
    """
    if not warehouse.is_valid(start[0], start[1]) or not warehouse.is_valid(goal[0], goal[1]):
        return []

    if start == goal:
        return [start]

    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}

    # 4-Directional movement (Up, Down, Left, Right)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if not warehouse.is_valid(neighbor[0], neighbor[1]):
                continue

            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Path not found