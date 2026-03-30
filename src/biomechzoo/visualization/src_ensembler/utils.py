def _get_condition_from_path(path, conditions):
    for cond in conditions:
        if cond in path:
            return cond
    return "Unknown"