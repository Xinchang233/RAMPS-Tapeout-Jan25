import numpy as np


def compute_arc_length2( arc_list):
    arc_length = 0
    for arc in arc_list:
        x = arc['x']
        y = arc['y']
        pts = np.array(list(zip(x, y)))
        arc_length += np.sum(np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1)))
        y1=np.sum(y)
    return x[-1],y[-1]