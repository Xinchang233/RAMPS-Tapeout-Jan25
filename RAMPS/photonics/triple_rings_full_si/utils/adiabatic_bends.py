import numpy as np

def compute_arc_length(arc_list):
    arc_length = 0
    for arc in arc_list:
        x = arc['x']
        y = arc['y']
        pts = np.array(list(zip(x, y)))
        arc_length += np.sum(np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1)))
    return float(arc_length)

def get_arc_height(arc_list):
    arc_max = -1e6
    arc_min = 1e6
    for arc in arc_list:
        y = arc['y']
        MAX = max(y)
        MIN = min(y)

        if MAX > arc_max:
            arc_max = MAX

        if MIN < arc_min:
            arc_min = MIN

    return float(arc_max - arc_min)

def get_arc_length(arc_list):
    arc_max = -1e6
    arc_min = 1e6
    for arc in arc_list:
        x = arc['x']
        MAX = max(x)
        MIN = min(x)

        if MAX > arc_max:
            arc_max = MAX

        if MIN < arc_min:
            arc_min = MIN

    return float(arc_max - arc_min)