from map.grid_map import GridMap


class MapValidator:
    @staticmethod
    def validate(grid_map: GridMap) -> tuple[bool, str]:
        if grid_map.start is None:
            return False, "Need Start"
        if grid_map.goal is None:
            return False, "Need Goal"
        start_x, start_y = grid_map.start
        goal_x, goal_y = grid_map.goal
        if grid_map.is_obstacle(start_x, start_y):
            return False, "Start is obstacle"
        if grid_map.is_obstacle(goal_x, goal_y):
            return False, "Goal is obstacle"
        return True, "OK"
