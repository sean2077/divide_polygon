"""
Author       : zhangxianbing
Date         : 2021-01-11 09:01:15
LastEditors  : zhangxianbing
LastEditTime : 2021-02-28 22:49:15
Description  : Divide polygon
"""

import copy
from math import atan2, cos, pi, sin, sqrt
from typing import List, Tuple


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f})"


_Segment = Tuple[Point, Point]
_Polygon = List[Point]


def _cross_point(p1: Point, p2: Point, x: float) -> Point:
    """Get the point on segment(p1p2) whose first-dimensional coordinate is x

    Args:
        p1 (Point): point1
        p2 (Point): point2
        x (float): first-dimensional coordinate

    Returns:
        Point: returned point
    """
    y = (p2.y - p1.y) / (p2.x - p1.x) * (x - p1.x) + p1.y
    return Point(x, y)


def _dividing_polygon_segs(p: _Polygon) -> List[_Segment]:
    """Get segments to divide polygon into multiple trapezoids.

    Args:
        p (_Polygon): convex polygon

    Returns:
        List[_Segment]: dividing segments
    """
    t, b = -1, 0
    rt = p[t]  # right top point
    rb = p[b]  # right bottom point
    lt = rt  # left top point
    lb = rb  # left bottom point
    segs = []
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
        segs.append((rb, rt))
        lt = rt
        lb = rb
    return segs


def _polygon_area(p: _Polygon) -> float:
    """Evaluate area of a polygon using shoelace formula.

    Args:
        p (_Polygon): convex polygon

    Returns:
        float: area of polygon
    """
    area = 0.0
    n = len(p)
    j = n - 1
    for i in range(0, n):
        area += (p[j].x + p[i].x) * (p[j].y - p[i].y)
        j = i

    return abs(area / 2.0)


def _trapezoid_area(left: _Segment, right: _Segment) -> float:
    """Evaluate area of a trapezoid.

    Args:
        left (_Segment): left segment (left_bottom, left_top) of the trapezoid
        right (_Segment): right segment (right_bottom, right_top) of the trapezoid

    Returns:
        float: area of trapezoid
    """
    a = left[1].y - left[0].y
    b = right[1].y - right[0].y
    h = right[0].x - left[0].x
    return (a + b) * h / 2.0


def _isclose(a, b, precision=1e-8):
    return abs(a - b) <= precision


def _sep_trapeziod(left: _Segment, right: _Segment, des_area: float) -> float:
    """Separate the left part of the specified area from the trapeziod.

    Args:
        left (_Segment): left segment (left_bottom, left_top) of the trapezoid
        right (_Segment): right segment (right_bottom, right_top) of the trapezoid
        des_area (float): desired area

    Returns:
        float: dividing point's first-dimensional coordinate `x`
    """
    a = left[1].y - left[0].y
    b = right[1].y - right[0].y
    h = right[0].x - left[0].x
    area = (a + b) * h / 2.0
    if _isclose(a, b):
        lmd = des_area / (area - des_area)
    else:
        c = sqrt(a ** 2 + (des_area / area) * (b ** 2 - a ** 2))

        lmd = (c - a) / (b - c)
    return (left[0].x + lmd * right[0].x) / (1 + lmd)


def _divide_polygon(p: _Polygon, n: int) -> List[_Segment]:
    """Divede polygon with lines parallel with its fisrt edge.

    Args:
        p (_Polygon): convex polygon counterclockwise, with the first edge(p[0]p[-1]) parallel with y axis.
        n (int): number of parts to divide polygon into.

    Returns:
        List[_Segment]: dividing segments
    """
    res = []
    segs = _dividing_polygon_segs(p)
    area = _polygon_area(p)
    des_area = area / n
    cur_area = 0.0
    left_seg = (p[0], p[-1])
    i = 0

    while i < len(segs) and len(res) < n - 1:
        right_seg = segs[i]
        trap_area = _trapezoid_area(left_seg, right_seg)
        delta_area = des_area - (trap_area + cur_area)

        if delta_area > 0.0:
            left_seg = right_seg
            cur_area += trap_area
            i += 1

        elif delta_area < 0.0:
            x = _sep_trapeziod(left_seg, right_seg, des_area - cur_area)
            bott = _cross_point(left_seg[0], right_seg[0], x)
            top = _cross_point(left_seg[1], right_seg[1], x)
            left_seg = (bott, top)
            res.append(left_seg)
            cur_area = 0.0

        else:
            left_seg = right_seg
            res.append(left_seg)
            cur_area = 0.0
            i += 1

    return res


