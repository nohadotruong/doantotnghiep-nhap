def optimize_path(path, remove_redundant=False, remove_transitive=False):
    optimized = path
    if remove_redundant:
        optimized = remove_redundant_points(optimized)
    if remove_transitive:
        while True:
            new_optimized = remove_transitive_redundant_points(optimized)
            if len(new_optimized) == len(optimized):
                break
            optimized = new_optimized
    return optimized

def remove_redundant_points(path):
    if len(path) <= 2:
        return path
    optimized_path = [path[0]]
    i = 1
    while i < len(path) - 1:
        prev_point = optimized_path[-1]
        curr_point = path[i]
        next_point = path[i + 1]
        (x_prev, y_prev) = prev_point
        (x_curr, y_curr) = curr_point
        (x_next, y_next) = next_point
        dx_prev = x_curr - x_prev
        dy_prev = y_curr - y_prev
        dx_next = x_next - x_curr
        dy_next = y_next - y_curr
        if dx_prev == 0 and dx_next == 0:
            is_collinear = True
        elif dx_prev == 0 or dx_next == 0:
            is_collinear = False
        else:
            fr = dy_prev / dx_prev
            af = dy_next / dx_next
            is_collinear = abs(fr - af) < 1e-09
        if not is_collinear:
            optimized_path.append(curr_point)
        i += 1
    optimized_path.append(path[-1])
    return optimized_path

def remove_transitive_redundant_points(path):
    return path
