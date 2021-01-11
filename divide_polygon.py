"""
Author       : zhangxianbing
Date         : 2021-01-11 09:01:15
LastEditors  : zhangxianbing
LastEditTime : 2021-01-11 16:56:38
Description  : Divide polygon
"""

import copy
from math import atan2, cos, pi, sin, sqrt
from typing import List


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f})"


def _cross_point(p1: Point, p2: Point, x):
    y = (p2.y - p1.y) / (p2.x - p1.x) * (x - p1.x) + p1.y
    return Point(x, y)


def _sep_polygon_lines(p: List[Point]):
    t, b = -1, 0
    rt = p[t]  # right top point
    rb = p[b]  # right bottom point
    lt = rt  # left top point
    lb = rb  # left bottom point
    lines = []
    while True:
        if p[t - 1].x < p[b + 1].x:
            rt = p[t - 1]
            rb = _cross_point(lb, p[b + 1], p[t - 1].x)
            t = t - 1
        elif p[t - 1].x > p[b + 1].x:
            rt = _cross_point(lt, p[t - 1], p[b + 1].x)
            rb = p[b + 1]
            b = b + 1
        else:
            rt = p[t - 1]
            rb = p[b + 1]
            t = t - 1
            b = b + 1
        if rt.y < rb.y:
            break
        lines.append(((rb, rt)))
        lt = rt
        lb = rb
    return lines


def _eval_polygon_area(p: List[Point]):
    """evaluate area of a polygon using shoelace formula."""
    area = 0.0
    n = len(p)
    j = n - 1
    for i in range(0, n):
        area += (p[j].x + p[i].x) * (p[j].y - p[i].y)
        j = i

    return abs(area / 2.0)


def _eval_trapezoid_area(l1: List[Point], l2: List[Point]):
    a = l1[1].y - l1[0].y
    b = l2[1].y - l2[0].y
    h = l2[0].x - l1[0].x
    return (a + b) * h / 2.0


def _sep_trapeziod_area(l1: List[Point], l2: List[Point], A):
    a = l1[1].y - l1[0].y
    b = l2[1].y - l2[0].y
    h = l2[0].x - l1[0].x
    S = (a + b) * h / 2.0
    if a == b:
        lmd = A / (S - A)
    else:
        c = sqrt(a ** 2 + (A / S) * (b ** 2 - a ** 2))
        lmd = (c - a) / (b - c)
    return (l1[0].x + lmd * l2[0].x) / (1 + lmd)


def _divide_polygon(p: List[Point], n: int, tolerance=1e-12):
    """Divede polygon with parallel lines

    Args:
        p (List[Point]): counterclockwise polygon with edge p[0]p[-1] on y axis.
        n (int): divisor
        tolerance (float, optional): tolerance, expressed as polygon area percentage. Defaults to 1e-12.

    Returns:
        [type]: [description]
    """
    res = []
    sep_lines = _sep_polygon_lines(p)
    area = _eval_polygon_area(p)
    tol_area = area * tolerance
    des_area = area / n
    cur_area = 0.0
    left_line = (p[0], p[-1])
    i = 0

    while i < len(sep_lines) and len(res) < n - 1:
        right_line = sep_lines[i]
        trap_area = _eval_trapezoid_area(left_line, right_line)
        delta_area = des_area - (trap_area + cur_area)

        if delta_area > tol_area:
            left_line = right_line
            cur_area += trap_area
            i += 1

        elif delta_area < tol_area:
            x = _sep_trapeziod_area(left_line, right_line, des_area - cur_area)
            bott = _cross_point(left_line[0], right_line[0], x)
            top = _cross_point(left_line[1], right_line[1], x)
            left_line = (bott, top)
            res.append(left_line)
            cur_area = 0.0

        elif abs(delta_area) <= tol_area:
            left_line = right_line
            res.append(left_line)
            cur_area = 0.0
            i += 1

    return res


def _translate_coord(origin: List[Point], trans: Point):
    for i in range(len(origin)):
        origin[i].x += trans.x
        origin[i].y += trans.y


def _rotate_coord(origin: List[Point], theta: float):
    sin_theta, cos_theta = sin(theta), cos(theta)
    for i in range(len(origin)):
        px, py = origin[i].x, origin[i].y
        origin[i].x = cos_theta * px + sin_theta * py
        origin[i].y = -sin_theta * px + cos_theta * py


def divide_polygon(poly: List[Point], n: int, idx: int, tolerance=1e-12, in_place=True):
    """Divede polygon with parallel lines

    Args:
        poly (List[Point]): counterclockwise polygon with edge p[0]p[-1] on y axis.
        n (int): divisor
        idx (int): edge (p[idx-1]p[idx]) sepcified to parallel with.
        tolerance (float, optional): tolerance, expressed as polygon area percentage. Defaults to 1e-12.
        in_place (bool, optional): whether to operate in place.

    Returns:
        [type]: [description]
    """
    if in_place:
        p = copy.deepcopy(poly)
    else:
        p = poly
    # tanslate current coordinate system by by -p[idx]
    trans = Point(-p[idx].x, -p[idx].y)
    _translate_coord(p, trans)
    # rotate current coordinate system by theta and tanslate by -p[idx]
    # angle from sepc line to y axis
    theta = atan2(p[idx - 1].y - p[idx].y, p[idx - 1].x - p[idx].x) - pi / 2.0
    _rotate_coord(p, theta)
    # change p[idx] to p[0]
    p = p[idx:] + p[:idx]

    lines = _divide_polygon(p, n, tolerance)

    # convert to origin coord
    trans = Point(-trans.x, -trans.y)
    for i in range(len(lines)):
        _rotate_coord(lines[i], -theta)
        _translate_coord(lines[i], trans)

    return lines


# for test
def _draw_polygon(p: List[Point], lines=None):
    import matplotlib.pyplot as plt

    coord = [(_p.x, _p.y) for _p in p]
    coord.append(coord[0])
    xs, ys = zip(*coord)
    plt.figure()
    plt.axis("square")
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.grid(color="r", linestyle="--", linewidth=1, alpha=0.3)
    plt.plot(xs, ys)
    if lines:
        for line in lines:
            plt.plot([p.x for p in line], [p.y for p in line])
    plt.show()


if __name__ == "__main__":
    p1 = [
        Point(0, 0),
        Point(0.5, -1),
        Point(1.5, -1.5),
        Point(2.5, -1.5),
        Point(3.5, -1),
        Point(3.5, 3),
        Point(2.5, 3.5),
        Point(1, 3),
        Point(0, 1),
    ]
    # print(_sep_polygon_lines(polygon))

    # print(_eval_polygon_area([Point(0, 1), Point(2, 3), Point(4, 7)]))

    # print(
    #     _sep_trapeziod_area(
    #         [Point(0.0, 0.0), Point(0.0, 1.0)],
    #         [Point(1.0, 0.00), Point(1.0, 1.00)],
    #         0.5,
    #     )
    # )
    # for i in range(2, 10):
    #     print(_divide_polygon(p1, i))

    # _draw_polygon(p1)
    lines = divide_polygon(p1, 4, 1)
    print(p1)
    _draw_polygon(p1, lines)