def _rotate_coord(origin: List[Point], theta: float) -> None:
    """Rotate coordinate system by `theta`.

    Args:
        origin (List[Point]): coordinates to be translated.
        theta (float): the angle to rotate
    """
    sin_theta, cos_theta = sin(theta), cos(theta)
    for p in origin:
        px, py = p.x, p.y
        p.x = cos_theta * px + sin_theta * py
        p.y = -sin_theta * px + cos_theta * py


def divide_polygon(poly: _Polygon, n: int, idx: int, in_place=False) -> List[_Segment]:
    """Divede polygon with lines parallel with its idx-th edge.

    Args:
        poly (_Polygon): counterclockwise polygon with edge p[0]p[-1] on y axis.
        n (int): number of parts to divide polygon into.
        idx (int): index of edge to be paralleled with.
        in_place (bool, optional): whether to operate in place (If true, input data would be changed). Defaults to False.

    Returns:
        List[_Segment]: dividing segments
    """
    if not in_place:
        p = copy.deepcopy(poly)
    else:
        p = poly
    # rotate current coordinate system by theta(angle from sepc line to y axis)
    theta = atan2(p[idx - 1].y - p[idx].y, p[idx - 1].x - p[idx].x) - pi / 2.0
    _rotate_coord(p, theta)
    # change p[idx] to p[0]
    p = p[idx:] + p[:idx]

    lines = _divide_polygon(p, n)

    # convert to origin coord
    for line in lines:
        _rotate_coord(line, -theta)

    return lines


# for test
def _draw_polygon(p: _Polygon, lines=None, title="") -> None:
    import matplotlib.pyplot as plt

    coord = [(_p.x, _p.y) for _p in p]
    coord.append(coord[0])
    xs, ys = zip(*coord)
    plt.figure()
    plt.axis("square")
    plt.xlim(min(p, key=lambda p: p.x).x - 1, max(p, key=lambda p: p.x).x + 1)
    plt.ylim(min(p, key=lambda p: p.y).y - 1, max(p, key=lambda p: p.y).y + 1)
    plt.grid(color="r", linestyle="--", linewidth=1, alpha=0.3)
    plt.plot(xs, ys)
    if lines:
        for line in lines:
            plt.plot([p.x for p in line], [p.y for p in line])
    if title:
        plt.savefig(title)
    else:
        plt.show()


if __name__ == "__main__":
    import os

    # poly = [Point(3, 3), Point(8, 3), Point(8, 6), Point(3, 6)]
    # poly = [
    #     Point(-1, 0),
    #     Point(0.5, -1),
    #     Point(1.5, -1.5),
    #     Point(2.5, -1.5),
    #     Point(3.5, -1),
    #     Point(3.5, 3),
    #     Point(2.5, 3.5),
    #     Point(1, 3),
    #     Point(-0.5, 1),
    # ]
    poly = [
        Point(1, 6),
        Point(4, 2),
        Point(8, 3),
        Point(10, 5),
        Point(7, 9),
        Point(5, 9),
    ]

    # print(_sep_polygon_lines(p1))

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

    print(f"polygon: {poly}")
    for i in range(2, 6):
        lines = divide_polygon(poly, i, 2)
        print(f"when n={i}, result: {lines}")
        _draw_polygon(poly, lines, os.path.join("images", f"divide_{i}.png"))
