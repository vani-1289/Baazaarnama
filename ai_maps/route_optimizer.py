from collections import deque

def get_shortest_path(start_x, start_y, end_x, end_y, shop_positions=None):
    """
    Computes shortest walking path from (start_x, start_y) to (end_x, end_y) on a 10x10 grid.
    Walkways are at rows and columns 3 and 7.
    Shops (stalls) act as obstacles unless they are the start or destination.
    Returns list of coordinate tuples [(x1,y1), (x2,y2), ...] forming the path.
    """
    grid_size = 10
    walkways_x = {3, 7}
    walkways_y = {3, 7}

    # If shop_positions is provided, block coordinates of other shops
    obstacles = set()
    if shop_positions:
        for s_id, pos in shop_positions.items():
            pos_tuple = (pos['x'], pos['y'])
            if pos_tuple != (start_x, start_y) and pos_tuple != (end_x, end_y):
                obstacles.add(pos_tuple)

    # Walkway cells + start + end are walkable
    def is_walkable(x, y):
        if not (1 <= x <= grid_size and 1 <= y <= grid_size):
            return False
        if (x, y) == (start_x, start_y) or (x, y) == (end_x, end_y):
            return True
        if (x, y) in obstacles:
            return False
        # To make routing easier, let's say walkways are fully walkable, and grid boundary borders are walkable
        if x in walkways_x or y in walkways_y or x in {1, grid_size} or y in {1, grid_size}:
            return True
        # If it's a shop area and not an obstacle, allow it but with higher routing weight (not in simple BFS, BFS treats all as equal)
        # So we just allow walkway routing
        return False

    queue = deque([[(start_x, start_y)]])
    visited = {(start_x, start_y)}

    while queue:
        path = queue.popleft()
        cx, cy = path[-1]

        if (cx, cy) == (end_x, end_y):
            return path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if is_walkable(nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(path + [(nx, ny)])

    # Fallback to direct coordinate interpolation if blocked
    path = []
    curr_x, curr_y = start_x, start_y
    path.append((curr_x, curr_y))
    while (curr_x, curr_y) != (end_x, end_y):
        if curr_x < end_x:
            curr_x += 1
        elif curr_x > end_x:
            curr_x -= 1
        elif curr_y < end_y:
            curr_y += 1
        elif curr_y > end_y:
            curr_y -= 1
        path.append((curr_x, curr_y))
    return path
